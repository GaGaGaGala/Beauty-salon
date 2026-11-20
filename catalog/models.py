from django.db import models
from django.contrib.auth.models import User
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_pic: ImageField = models.ImageField(null=True, blank=True, upload_to="images/profile/")
    vk = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=30, blank=True, default="")
    district = models.CharField(max_length=100, blank=True, default="")
    comment = models.TextField(blank=True, default="")
    patronymic = models.CharField(max_length=100, blank=True, default="")


    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        profile = Profile.objects.get(user=instance)
    except Profile.DoesNotExist:
        return
    profile.save()


class Client(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ServiceCategory(models.TextChoices):
    MANICURE = "manicure", "Маникюр"
    PEDICURE = "pedicure", "Педикюр"
    BROWS = "brows", "Брови"
    HAIR = "hair", "Парикмахерские услуги"


class Service(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    category = models.CharField(max_length=20, choices=ServiceCategory.choices, default=ServiceCategory.MANICURE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    clients = models.ManyToManyField(Client, related_name="services", blank=True)

    def __str__(self):
        return f"{self.title} — {self.price} руб."

    class Meta:
        ordering = ["category", "title"]

class BookingStatus(models.TextChoices):
    PENDING = "pending", "Ожидает подтверждения"
    PROPOSED = "proposed", "Предложено другое время"
    CONFIRMED = "confirmed", "Подтверждена"
    REJECTED = "rejected", "Отклонена"
    CANCELLED = "cancelled", "Отменена"
    COMPLETED = "completed", "Выполнена"


class Booking(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    desired_datetime = models.DateTimeField(verbose_name="Желаемая дата и время")
    confirmed_start = models.DateTimeField(null=True, blank=True, verbose_name="Согласованное время начала")
    confirmed_end = models.DateTimeField(null=True, blank=True, verbose_name="Согласованное время окончания")
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    duration_minutes = models.PositiveIntegerField(default=60)
    travel_time_minutes = models.PositiveIntegerField(default=0)
    client_district = models.CharField(max_length=100, blank=True, default="")
    client_comment = models.TextField(blank=True, default="")
    master_note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Booking #{self.id} {self.client.username} - {self.service.title}"

    @property
    def interval_start(self):
        return self.confirmed_start or self.desired_datetime

    @property
    def interval_end(self):
        if self.confirmed_end:
            return self.confirmed_end
        return self.interval_start + timezone.timedelta(minutes=self.duration_minutes)


class DayOfWeek(models.IntegerChoices):
    MONDAY = 0, "Понедельник"
    TUESDAY = 1, "Вторник"
    WEDNESDAY = 2, "Среда"
    THURSDAY = 3, "Четверг"
    FRIDAY = 4, "Пятница"
    SATURDAY = 5, "Суббота"
    SUNDAY = 6, "Воскресенье"


class WorkingSchedule(models.Model):
    day_of_week = models.IntegerField(choices=DayOfWeek.choices, unique=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    is_working = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week"]

    def __str__(self):
        if self.is_working:
            return f"{self.get_day_of_week_display()}: {self.start_time}-{self.end_time}"
        return f"{self.get_day_of_week_display()}: выходной"


class ScheduleException(models.Model):
    date = models.DateField(unique=True)
    is_working = models.BooleanField(default=False)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.date}: {'работа' if self.is_working else 'выходной'}"


class CalendarSettings(models.Model):
    """Singleton settings for master calendar (dispatch duty cycle, etc.)."""
    dispatch_cycle_start = models.DateField(null=True, blank=True, help_text="Дата первой смены в диспетчерской (закрытый день)")
    dispatch_cycle_length = models.PositiveIntegerField(default=4, help_text="Длина цикла смен (дней)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Настройки календаря"
        verbose_name_plural = "Настройки календаря"

    def __str__(self):
        return f"Настройки календаря (старт: {self.dispatch_cycle_start})"


class RecurringBusy(models.Model):
    WEEKDAYS = [(i, d) for i, d in enumerate(["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"])]
    weekday = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    buffer_before_minutes = models.PositiveIntegerField(default=0, help_text="Время до занятия (дорога/сборы)")
    buffer_after_minutes = models.PositiveIntegerField(default=0, help_text="Время после занятия (дорога/сборы)")
    active_from = models.DateField(default=timezone.now().date() if False else None, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    comment = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Повторяющаяся занятость"
        verbose_name_plural = "Повторяющаяся занятость"
        ordering = ["weekday", "start_time"]

    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time}-{self.end_time}"
class DayPlan(models.Model):
    date = models.DateField(unique=True)
    start_time = models.TimeField(null=True, blank=True)
    start_location = models.CharField(max_length=100, blank=True, default="")
    note = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"План на {self.date}"


class PersonalEventType(models.TextChoices):
    PERSONAL = "personal", "Личное дело"
    TRAINING = "training", "Тренировка"
    DAY_OFF = "day_off", "Выходной"
    VACATION = "vacation", "Отпуск"
    TRIP = "trip", "Поездка"
    OTHER = "other", "Другое"


class PersonalEvent(models.Model):
    title = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=PersonalEventType.choices, default=PersonalEventType.PERSONAL)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    comment = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["start_datetime"]

    def __str__(self):
        return f"{self.title} ({self.start_datetime})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_datetime <= self.start_datetime:
            raise ValidationError("Окончание должно быть позже начала.")


class Review(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PUBLISHED = 'published'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'На модерации'),
        (STATUS_PUBLISHED, 'Опубликован'),
        (STATUS_REJECTED, 'Отклонён'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    booking = models.OneToOneField('Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name="review")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True, default="")
    photo = models.ImageField(null=True, blank=True, upload_to="reviews/")
    is_published = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    likes = models.ManyToManyField(User, related_name="liked_reviews", blank=True)
    dislikes = models.ManyToManyField(User, related_name="disliked_reviews", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Review by {self.client.username}: {self.rating}"

    def save(self, *args, **kwargs):
        # Keep legacy boolean flags in sync with status.
        self.is_published = (self.status == self.STATUS_PUBLISHED)
        self.rejected = (self.status == self.STATUS_REJECTED)
        super().save(*args, **kwargs)


class PortfolioCategory(models.TextChoices):
    MANICURE = "manicure", "Маникюр"
    PEDICURE = "pedicure", "Педикюр"
    BROWS = "brows", "Брови"
    HAIR = "hair", "Парикмахерские услуги"
    OTHER = "other", "Другое"


class PortfolioImage(models.Model):
    image = models.ImageField(upload_to="portfolio/")
    title = models.CharField(max_length=255, blank=True, default="")
    category = models.CharField(max_length=20, choices=PortfolioCategory.choices, default=PortfolioCategory.OTHER)
    description = models.TextField(blank=True, default="")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Portfolio #{self.id}"


class PortfolioImageReaction(models.Model):
    REACTION_LIKE = 'like'
    REACTION_DISLIKE = 'dislike'
    REACTION_CHOICES = [
        (REACTION_LIKE, 'Нравится'),
        (REACTION_DISLIKE, 'Не нравится'),
    ]

    image = models.ForeignKey(PortfolioImage, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolio_reactions')
    reaction = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['image', 'user'], name='unique_portfolio_image_reaction'),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.reaction} on PortfolioImage #{self.image_id}"
class Image(models.Model):
    id = models.IntegerField(primary_key=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True, verbose_name='images')
    def im(self):
        return self.image

class Comment(models.Model):
    services = models.ForeignKey(Service, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(Client, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='media/images', null=True, blank=True, verbose_name='images')

    def __str__(self):
        return f'Comment by {self.author} on {self.services}'
