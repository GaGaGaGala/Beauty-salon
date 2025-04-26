from django.db import models
from django.contrib.auth.models import User
from django.db.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_pic: ImageField = models.ImageField(null=True, blank=True, upload_to="images/profile/")
    vk = models.CharField(max_length=50, null=True, blank=True)
    instagram = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Service(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='media/images', null=True, blank=True, verbose_name='Image')
    likes = models.ManyToManyField(User, related_name='Likes', blank=True)
    dislikes = models.ManyToManyField(User, related_name='Dislikes', blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return '{} {} {} {} {}'.format(self.title, self.client, self.photo, self.likes, self.dislikes)

    def number_of_likes(self):
        return self.likes.count()

    def number_of_dislikes(self):
        return self.dislikes.count()
