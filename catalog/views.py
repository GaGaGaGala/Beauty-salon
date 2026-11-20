from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Service, Profile, Image, Booking, WorkingSchedule, ScheduleException, DayPlan, PersonalEvent, Review, PortfolioImage, CalendarSettings, RecurringBusy, PortfolioCategory, PortfolioImageReaction
from .forms import (ServiceForm, ProfileForm, UserForm, SignUpForm, BookingForm, BookingMasterForm,
                    WorkingScheduleForm, ScheduleExceptionForm, DayPlanForm, PersonalEventForm,
                    ReviewForm, PortfolioImageForm, CalendarSettingsForm, RecurringBusyForm)
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from .scheduling import intervals_overlap, is_slot_available, get_working_interval, available_slots as available_slots_list, is_dispatch_duty, is_auto_cycle_exception
from django.utils import timezone
from django.db.models import Q
from functools import wraps
import calendar
from datetime import date, timedelta, datetime


def client_access_required(view_func):
    """Allow only authenticated users; show a friendly message to guests."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'access_restricted.html')
        return view_func(request, *args, **kwargs)
    return wrapper

def is_master(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


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
            login(request, user, backend='catalog.backends.PhoneOrUsernameBackend')
            messages.success(request, f'Ваш логин: {user.username}\nПожалуйста, запомните или сохраните его. Он понадобится для входа в личный кабинет с другого устройства или после выхода из аккаунта')
            return redirect('catalog:my_bookings')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@client_access_required
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
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, ('Ваш профиль был успешно обновлен!'))
            return redirect('catalog:profile')
        else:
            messages.error(request, ('Пожалуйста, исправьте ошибки.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
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
    from .models import PortfolioImage, PortfolioImageReaction

    user = request.user if request.user.is_authenticated else None

    def make_item(portfolio_image):
        item = {
            'url': portfolio_image.image.url,
            'id': portfolio_image.id,
            'likes': 0,
            'dislikes': 0,
            'user_reaction': None,
        }
        reactions = PortfolioImageReaction.objects.filter(image=portfolio_image)
        item['likes'] = reactions.filter(reaction=PortfolioImageReaction.REACTION_LIKE).count()
        item['dislikes'] = reactions.filter(reaction=PortfolioImageReaction.REACTION_DISLIKE).count()
        if user is not None:
            own = reactions.filter(user=user).first()
            item['user_reaction'] = own.reaction if own else None
        return item

    def collect(category):
        return [
            make_item(image)
            for image in PortfolioImage.objects.filter(is_published=True, category=category).order_by('-created_at')
            if image.image
        ]

    context = {
        'images_hair': collect(PortfolioCategory.HAIR),
        'images_manicure': collect(PortfolioCategory.MANICURE),
        'images_pedicure': collect(PortfolioCategory.PEDICURE),
        'images_brows': collect(PortfolioCategory.BROWS),
        'images_other': collect(PortfolioCategory.OTHER),
    }
    return render(request, "catalog/portfolio.html", context)





def price_manicure(request):
    title = [
        "Маникюр классический без покрытия ********************************* 1000",
        "Маникюр классический с покрытием (лак) **************************** 1100",
        "Маникюр + укрепление (гель) + покрытие в один тон************ 2500",
        "Коррекция ногтей (гель) + покрытие в один тон ****************************** 2500",
        "Дизайн одного ногтя **************************************************** 100",
        "Френч ******************************************************************** 300",
        "Амбре ******************************************************************** 500",
        "Маникюр + покрытие (гель-лак) в один тон ************************** 2000",
        "Коррекция ногтей (гель-лак) ******************************************* 2200",
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
        "Педикюр классический полный без покрытия ************** 2000",
        "Педикюр комплексный с покрытием (гель-лак) ************* 2500",
        "Педикюр комплексный с покрытием (лак) ****************** 2100",
        "Педикюр (пальчики) с покрытием (гель-лак) *************** 2000"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_pedicure.html", context=context)

def price_eyebrows(request):
    title = [
        "Окрашивание бровей *********************************** 300",
        "Окрашивание ресниц *********************************** 300",
        "Коррекция бровей ************************************** 300"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_eyebrows.html", context=context)

def price_hair(request):
    title = [
        "Стрижка ************************************************* 1000",
        "Окрашивание в один тон(+ краска) ********************* 2000",
        "Мелирование (корни)*********************************** 3000",
        "Тонирование ******************************************* 2000",
        "Колорирование **************************************** 3500",
        "Сложное окрашивание (шатуш, омбре, балаяж)************** от 5000",
        "Химическая завивка ******************************** от  2500",
        "Укладка феном **************************************** 1000",
        "Укладка вечерняя (+ препараты)*************************** 1500",
        "Причёска вечерняя ************************************ 3000",
        "Причёска свадебная *********************************** 5000"
    ]
    context = {
        'title': title,
    }
    return render(request, "catalog/price_hair.html", context=context)

@client_access_required
def portfolio_like(request, pk):
    image = get_object_or_404(PortfolioImage, pk=pk, is_published=True)
    user = request.user
    existing = PortfolioImageReaction.objects.filter(image=image, user=user).first()
    if existing and existing.reaction == PortfolioImageReaction.REACTION_LIKE:
        existing.delete()
    elif existing and existing.reaction == PortfolioImageReaction.REACTION_DISLIKE:
        existing.reaction = PortfolioImageReaction.REACTION_LIKE
        existing.save()
    else:
        PortfolioImageReaction.objects.create(image=image, user=user, reaction=PortfolioImageReaction.REACTION_LIKE)
    return redirect(f"{reverse('catalog:port')}#portfolio-image-{pk}")


@client_access_required
def portfolio_dislike(request, pk):
    image = get_object_or_404(PortfolioImage, pk=pk, is_published=True)
    user = request.user
    existing = PortfolioImageReaction.objects.filter(image=image, user=user).first()
    if existing and existing.reaction == PortfolioImageReaction.REACTION_DISLIKE:
        existing.delete()
    elif existing and existing.reaction == PortfolioImageReaction.REACTION_LIKE:
        existing.reaction = PortfolioImageReaction.REACTION_DISLIKE
        existing.save()
    else:
        PortfolioImageReaction.objects.create(image=image, user=user, reaction=PortfolioImageReaction.REACTION_DISLIKE)
    return redirect(f"{reverse('catalog:port')}#portfolio-image-{pk}")


@client_access_required
def reg_for_manic(request):
    manicure_services = [
        ("Маникюр классический без покрытия", 800, 40),
        ("Маникюр классический с покрытием (лак)", 900, 60),
        ("Маникюр + наращивание (гель) + покрытие", 2500, 150),
        ("Маникюр + наращивание (гель) + покрытие, дизайн", 2500, 150),
        ("Коррекция ногтей (гель)", 2000, 165),
        ("Коррекция ногтей (гель), дизайн", 2000, 165),
        ("Маникюр + покрытие (гель-лак) в один тон", 1700, 90),
        ("Коррекция ногтей (гель-лак)", 1800, 105),
        ("Снятие покрытия + маникюр (классич., аппарат.)", 1000, 60),
        ("Снятие нарощенных ногтей + маникюр", 1200, 60),
    ]
    for title, price, duration in manicure_services:
        Service.objects.get_or_create(
            title=title,
            category='manicure',
            defaults={'price': price, 'duration_minutes': duration, 'is_active': True},
        )
    services = Service.objects.filter(category='manicure', is_active=True)
    return render(request, "catalog/reg_manic.html", {'services': services})

@client_access_required
def reg_for_pedic(request):
    pedicure_services = [
        ("Педикюр классический полный без покрытия", 2000, 90),
        ("Педикюр комплексный с покрытием (гель-лак)", 2500, 120),
        ("Педикюр комплексный с покрытием (лак)", 2100, 105),
        ("Педикюр (пальчики) с покрытием (гель-лак)", 2000, 90),
    ]
    for title, price, duration in pedicure_services:
        Service.objects.get_or_create(
            title=title,
            category='pedicure',
            defaults={'price': price, 'duration_minutes': duration, 'is_active': True},
        )
    services = Service.objects.filter(category='pedicure', is_active=True)
    return render(request, "catalog/reg_pedic.html", {'services': services})


@client_access_required
def reg_for_brows(request):
    brow_services = [
        ("Окрашивание бровей", 300, 15),
        ("Окрашивание ресниц", 300, 15),
        ("Коррекция бровей", 300, 15),
    ]
    for title, price, duration in brow_services:
        Service.objects.get_or_create(
            title=title,
            category='brows',
            defaults={'price': price, 'duration_minutes': duration, 'is_active': True},
        )
    services = Service.objects.filter(category='brows', is_active=True)
    return render(request, "catalog/reg_brows.html", {'services': services})


@client_access_required
def reg_for_hair(request):
    hair_services = [
        ("Стрижка", 1000, 30),
        ("Окрашивание в один тон (+краска)", 2000, 60),
        ("Мелирование (корни)", 3000, 120),
        ("Тонирование", 2000, 60),
        ("Колорирование", 3500, 135),
        ("Сложное окрашивание (шатуш, омбре, балаяж)", 5000, 195),
        ("Химическая завивка", 2500, 120),
        ("Укладка феном", 1000, 45),
        ("Укладка вечерняя (+ препараты)", 1500, 75),
        ("Причёска вечерняя", 3000, 105),
        ("Причёска свадебная", 5000, 150),
    ]
    for title, price, duration in hair_services:
        Service.objects.get_or_create(
            title=title,
            category='hair',
            defaults={'price': price, 'duration_minutes': duration, 'is_active': True},
        )
    services = Service.objects.filter(category='hair', is_active=True)
    return render(request, "catalog/reg_hair.html", {'services': services})


@client_access_required
def booking_create(request):
    if not request.user.is_authenticated:
        return redirect('login')
    service_id = request.GET.get('service') or request.POST.get('service')
    selected_service = None
    if service_id:
        try:
            selected_service = Service.objects.get(pk=service_id, is_active=True)
        except (Service.DoesNotExist, ValueError):
            selected_service = None
    available_slots = []
    selected_date = request.GET.get('date') or request.POST.get('desired_date')
    if selected_date:
        try:
            d = datetime.strptime(selected_date, '%Y-%m-%d').date()
            duration = selected_service.duration_minutes if selected_service else 60
            available_slots = available_slots_list(d, duration)
        except ValueError:
            available_slots = []
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            if selected_service and not booking.service_id:
                booking.service = selected_service
            booking.client = request.user
            booking.status = 'pending'
            booking.duration_minutes = booking.service.duration_minutes
            # Server-side availability check
            start = booking.desired_datetime
            end = start + timezone.timedelta(minutes=booking.duration_minutes)
            if not is_slot_available(start, end):
                messages.error(request, 'Выбранное время недоступно. Выберите другой интервал.')
                # recompute slots for the date
                try:
                    d = start.date()
                    available_slots = available_slots_list(d, booking.duration_minutes)
                except Exception:
                    available_slots = []
                return render(request, 'catalog/booking_form.html', {
                    'form': form, 'selected_service': selected_service,
                    'available_slots': available_slots, 'selected_date': selected_date,
                })
            # Защита от повторного создания одинаковой заявки при двойном нажатии
            existing = Booking.objects.filter(
                client=request.user,
                service=booking.service,
                desired_datetime=booking.desired_datetime,
                status='pending',
            ).first()
            if existing:
                messages.info(request, 'Такая заявка уже создана. Проверьте личный кабинет.')
                return redirect('catalog:my_bookings')
            if not booking.client_district:
                try:
                    booking.client_district = request.user.profile.district
                except Exception:
                    booking.client_district = ''
            booking.save()
            messages.success(request, f'Ваша заявка успешно создана! Вы выбрали услугу: {booking.service.title}. Информация о записи доступна в личном кабинете.')
            return redirect('catalog:my_bookings')
    else:
        initial = {'service': selected_service.id} if selected_service else {}
        form = BookingForm(initial=initial)
    return render(request, 'catalog/booking_form.html', {
        'form': form, 'selected_service': selected_service,
        'available_slots': available_slots, 'selected_date': selected_date,
    })


def reviews(request):
    """Публичная страница отзывов."""
    public_reviews = Review.objects.filter(status=Review.STATUS_PUBLISHED).order_by('-created_at')
    return render(request, 'catalog/reviews.html', {'reviews': public_reviews})


@client_access_required
@client_access_required
def review_create(request):
    """Выбор выполненной услуги для создания отзыва."""
    completed = Booking.objects.filter(client=request.user, status='completed').order_by('-created_at')
    reviewed_booking_ids = set(Review.objects.filter(client=request.user).values_list('booking_id', flat=True))
    eligible = [b for b in completed if b.pk not in reviewed_booking_ids]
    if not eligible:
        messages.info(request, 'У вас нет выполненных услуг без отзыва. Перейдите в личный кабинет к подходящей записи.')
        return redirect('catalog:my_bookings')
    if len(eligible) == 1:
        return redirect('catalog:booking_review', pk=eligible[0].pk)
    return render(request, 'catalog/review_select.html', {'bookings': eligible})


@client_access_required
def my_bookings(request):
    bookings = Booking.objects.filter(client=request.user).order_by('-created_at')
    completed_bookings = bookings.filter(status='completed')
    reviews = Review.objects.filter(client=request.user).order_by('-created_at')
    reviewed_booking_ids = set(reviews.values_list('booking_id', flat=True))
    return render(request, 'catalog/my_bookings.html', {
        'bookings': bookings,
        'completed_bookings': completed_bookings,
        'reviews': reviews,
        'reviewed_booking_ids': reviewed_booking_ids,
    })


@client_access_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status in ('pending', 'proposed', 'confirmed'):
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Запись отменена.')
    else:
        messages.error(request, 'Невозможно отменить эту запись.')
    return redirect('catalog:my_bookings')


@client_access_required
def booking_accept_proposal(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status == 'proposed':
        start = booking.confirmed_start or booking.desired_datetime
        end = booking.confirmed_end or (start + timezone.timedelta(minutes=booking.duration_minutes))
        if not is_slot_available(start, end, exclude_booking_id=booking.id):
            messages.error(request, 'Предложенное время недоступно. Обратитесь к мастеру.')
            return redirect('catalog:my_bookings')
        booking.status = 'confirmed'
        booking.confirmed_start = start
        booking.confirmed_end = end
        booking.save()
        messages.success(request, 'Вы приняли предложенное время. Запись подтверждена.')
    else:
        messages.error(request, 'Эта запись не ожидает подтверждения предложенного времени.')
    return redirect('catalog:my_bookings')


@client_access_required
def booking_reject_proposal(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status == 'proposed':
        booking.status = 'rejected'
        booking.confirmed_start = None
        booking.confirmed_end = None
        booking.save()
        messages.success(request, 'Предложенное время отклонено.')
    else:
        messages.error(request, 'Эта запись не ожидает подтверждения предложенного времени.')
    return redirect('catalog:my_bookings')


@client_access_required
def booking_review(request, pk):
    booking = get_object_or_404(Booking, pk=pk, client=request.user)
    if booking.status != 'completed':
        messages.error(request, 'Отзыв можно оставить только после выполненной услуги.')
        return redirect('catalog:my_bookings')
    if Review.objects.filter(booking=booking).exists():
        messages.info(request, 'Отзыв по этой записи уже оставлен.')
        return redirect('catalog:my_bookings')
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = request.user
            review.booking = booking
            if not review.service:
                review.service = booking.service
            review.status = Review.STATUS_PENDING
            review.save()
            messages.success(request, 'Отзыв отправлен на модерацию.')
            return redirect('catalog:my_bookings')
    else:
        form = ReviewForm(initial={'service': booking.service})
    return render(request, 'catalog/review_form.html', {'form': form, 'booking': booking})


def master_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not is_master(request.user):
            messages.error(request, 'Доступ запрещён.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@master_required
def master_clients(request):
    clients = User.objects.filter(bookings__isnull=False).distinct().order_by('username')
    client_data = []
    for client in clients:
        bookings = Booking.objects.filter(client=client).select_related('service').order_by('-desired_datetime')
        client_data.append({
            'client': client,
            'bookings': bookings,
            'completed': bookings.filter(status='completed'),
        })
    return render(request, 'catalog/master_clients.html', {'client_data': client_data})


@master_required
def master_dashboard(request):
    pending = Booking.objects.filter(status='pending').order_by('desired_datetime')
    proposed = Booking.objects.filter(status='proposed').order_by('confirmed_start')
    confirmed = Booking.objects.filter(status='confirmed').order_by('confirmed_start')
    rejected = Booking.objects.filter(status='rejected').order_by('-updated_at')
    cancelled = Booking.objects.filter(status='cancelled').order_by('-updated_at')
    completed = Booking.objects.filter(status='completed').order_by('-updated_at')
    return render(request, 'catalog/master_dashboard.html', {
        'pending': pending, 'proposed': proposed, 'confirmed': confirmed,
        'rejected': rejected, 'cancelled': cancelled, 'completed': completed,
    })


@master_required
def master_booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingMasterForm(request.POST, instance=booking)
        if form.is_valid():
            new_start = form.cleaned_data.get('confirmed_start')
            new_end = form.cleaned_data.get('confirmed_end')
            new_status = form.cleaned_data.get('status')
            # Если мастер указал согласованное время, заявка подтверждается,
            # даже если статус в форме остался «Ожидает подтверждения».
            if new_status == 'pending' and new_start:
                new_status = 'confirmed'
            # При возврате в ожидание/отклонении/отмене очищаем подтверждённое время
            if new_status in ('pending', 'rejected', 'cancelled'):
                new_start = None
                new_end = None
            # Для предложения другого времени время обязательно
            if new_status == 'proposed':
                if not new_start or not new_end:
                    messages.error(request, 'Укажите начало и окончание для предложенного времени.')
                    return render(request, 'catalog/master_booking_detail.html', {'form': form, 'booking': booking})
                if new_end <= new_start:
                    messages.error(request, 'Окончание должно быть позже начала.')
                    return render(request, 'catalog/master_booking_detail.html', {'form': form, 'booking': booking})
                if not is_slot_available(new_start, new_end, exclude_booking_id=booking.id):
                    messages.error(request, 'Интервал пересекается с другими записями или личными событиями.')
                    return render(request, 'catalog/master_booking_detail.html', {'form': form, 'booking': booking})
            # Для подтверждения автозаполнение из желаемого времени, если не указано
            if new_status == 'confirmed':
                if not new_start:
                    new_start = booking.desired_datetime
                if not new_end:
                    new_end = new_start + timezone.timedelta(minutes=booking.duration_minutes)
                if new_end <= new_start:
                    messages.error(request, 'Окончание должно быть позже начала.')
                    return render(request, 'catalog/master_booking_detail.html', {'form': form, 'booking': booking})
                if not is_slot_available(new_start, new_end, exclude_booking_id=booking.id):
                    messages.error(request, 'Интервал пересекается с другими записями или личными событиями.')
                    return render(request, 'catalog/master_booking_detail.html', {'form': form, 'booking': booking})
            with transaction.atomic():
                booking = form.save(commit=False)
                booking.status = new_status
                booking.confirmed_start = new_start
                booking.confirmed_end = new_end
                if booking.status == 'confirmed' and not booking.confirmed_start:
                    booking.confirmed_start = booking.desired_datetime
                if booking.status == 'confirmed' and not booking.confirmed_end:
                    booking.confirmed_end = booking.confirmed_start + timezone.timedelta(minutes=booking.duration_minutes)
                booking.save()
            messages.success(request, 'Запись обновлена.')
            return redirect('catalog:master_dashboard')
    else:
        form = BookingMasterForm(instance=booking)
    return render(request, 'catalog/master_booking_detail.html', {'form': form, 'booking': booking})


@master_required
def master_booking_reject(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status not in ('completed', 'cancelled'):
        booking.status = 'rejected'
        booking.save()
        messages.success(request, 'Заявка отклонена.')
    else:
        messages.error(request, 'Невозможно отклонить эту запись.')
    return redirect('catalog:master_dashboard')


@master_required
def master_booking_complete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.status == 'confirmed':
        booking.status = 'completed'
        booking.save()
        messages.success(request, 'Запись отмечена выполненной.')
    else:
        messages.error(request, 'Выполнить можно только подтверждённую запись.')
    return redirect('catalog:master_dashboard')


@master_required
def master_services(request):
    services = Service.objects.all().order_by('category', 'title')
    return render(request, 'catalog/master_services.html', {'services': services})


@master_required
def master_service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Услуга создана.')
            return redirect('catalog:master_services')
    else:
        form = ServiceForm()
    return render(request, 'catalog/master_service_form.html', {'form': form})


@master_required
def master_service_edit(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Услуга обновлена.')
            return redirect('catalog:master_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'catalog/master_service_form.html', {'form': form, 'service': service})


@master_required
def master_service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        messages.success(request, 'Услуга удалена.')
        return redirect('catalog:master_services')
    return render(request, 'catalog/master_service_delete.html', {'service': service})


@master_required
def master_schedule(request):
    schedules = WorkingSchedule.objects.all().order_by('day_of_week')
    if request.method == 'POST':
        form = WorkingScheduleForm(request.POST)
        if form.is_valid():
            WorkingSchedule.objects.update_or_create(
                day_of_week=form.cleaned_data['day_of_week'],
                defaults={
                    'start_time': form.cleaned_data['start_time'],
                    'end_time': form.cleaned_data['end_time'],
                    'is_working': form.cleaned_data['is_working'],
                }
            )
            messages.success(request, 'График сохранён.')
            return redirect('catalog:master_schedule')
    else:
        form = WorkingScheduleForm()
    return render(request, 'catalog/master_schedule.html', {'schedules': schedules, 'form': form})


@master_required
def master_exceptions(request):
    exceptions = ScheduleException.objects.all().order_by('date')
    if request.method == 'POST':
        form = ScheduleExceptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Исключение добавлено.')
            return redirect('catalog:master_exceptions')
    else:
        form = ScheduleExceptionForm()
    return render(request, 'catalog/master_exceptions.html', {'exceptions': exceptions, 'form': form})


@master_required
def master_exception_delete(request, pk):
    exc = get_object_or_404(ScheduleException, pk=pk)
    if request.method == 'POST':
        exc.delete()
        messages.success(request, 'Исключение удалено.')
        return redirect('catalog:master_exceptions')
    return render(request, 'catalog/master_exception_delete.html', {'exc': exc})


@master_required
def master_dayplans(request):
    plans = DayPlan.objects.all().order_by('date')
    if request.method == 'POST':
        form = DayPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'План дня добавлен.')
            return redirect('catalog:master_dayplans')
    else:
        form = DayPlanForm()
    return render(request, 'catalog/master_dayplans.html', {'plans': plans, 'form': form})


@master_required
def master_events(request):
    events = PersonalEvent.objects.all().order_by('start_datetime')
    if request.method == 'POST':
        form = PersonalEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            if event.end_datetime <= event.start_datetime:
                messages.error(request, 'Окончание должно быть позже начала.')
            else:
                event.save()
                messages.success(request, 'Событие добавлено.')
                return redirect('catalog:master_events')
    else:
        form = PersonalEventForm()
    return render(request, 'catalog/master_events.html', {'events': events, 'form': form})


@master_required
def master_event_delete(request, pk):
    event = get_object_or_404(PersonalEvent, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Событие удалено.')
        return redirect('catalog:master_events')
    return render(request, 'catalog/master_event_delete.html', {'event': event})


@master_required
def master_reviews(request):
    reviews = Review.objects.all().order_by('-created_at')
    return render(request, 'catalog/master_reviews.html', {'reviews': reviews})


@master_required
def master_review_toggle(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.status == Review.STATUS_PUBLISHED:
        review.status = Review.STATUS_PENDING
    else:
        review.status = Review.STATUS_PUBLISHED
    review.save()
    messages.success(request, 'Статус отзыва изменён.')
    return redirect('catalog:master_reviews')


@master_required
def master_review_publish(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.status = Review.STATUS_PUBLISHED
    review.save()
    messages.success(request, 'Отзыв опубликован.')
    return redirect('catalog:master_reviews')


@master_required
def master_review_reject(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.status = Review.STATUS_REJECTED
    review.save()
    messages.success(request, 'Отзыв отклонён.')
    return redirect('catalog:master_reviews')


@master_required
def master_review_pending(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.status = Review.STATUS_PENDING
    review.save()
    messages.success(request, 'Отзыв отправлен на модерацию.')
    return redirect('catalog:master_reviews')


@client_access_required
def review_like(request, pk):
    review = get_object_or_404(Review, pk=pk, status=Review.STATUS_PUBLISHED)
    user = request.user
    if review.dislikes.filter(pk=user.pk).exists():
        review.dislikes.remove(user)
    if review.likes.filter(pk=user.pk).exists():
        review.likes.remove(user)
    else:
        review.likes.add(user)
    return redirect(f"{reverse('catalog:reviews')}#review-{pk}")


@client_access_required
def review_dislike(request, pk):
    review = get_object_or_404(Review, pk=pk, status=Review.STATUS_PUBLISHED)
    user = request.user
    if review.likes.filter(pk=user.pk).exists():
        review.likes.remove(user)
    if review.dislikes.filter(pk=user.pk).exists():
        review.dislikes.remove(user)
    else:
        review.dislikes.add(user)
    return redirect(f"{reverse('catalog:reviews')}#review-{pk}")


@master_required
def master_portfolio(request):
    images = PortfolioImage.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = PortfolioImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изображение добавлено.')
            return redirect('catalog:master_portfolio')
    else:
        form = PortfolioImageForm()
    return render(request, 'catalog/master_portfolio.html', {'images': images, 'form': form})


@master_required
def master_portfolio_delete(request, pk):
    img = get_object_or_404(PortfolioImage, pk=pk)
    if request.method == 'POST':
        img.delete()
        messages.success(request, 'Изображение удалено.')
        return redirect('catalog:master_portfolio')
    return render(request, 'catalog/master_portfolio_delete.html', {'img': img})


@master_required
def master_calendar(request):
    today = timezone.now().date()
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
    except (TypeError, ValueError):
        year, month = today.year, today.month
    if month < 1:
        month = 1
    if month > 12:
        month = 12

    cs, _ = CalendarSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'autogen':
            start_date_str = request.POST.get('auto_start_date') or today.isoformat()
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = today
            cs.dispatch_cycle_start = start_date
            try:
                cs.dispatch_cycle_length = int(request.POST.get('cycle_length') or 4)
            except (TypeError, ValueError):
                cs.dispatch_cycle_length = 4
            # Удаляем только автоматически созданные исключения старого алгоритма,
            # ручные исключения мастера сохраняем.
            ScheduleException.objects.filter(
                reason__in=['Сутки через трое', 'Выходной (сутки через трое)'],
            ).delete()
            cs.save()
            messages.success(request, 'Настройки цикла «сутки через трое» сохранены. График пересчитан.')
            return redirect(f'{request.path}?year={year}&month={month}')
        elif action == 'set_day':
            form = ScheduleExceptionForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'День обновлён.')
            else:
                messages.error(request, 'Проверьте данные дня.')
            return redirect(f'{request.path}?year={year}&month={month}')
        elif action == 'add_busy':
            form = RecurringBusyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Повторяющаяся занятость добавлена.')
            else:
                messages.error(request, 'Проверьте данные занятости.')
            return redirect(f'{request.path}?year={year}&month={month}')
        elif action == 'delete_busy':
            try:
                RecurringBusy.objects.filter(pk=int(request.POST.get('busy_id'))).delete()
                messages.success(request, 'Запись удалена.')
            except (TypeError, ValueError):
                messages.error(request, 'Неверный идентификатор.')
            return redirect(f'{request.path}?year={year}&month={month}')
        elif action == 'set_dayplan':
            form = DayPlanForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Точка отправления сохранена.')
            else:
                messages.error(request, 'Проверьте данные.')
            return redirect(f'{request.path}?year={year}&month={month}')

    cal = calendar.monthcalendar(year, month)
    weeks = []
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(None)
                continue
            d = date(year, month, day)
            exc = ScheduleException.objects.filter(date=d).first()
            # Автоматические исключения старого алгоритма («сутки через трое»)
            # не должны перекрывать актуальный расчёт через is_dispatch_duty.
            # Учитываем только ручные исключения мастера.
            if exc is not None and is_auto_cycle_exception(exc):
                exc = None
            events = list(PersonalEvent.objects.filter(start_datetime__date=d))
            bookings_count = Booking.objects.filter(
                Q(confirmed_start__date=d) | Q(desired_datetime__date=d),
                status__in=['pending', 'proposed', 'confirmed'],
            ).count()
            if exc is not None:
                status = 'working' if exc.is_working else 'off'
            elif is_dispatch_duty(d):
                status = 'duty'
            else:
                wi = get_working_interval(d)
                status = 'working' if wi is not None else 'off'
            row.append({
                'day': day,
                'date': d,
                'status': status,
                'exception': exc,
                'events': events,
                'bookings': bookings_count,
                'is_duty': is_dispatch_duty(d),
            })
        weeks.append(row)

    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    ru_months = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']
    context = {
        'year': year,
        'month': month,
        'month_name': f"{ru_months[month-1].capitalize()} {year}",
        'weeks': weeks,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'exception_form': ScheduleExceptionForm(),
        'busy_form': RecurringBusyForm(),
        'dayplan_form': DayPlanForm(),
        'settings_form': CalendarSettingsForm(instance=cs),
        'calendar_settings': cs,
        'recurring_busy': RecurringBusy.objects.all(),
        'dayplans': DayPlan.objects.filter(date__year=year, date__month=month),
        'today': today,
        'client_bookings': Booking.objects.filter(status__in=['pending','proposed','confirmed']).select_related('client','service').order_by('desired_datetime'),
    }
    return render(request, 'catalog/master_calendar.html', context)
