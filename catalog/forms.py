from django import forms
from .models import (
    Service, Profile, Comment, Booking, WorkingSchedule,
    ScheduleException, DayPlan, PersonalEvent, Review, PortfolioImage,
    CalendarSettings, RecurringBusy,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'description', 'category', 'price', 'duration_minutes', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'category': 'Категория',
            'price': 'Цена',
            'duration_minutes': 'Длительность (мин)',
            'is_active': 'Активна',
        }


class SignUpForm(UserCreationForm):
    last_name = forms.CharField(label='Фамилия', max_length=100, required=True)
    first_name = forms.CharField(label='Имя', max_length=100, required=True)
    patronymic = forms.CharField(label='Отчество', max_length=100, required=True)
    phone = forms.CharField(label='Номер телефона', max_length=30, required=True)
    email = forms.EmailField(label='Электронная почта', required=False)
    district = forms.CharField(
        label='Район проживания или обслуживания',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    login_type = forms.ChoiceField(
        label='Способ создания логина',
        choices=(('auto', 'Создать автоматически'), ('manual', 'Придумать самому')),
        initial='auto',
        required=False,
        widget=forms.RadioSelect,
    )
    username = forms.CharField(
        label='Логин',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput,
        help_text='Пароль должен содержать не менее 8 символов и не быть слишком простым.',
    )
    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput,
        help_text='Введите тот же пароль ещё раз.',
    )

    class Meta:
        model = User
        fields = ('password1', 'password2')

    def clean_username(self):
        login_type = self.data.get('login_type') or self.cleaned_data.get('login_type') or 'auto'
        username = (self.cleaned_data.get('username') or '').strip()
        if login_type == 'manual':
            if not username:
                raise forms.ValidationError('Введите желаемый логин.')
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Этот логин уже занят. Выберите другой.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        last_name = self.cleaned_data['last_name']
        first_name = self.cleaned_data['first_name']
        patronymic = self.cleaned_data['patronymic']
        login_type = self.data.get('login_type') or self.cleaned_data.get('login_type') or 'auto'
        manual_username = (self.cleaned_data.get('username') or '').strip()
        if login_type == 'manual':
            username = manual_username
        else:
            base_username = ''.join(first_name.split())
            if not base_username:
                base_username = ''.join(last_name.split())
            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                username = f'{base_username}{suffix}'
                suffix += 1

        user = super().save(commit=False)
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = self.cleaned_data.get('email') or ''
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data['phone']
            profile.patronymic = patronymic
            profile.district = self.cleaned_data.get('district') or ''
            profile.save()
        self.generated_username = username
        return user


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Электронная почта',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('patronymic', 'birth_date', 'phone', 'district')
        labels = {
            'patronymic': 'Отчество',
            'birth_date': 'Дата рождения',
            'phone': 'Телефон',
            'district': 'Район обслуживания / проживания',
        }
        widgets = {
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('services', 'author', 'content', 'photo')


class BookingForm(forms.ModelForm):
    desired_datetime = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )

    class Meta:
        model = Booking
        fields = ['service', 'desired_datetime', 'client_district', 'client_comment']
        labels = {
            'service': 'Услуга',
            'desired_datetime': 'Желаемое время',
            'client_district': 'Район / адрес',
            'client_comment': 'Пожелания к процедуре',
        }
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'client_district': forms.TextInput(attrs={'class': 'form-control'}),
            'client_comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)


class BookingMasterForm(forms.ModelForm):
    confirmed_start = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )
    confirmed_end = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'],
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
    )

    class Meta:
        model = Booking
        fields = ['status', 'confirmed_start', 'confirmed_end', 'client_district', 'master_note']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'client_district': forms.TextInput(attrs={'class': 'form-control'}),
            'master_note': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'status': 'Статус',
            'confirmed_start': 'Согласованное начало',
            'confirmed_end': 'Согласованное окончание',
            'client_district': 'Район клиента',
            'master_note': 'Заметка мастера',
        }


class WorkingScheduleForm(forms.ModelForm):
    class Meta:
        model = WorkingSchedule
        fields = ['day_of_week', 'start_time', 'end_time', 'is_working']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }
        labels = {
            'day_of_week': 'День недели',
            'start_time': 'Начало',
            'end_time': 'Окончание',
            'is_working': 'Рабочий день',
        }


class ScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model = ScheduleException
        fields = ['date', 'is_working', 'start_time', 'end_time', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'date': 'Дата',
            'is_working': 'Рабочий день',
            'start_time': 'Начало',
            'end_time': 'Окончание',
            'reason': 'Причина',
        }


class DayPlanForm(forms.ModelForm):
    class Meta:
        model = DayPlan
        fields = ['date', 'start_time', 'start_location', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'start_location': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'date': 'Дата',
            'start_time': 'Время начала',
            'start_location': 'Место начала',
            'note': 'Заметка',
        }


class PersonalEventForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    end_datetime = forms.DateTimeField(input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))

    class Meta:
        model = PersonalEvent
        fields = ['title', 'event_type', 'start_datetime', 'end_datetime', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название',
            'event_type': 'Тип события',
            'start_datetime': 'Начало',
            'end_datetime': 'Окончание',
            'comment': 'Комментарий',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['service', 'rating', 'text', 'photo']
        widgets = {
            'service': forms.HiddenInput(),
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=[(i, '★' * i) for i in range(1, 6)]),
            'text': forms.Textarea(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'service': 'Услуга',
            'rating': 'Оценка',
            'text': 'Текст отзыва',
            'photo': 'Фото',
        }


class CalendarSettingsForm(forms.ModelForm):
    class Meta:
        model = CalendarSettings
        fields = ['dispatch_cycle_start', 'dispatch_cycle_length']
        widgets = {
            'dispatch_cycle_start': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dispatch_cycle_length': forms.NumberInput(attrs={'class': 'form-control', 'min': 2, 'max': 14}),
        }
        labels = {
            'dispatch_cycle_start': 'Дата первой смены в диспетчерской',
            'dispatch_cycle_length': 'Длина цикла (дней)',
        }


class RecurringBusyForm(forms.ModelForm):
    class Meta:
        model = RecurringBusy
        fields = ['weekday', 'start_time', 'end_time', 'buffer_before_minutes', 'buffer_after_minutes', 'active_from', 'is_active', 'comment']
        widgets = {
            'weekday': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'buffer_before_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'buffer_after_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'active_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'comment': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'weekday': 'День недели',
            'start_time': 'Начало',
            'end_time': 'Окончание',
            'buffer_before_minutes': 'Время до (мин)',
            'buffer_after_minutes': 'Время после (мин)',
            'active_from': 'Действует с',
            'is_active': 'Активно',
            'comment': 'Комментарий',
        }
class PortfolioImageForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['image', 'title', 'category', 'description', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }
        labels = {
            'image': 'Изображение',
            'title': 'Название',
            'category': 'Категория',
            'description': 'Описание',
            'is_published': 'Опубликовано',
        }