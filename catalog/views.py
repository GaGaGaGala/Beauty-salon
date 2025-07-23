from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from .models import Service, Profile, Image
from .forms import ServiceForm, ProfileForm, UserForm, SignUpForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django. contrib import messages
from django.core.paginator import Paginator

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

    return render(request, 'catalog/free_window.html')

def list_of_services(request):
    """Все услуги."""
    service = ["Маникюр", "Педикюр", "Брови", "Парикмахерские услуги"]
    context = {
        "service": service,
    }
    return render(request, "catalog/list_of_services.html", context)

def list_detail_manic(request):
    return render(request, "catalog/detail/manic.html")

def detail_pedic(request):
    return render(request, "catalog/detail/pedic.html")

def detail_brows(request):
    return render(request, "catalog/detail/brows.html")

def detail_hair(request):
    service = ["Стрижки женские и мужские", "Все виды окрашивания",
               "Все виды химических завивок", "Причёски свадебные, торжественные",
               "Укладки"]
    context = {
        "service": service,
    }
    return render(request, "catalog/detail/hair.html", context)

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

def about_me(request):
    return render(request, "catalog/about.html")

def port_im(request):
    images = Image.objects.get_queryset().order_by('id')
    images_hair = ['/static/img/portfolio/hair/1745742172764.jpg', '/static/img/portfolio/hair/1745742172783.jpg',
            '/static/img/portfolio/hair/IMG-20231010-WA0037.jpg', '/static/img/portfolio/hair/IMG-20231010-WA0038.jpg',
            '/static/img/portfolio/hair/IMG-20231010-WA0039.jpg', '/static/img/portfolio/hair/IMG_20230115_101619.jpg',
            '/static/img/portfolio/hair/IMG_20230115_101711.jpg', '/static/img/portfolio/hair/IMG_20230708_102916.jpg',
            '/static/img/portfolio/hair/Screenshot_20220311-215551.png', '/static/img/portfolio/hair/Screenshot_20220311-215558.png',
            '/static/img/portfolio/hair/Screenshot_20220311-220117.png', '/static/img/portfolio/hair/Screenshot_20220311-220121.png',
            '/static/img/portfolio/hair/Screenshot_20220311-220117.png', '/static/img/portfolio/hair/Screenshot_20220311-222508.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221307.png', '/static/img/portfolio/hair/Screenshot_20220311-221503.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221509.png', '/static/img/portfolio/hair/Screenshot_20220311-221514.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221523.png', '/static/img/portfolio/hair/Screenshot_20220311-221532.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221603.png', '/static/img/portfolio/hair/Screenshot_20220311-221606.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221618.png', '/static/img/portfolio/hair/Screenshot_20220311-221622.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221630.png', '/static/img/portfolio/hair/Screenshot_20220311-221634.png',
            '/static/img/portfolio/hair/Screenshot_20220311-221638.png', '/static/img/portfolio/hair/Screenshot_20220311-222433.png',
            '/static/img/portfolio/hair/Screenshot_20220311-222453.png',
            ]

    images_manic = ['/static/img/portfolio/manic/2023-01-21_22-49-55_159.jpg', '/static/img/portfolio/manic/1706216487561.jpg',
             '/static/img/portfolio/manic/1706595312540.jpg', '/static/img/portfolio/manic/1709230633583.jpg',
             '/static/img/portfolio/manic/1709230633591.jpg', '/static/img/portfolio/manic/1709720317750.jpg',
             '/static/img/portfolio/manic/1711378773111.jpg', '/static/img/portfolio/manic/1712383229595_1.jpg',
             '/static/img/portfolio/manic/1714198071741.jpg', '/static/img/portfolio/manic/1715243861910.jpg',
             '/static/img/portfolio/manic/1715325700602.jpg', '/static/img/portfolio/manic/1735904513845.jpg',
             '/static/img/portfolio/manic/1717048802093.jpg', '/static/img/portfolio/manic/1735904513881.jpg',
             '/static/img/portfolio/manic/1735904583881.jpg', '/static/img/portfolio/manic/1735904583890.jpg',
             '/static/img/portfolio/manic/1738722944907.jpg', '/static/img/portfolio/manic/1738723020347.jpg',
             '/static/img/portfolio/manic/1745742110413.jpg', '/static/img/portfolio/manic/1745742172822.jpg',
             '/static/img/portfolio/manic/IMG-20220521-WA0019.jpg', '/static/img/portfolio/manic/IMG-20220807-WA0017.jpg',
             '/static/img/portfolio/manic/IMG-20230326-WA0001.jpg', '/static/img/portfolio/manic/IMG-20230427-WA0031.jpg',
             '/static/img/portfolio/manic/IMG-20230531-WA0052.jpg', '/static/img/portfolio/manic/IMG-20230626-WA0038.jpg',
             '/static/img/portfolio/manic/IMG-20230928-WA0016.jpg', '/static/img/portfolio/manic/IMG-20231024-WA0024.jpg',
             '/static/img/portfolio/manic/IMG-20231230-WA0046.jpg', '/static/img/portfolio/manic/IMG_20220306_021134.jpg',
             '/static/img/portfolio/manic/IMG_20220523_184538.jpg', '/static/img/portfolio/manic/IMG_20220820_125058.jpg',
             '/static/img/portfolio/manic/IMG_20220915_091052.jpg', '/static/img/portfolio/manic/IMG_20220921_083042.jpg',
             '/static/img/portfolio/manic/IMG_20220921_151139.jpg', '/static/img/portfolio/manic/IMG_20221009_075913.jpg',
             '/static/img/portfolio/manic/IMG_20221022_234059 (1).jpg', '/static/img/portfolio/manic/IMG_20221028_191603.jpg',
             '/static/img/portfolio/manic/IMG_20221030_095914.jpg', '/static/img/portfolio/manic/IMG_20221126_233926.jpg',
             '/static/img/portfolio/manic/IMG_20221224_142402.jpg', '/static/img/portfolio/manic/IMG_20221225_172604.jpg',
             '/static/img/portfolio/manic/IMG_20230105_233458.jpg', '/static/img/portfolio/manic/IMG_20230110_205124.jpg',
             '/static/img/portfolio/manic/IMG_20230110_205319.jpg', '/static/img/portfolio/manic/IMG_20230117_200755.jpg',
             '/static/img/portfolio/manic/IMG_20230118_145351.jpg', '/static/img/portfolio/manic/IMG_20230128_135147.jpg',
             '/static/img/portfolio/manic/IMG_20230129_091938.jpg', '/static/img/portfolio/manic/IMG_20230226_023714.jpg',
             '/static/img/portfolio/manic/IMG_20230321_180323.jpg', '/static/img/portfolio/manic/IMG_20230408_201114.jpg',
             '/static/img/portfolio/manic/IMG_20230413_233435.jpg', '/static/img/portfolio/manic/IMG_20230421_061254.jpg',
             '/static/img/portfolio/manic/IMG_20230426_191450.jpg', '/static/img/portfolio/manic/IMG_20230504_204051.jpg',
             '/static/img/portfolio/manic/IMG_20230510_092239.jpg', '/static/img/portfolio/manic/IMG_20230601_214654.jpg',
             '/static/img/portfolio/manic/IMG_20230621_220516.jpg', '/static/img/portfolio/manic/IMG_20230702_174641.jpg',
             '/static/img/portfolio/manic/IMG_20230715_092544.jpg', '/static/img/portfolio/manic/IMG_20230725_142406.jpg',
             '/static/img/portfolio/manic/IMG_20230726_164119.jpg', '/static/img/portfolio/manic/IMG_20230807_182040.jpg',
             '/static/img/portfolio/manic/IMG_20230808_095457.jpg', '/static/img/portfolio/manic/IMG_20230822_154435.jpg',
             '/static/img/portfolio/manic/IMG_20230922_081503.jpg', '/static/img/portfolio/manic/IMG_20230923_235041.jpg',
             '/static/img/portfolio/manic/IMG_20231024_093636.jpg', '/static/img/portfolio/manic/IMG_20231107_174609.jpg',
             '/static/img/portfolio/manic/IMG_20231124_183654.jpg', '/static/img/portfolio/manic/IMG_20231226_091831.jpg',
             '/static/img/portfolio/manic/IMG_20231226_202146.jpg', '/static/img/portfolio/manic/IMG_20231227_142735.jpg',
             '/static/img/portfolio/manic/IMG_20231228_222705.jpg', '/static/img/portfolio/manic/Screenshot_2023-01-20-07-02-32-303_com.miui.gallery.jpg',
             '/static/img/portfolio/manic/Screenshot_20220311-215016.png', '/static/img/portfolio/manic/Screenshot_20220311-215309.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215142.png', '/static/img/portfolio/manic/Screenshot_20220311-215228.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215331.png', '/static/img/portfolio/manic/Screenshot_20220311-215343.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215351.png', '/static/img/portfolio/manic/Screenshot_20220311-215358.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215411.png', '/static/img/portfolio/manic/Screenshot_20220311-215417.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215424.png', '/static/img/portfolio/manic/Screenshot_20220311-215443.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215453.png', '/static/img/portfolio/manic/Screenshot_20220311-215457.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215518.png', '/static/img/portfolio/manic/Screenshot_20220311-215532.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215659.png', '/static/img/portfolio/manic/Screenshot_20220311-215713.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215728.png', '/static/img/portfolio/manic/Screenshot_20220311-215813.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215820.png', '/static/img/portfolio/manic/Screenshot_20220311-215834.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215857.png', '/static/img/portfolio/manic/Screenshot_20220311-215904.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215932.png', '/static/img/portfolio/manic/Screenshot_20220311-215938.png',
             '/static/img/portfolio/manic/Screenshot_20220311-215945.png', '/static/img/portfolio/manic/Screenshot_20220311-220018.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220031.png', '/static/img/portfolio/manic/Screenshot_20220311-220102.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220112.png', '/static/img/portfolio/manic/Screenshot_20220311-220137.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220156.png', '/static/img/portfolio/manic/Screenshot_20220311-220205.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220226.png', '/static/img/portfolio/manic/Screenshot_20220311-220254.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220311.png', '/static/img/portfolio/manic/Screenshot_20220311-220336.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220353.png', '/static/img/portfolio/manic/Screenshot_20220311-220416.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220422.png', '/static/img/portfolio/manic/Screenshot_20220311-220432.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220440.png', '/static/img/portfolio/manic/Screenshot_20220311-220552.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220613.png', '/static/img/portfolio/manic/Screenshot_20220311-220620.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220625.png', '/static/img/portfolio/manic/Screenshot_20220311-220634.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220646.png', '/static/img/portfolio/manic/Screenshot_20220311-220655.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220702.png', '/static/img/portfolio/manic/Screenshot_20220311-220710.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220716.png', '/static/img/portfolio/manic/Screenshot_20220311-220726.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220739.png', '/static/img/portfolio/manic/Screenshot_20220311-220746.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220808.png', '/static/img/portfolio/manic/Screenshot_20220311-220817.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220825.png', '/static/img/portfolio/manic/Screenshot_20220311-220832.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220841.png', '/static/img/portfolio/manic/Screenshot_20220311-220845.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220927.png', '/static/img/portfolio/manic/Screenshot_20220311-220935.png',
             '/static/img/portfolio/manic/Screenshot_20220311-220951.png', '/static/img/portfolio/manic/Screenshot_20220311-221003.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221036.png', '/static/img/portfolio/manic/Screenshot_20220311-221041.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221048.png', '/static/img/portfolio/manic/Screenshot_20220311-221158.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221328.png', '/static/img/portfolio/manic/Screenshot_20220311-221357.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221413.png', '/static/img/portfolio/manic/Screenshot_20220311-221430.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221439.png', '/static/img/portfolio/manic/Screenshot_20220311-221457.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221559.png', '/static/img/portfolio/manic/Screenshot_20220311-221645.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221742.png', '/static/img/portfolio/manic/Screenshot_20220311-221830.png',
             '/static/img/portfolio/manic/Screenshot_20220311-221903.png', '/static/img/portfolio/manic/Screenshot_20220311-221934.png',
             '/static/img/portfolio/manic/Screenshot_20220311-222036.png', '/static/img/portfolio/manic/Screenshot_20220311-222047.png',
             '/static/img/portfolio/manic/Screenshot_20220311-222053.png', '/static/img/portfolio/manic/Screenshot_20220311-222228.png',
             '/static/img/portfolio/manic/Screenshot_20220311-222303.png', '/static/img/portfolio/manic/Screenshot_20220311-222349.png',
    ]
    context = {
        'images': images,
        'images_hair': images_hair,
        'images_manic': images_manic,
    }

    return render(request, "catalog/portfolio.html", context)



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
        "Коррекция бровей ************************************** 200"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_eyebrows.html", context=context)

