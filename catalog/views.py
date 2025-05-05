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
    ser1 = "Маникюр"
    ser2 = "Педикюр"
    ser3 = "Брови"
    ser4 = "Парикмахерские услуги"
    context = {
        'ser1': ser1,
        'ser2': ser2,
        'ser3': ser3,
        'ser4': ser4,
    }
    return render(request, "catalog/price_list.html", context=context)

def portfolio(request):
    return render(request, "catalog/portfolio.html")

def price_manicure(request):
    title = [
        "Маникюр классический без покрытия ********************************* 800",
        "Маникюр классический с покрытием (лак) **************************** 900",
        "Маникюр + наращивание (гель) + покрытие в один тон ************ 2500",
        "Коррекция ногтей (гель) *********************************************** 2000",
        "Дизайн одного ногтя **************************************************** 100",
        "Френч ******************************************************************** 300",
        "Амбре ******************************************************************** 500",
        "Маникюр + покрытие (гель-лак) в один тон ************************** 1700",
        "Коррекция ногтей (гель-лак) ******************************************* 1800",
        "Ремонт ногтя ************************************************************* 200",
        "Снятие покрытия ********************************************************* 200",
        "Снятие нарощенных ногтей ********************************************* 400"
        ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_manicure.html", context=context)

def price_pedicure(request):
    title = [
        "Педикюр классический полный без покрытия ************** 1700",
        "Педикюр комплексный с покрытием (гель-лак) ************* 2300",
        "Педикюр комплексный с покрытием (лак) ****************** 1800",
        "Педикюр (пальчики) с покрытием (гель-лак) *************** 1700"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_pedicure.html", context=context)

def price_eyebrows(request):
    title = [
        "Окрашивание бровей *********************************** 200",
        "Окрашивание ресниц *********************************** 200",
        "Коррекция бровей ************************************* 200"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_eyebrows.html", context=context)

def price_hair(request):
    title = [
        "Стрижка *********************************************** 800",
        "Окрашивание в один тон ******************************* 1500",
        "Мелирование ****************************************** 2500",
        "Тонирование ****************************************** 1500",
        "Колорирование **************************************** 2500",
        "Сложное окрашивание ********************************** 3500",
        "Химическая завивка *********************************** 2500",
        "Укладка феном ***************************************** 500",
        "Укладка вечерняя ************************************* 1500",
        "Причёска вечерняя ************************************ 2000",
        "Причёска свадебная *********************************** 4000"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_hair.html", context=context)

