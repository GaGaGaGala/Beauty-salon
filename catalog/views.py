from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from .models import Service, Profile
from .forms import ServiceForm, ProfileForm, UserForm, SignUpForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django. contrib import messages


def base(request):
    """Представление для базового шаблона."""
    return render(request, 'base.html')

def home(request):
    """Представление для шаблона главной страницы."""
    return render(request, 'home.html')

def signup(request):
    """Представление для регистрации."""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/catalog')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def free_window(request):
    """Для записи, свободное окно."""
    if request.method == "POST":
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.client = request.user
            form.save()
            img_obj = form.instance
            return redirect('catalog:list_of_service')
    else:
        form = ServiceForm()
    return render(request, 'catalog/free_window.html', {'form': form})

# def for_procedure(request):
#     """Представление для записи на процедуру."""
#     service = Service.objects.get()
#     context = {
#         'service': service,
#     }
#     return render(request, 'catalog/for_procedure.html', context=context)

def list_of_services(request):
    """Все услуги."""
    service = ["Маникюр", "Педикюр", "Брови", "Парикмахерские услуги"]
    context = {
        'service': service,
    }
    return render(request, "catalog/list_of_services.html", context=context)

def list_detail(request):
    return render(request, "catalog/list_detail.html")


def logout_view(request):
    """Выход из системы."""
    logout(request)
    return redirect('home')


@login_required
@transaction.atomic
def update_profile(request):
    """ Создание профиля пользователем."""
    Profile.objects.all()
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, ('Ваш профиль был успешно обновлен!'))
            return redirect('board:profile')
        else:
            messages.error(request, ('Пожалуйста, исправьте ошибки.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'catalog/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def price_list(request):
    return render(request, "catalog/price_list.html")

def portfolio(request):
    return render(request, "catalog/portfolio.html")