def price_hair(request):
    title = [
        "Стрижка ************************************************* 800",
        "Окрашивание в один тон ***************************** 1500",
        "Мелирование ****************************************** 2500",
        "Тонирование ******************************************* 1500",
        "Колорирование **************************************** 2500",
        "Сложное окрашивание ******************************** 3500",
        "Химическая завивка *********************************** 2500",
        "Укладка феном ****************************************** 500",
        "Укладка вечерняя ************************************** 1500",
        "Причёска вечерняя ************************************ 2000",
        "Причёска свадебная *********************************** 4000"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_hair.html", context=context)

def reg_for_manic(request):
    list_man = [
        "Маникюр классический без покрытия: ------------------------- 800 руб --------------- 30 -50 мин",
        "Маникюр классический с покрытием (лак): ------------------- 900 руб ---------------------- 1 час",
        "Маникюр + наращивание (гель) + покрытие: ---------------- 2500 руб ----------------- 2 - 3 часа",
        "Маникюр + наращивание (гель) + покрытие, дизайн: ------2500 - 3000 руб ----------2 - 3 часа",
        "Коррекция ногтей (гель): ------------------------------------ 2000 руб -------------------- 2,5 - 3 часа ",
        "Коррекция ногтей (гель), дизайн: ------------------- 2000 - 2500 руб ------------------ 2,5 - 3 часа ",
        "Маникюр + покрытие (гель-лак) в один тон: --------------- 1700 руб -------------------- 1,5 часа ",
        "Коррекция ногтей (гель-лак): --------------------------------- 1800 руб ----------------- 1,5 - 2 часа",
        "Снятие покрытия + маникюр (классич., аппарат.): ------ 1000 руб -------------------------- 1 час",
        "Снятие нарощенных ногтей + маникюр: ------------------- 1200 руб ------------------------- 1 час"
    ]
    context = {
        'list_man': list_man,
    }
    return render(request, "catalog/reg_manic.html", context=context)
