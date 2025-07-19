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


class Client(models.Model):
    name = models.CharField(max_length=100)

    def _str_(self):
        return self.name


class Service(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    clients = models.ManyToManyField(Client, related_name='services', blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # photo = models.ImageField(upload_to='media/images', null=True, blank=True, verbose_name='images')
    # likes = models.ManyToManyField(User, related_name='likes', blank=True)
    # dislikes = models.ManyToManyField(User, related_name='dislikes', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return '{} {} {} {}'.format(self.title, self.content, self.client, self.price)

    # def number_of_likes(self):
    #     return self.likes.count()
    #
    # def number_of_dislikes(self):
    #     return self.dislikes.count()

class Image(models.Model):
    id = models.IntegerField(primary_key=True)
    image = models.ImageField(upload_to='images/', blank=True, verbose_name='images')
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