from django import forms
from .models import Service, Profile, Comment
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'content', 'clients', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'clients': forms.Textarea(attrs={'class': 'form-control'}),
            'price': forms.DecimalField(max_digits=5, decimal_places=2),
        }

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2',)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date', 'profile_pic', 'vk', 'instagram')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('services', 'author', 'content', 'photo')