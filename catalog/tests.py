from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Service, Booking, WorkingSchedule, PersonalEvent, Review, PortfolioImage, Profile
from .scheduling import intervals_overlap, is_slot_available


class ServiceTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user('master', password='pass', is_staff=True, is_superuser=True)
        self.client = Client()
        self.client.login(username='master', password='pass')

    def test_service_create(self):
        resp = self.client.post('/catalog/master/services/create/', {
            'title': 'Маникюр', 'description': 'desc', 'category': 'manicure',
            'price': '1000.00', 'duration_minutes': 60, 'is_active': True,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Service.objects.count(), 1)

    def test_service_edit(self):
        s = Service.objects.create(title='A', price=100, duration_minutes=30)
        resp = self.client.post(f'/catalog/master/services/{s.id}/edit/', {
            'title': 'B', 'description': '', 'category': 'manicure',
            'price': '200.00', 'duration_minutes': 45, 'is_active': True,
        })
        self.assertEqual(resp.status_code, 302)
        s.refresh_from_db()
        self.assertEqual(s.title, 'B')


class AuthTests(TestCase):
    def test_profile_update_phone_district(self):
        user = User.objects.create_user('client2', password='pass')
        Profile.objects.get_or_create(user=user)
        c = Client()
        c.login(username='client2', password='pass')
        resp = c.post('/catalog/profile/', {
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'email': 'ivan@example.com',
            'patronymic': 'Иванович',
            'birth_date': '2000-01-01',
            'phone': '+79990001122',
            'district': 'Центр',
        })
        self.assertEqual(resp.status_code, 302)
        user.refresh_from_db()
        profile = user.profile
        profile.refresh_from_db()
        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.last_name, 'Иванов')
        self.assertEqual(profile.phone, '+79990001122')
        self.assertEqual(profile.district, 'Центр')
        self.assertEqual(profile.patronymic, 'Иванович')
    def test_signup(self):
        resp = self.client.post('/catalog/signup/', {
            'first_name': 'Иван',
            'patronymic': 'Иванович',
            'phone': '+79991234567',
            'email': 'ivan@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'login_type': 'auto',
        })
        self.assertIn(resp.status_code, (200, 302))
        user = User.objects.get(last_name='Иванов', first_name='Иван')
        self.assertTrue(user.check_password('StrongPass123!'))
        self.assertEqual(user.username, 'Иван')
        self.assertTrue(Profile.objects.filter(user=user, phone='+79991234567').exists())
        self.assertIn('_auth_user_id', self.client.session)
        cabinet_resp = self.client.get('/catalog/my-bookings/')
        self.assertEqual(cabinet_resp.status_code, 200)


class BookingTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user('master', password='pass', is_staff=True, is_superuser=True)
        self.client_user = User.objects.create_user('client', password='pass')
        self.service = Service.objects.create(title='Маникюр', price=1000, duration_minutes=60, is_active=True)
        booking_day = (timezone.now() + timedelta(days=1)).weekday()
        WorkingSchedule.objects.create(day_of_week=booking_day, start_time=timezone.now().time().replace(hour=0, minute=0),
                                     end_time=timezone.now().time().replace(hour=23, minute=59), is_working=True)
        self.c = Client()
        self.c.login(username='client', password='pass')

    def test_booking_create_pending(self):
        resp = self.c.post('/catalog/book/', {
            'service': self.service.id,
            'desired_datetime': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
            'client_district': 'Центр',
            'client_comment': 'test',
        })
        self.assertEqual(resp.status_code, 302)
        b = Booking.objects.get()
        self.assertEqual(b.status, 'pending')
        self.assertEqual(b.client, self.client_user)

    def test_client_cannot_see_others_booking(self):
        other = User.objects.create_user('other', password='pass')
        Booking.objects.create(client=other, service=self.service, desired_datetime=timezone.now() + timedelta(days=1), status='pending')
        resp = self.c.get('/catalog/my-bookings/')
        self.assertNotContains(resp, other.username)

    def test_master_can_confirm(self):
        booking = Booking.objects.create(client=self.client_user, service=self.service,
                                        desired_datetime=timezone.now() + timedelta(days=1), status='pending')
        mc = Client()
        mc.login(username='master', password='pass')
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(minutes=60)
        resp = mc.post(f'/catalog/master/booking/{booking.id}/', {
            'status': 'confirmed',
            'confirmed_start': start.strftime('%Y-%m-%dT%H:%M'),
            'confirmed_end': end.strftime('%Y-%m-%dT%H:%M'),
            'travel_time_minutes': 15,
            'client_district': 'Центр',
            'master_note': '',
        })
        self.assertEqual(resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')

    def test_master_confirm_persists_status_and_time(self):
        booking = Booking.objects.create(client=self.client_user, service=self.service,
                                        desired_datetime=timezone.now() + timedelta(days=1), status='pending')
        mc = Client()
        mc.login(username='master', password='pass')
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(minutes=60)
        resp = mc.post(f'/catalog/master/booking/{booking.id}/', {
            'status': 'pending',
            'confirmed_start': start.strftime('%Y-%m-%dT%H:%M'),
            'confirmed_end': end.strftime('%Y-%m-%dT%H:%M'),
            'client_district': 'Центр',
            'master_note': '',
        })
        self.assertEqual(resp.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')
        self.assertEqual(booking.confirmed_start.replace(microsecond=0), start.replace(microsecond=0, second=0))
        self.assertEqual(booking.confirmed_end.replace(microsecond=0), end.replace(microsecond=0, second=0))
        # подтверждённая заявка не в новых
        dash = mc.get('/catalog/master/')
        self.assertNotContains(dash, f'Обработать</a></td>\n      </tr>\n      <tr>\n        <td>{self.client_user.username}</td>\n        <td>{self.service.title}</td>\n        <td>{booking.desired_datetime}')
        # клиент видит статус и время
        self.c.get('/catalog/my-bookings/')
        client_resp = self.c.get('/catalog/my-bookings/')
        self.assertContains(client_resp, 'Подтверждена')
        self.assertContains(client_resp, booking.confirmed_start.strftime('%Y'))

    def test_overlap_check(self):
        start = timezone.now()
        end = start + timedelta(hours=1)
        self.assertTrue(intervals_overlap(start, end, start + timedelta(minutes=30), end + timedelta(minutes=30)))
        self.assertFalse(intervals_overlap(start, end, end, end + timedelta(hours=1)))


class SchedulingTests(TestCase):
    def setUp(self):
        self.master = User.objects.create_user('master', password='pass', is_staff=True, is_superuser=True)
        WorkingSchedule.objects.create(day_of_week=0, start_time=timezone.now().time().replace(hour=9, minute=0),
                                       end_time=timezone.now().time().replace(hour=18, minute=0), is_working=True)

    def test_personal_event_blocks(self):
        start = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=1)
        PersonalEvent.objects.create(title='Отпуск', event_type='vacation', start_datetime=start, end_datetime=end)
        self.assertFalse(is_slot_available(start + timedelta(minutes=30), end + timedelta(minutes=30)))


class ReviewTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create_user('client', password='pass')
        self.service = Service.objects.create(title='Маникюр', price=1000, duration_minutes=60, is_active=True)

    def test_review_rating_validation(self):
        from django.core.exceptions import ValidationError
        r = Review(client=self.client_user, service=self.service, rating=6)
        with self.assertRaises(ValidationError):
            r.full_clean()


class PortfolioTests(TestCase):
    def test_portfolio_create(self):
        img = PortfolioImage.objects.create(title='Фото', category='manicure', is_published=True)
        self.assertTrue(img.is_published)
