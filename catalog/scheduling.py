from datetime import datetime, time, timedelta, date
from django.utils import timezone
from .models import (
    WorkingSchedule, ScheduleException, PersonalEvent, Booking, DayPlan,
    CalendarSettings, RecurringBusy,
)


def intervals_overlap(start1, end1, start2, end2):
    return start1 < end2 and start2 < end1


def get_calendar_settings():
    cs, _ = CalendarSettings.objects.get_or_create(pk=1)
    return cs


def is_dispatch_duty(target_date):
    cs = get_calendar_settings()
    if not cs or not cs.dispatch_cycle_start:
        return False
    delta = (target_date - cs.dispatch_cycle_start).days
    if delta < 0:
        return False
    cycle = cs.dispatch_cycle_length or 4
    return (delta % cycle) == 0


def is_auto_cycle_exception(exc):
    """True for exceptions generated automatically from the dispatch duty cycle."""
    if exc is None:
        return False
    reason = (getattr(exc, "reason", "") or "").lower()
    return "сутки через трое" in reason



def get_working_interval(target_date):
    # Manual exception has priority
    try:
        exc = ScheduleException.objects.get(date=target_date)
        if is_auto_cycle_exception(exc):
            raise ScheduleException.DoesNotExist

        if not exc.is_working:
            return None
        if exc.start_time and exc.end_time:
            start_t = exc.start_time
            end_t = exc.end_time
        else:
            return None
        start_dt = timezone.make_aware(datetime.combine(target_date, start_t))
        end_dt = timezone.make_aware(datetime.combine(target_date, end_t))
        if end_dt <= start_dt:
            return None
        return start_dt, end_dt
    except ScheduleException.DoesNotExist:
        pass
    # Dispatch duty closes the salon day
    if is_dispatch_duty(target_date):
        return None
    try:
        ws = WorkingSchedule.objects.get(day_of_week=target_date.weekday())
    except WorkingSchedule.DoesNotExist:
        return None
    if not ws.is_working or not ws.start_time or not ws.end_time:
        return None
    start_dt = timezone.make_aware(datetime.combine(target_date, ws.start_time))
    end_dt = timezone.make_aware(datetime.combine(target_date, ws.end_time))
    if end_dt <= start_dt:
        return None
    return start_dt, end_dt


def conflicting_bookings(start, end, exclude_booking_id=None):
    qs = Booking.objects.filter(status__in=["confirmed", "proposed"])
    if exclude_booking_id:
        qs = qs.exclude(id=exclude_booking_id)
    conflicts = []
    for b in qs:
        b_start = b.confirmed_start or b.desired_datetime
        b_end = b.confirmed_end or (b_start + timedelta(minutes=b.duration_minutes + b.travel_time_minutes))
        # 30 минут на сборы после визита
        b_end = b_end + timedelta(minutes=30)
        if intervals_overlap(start, end, b_start, b_end):
            conflicts.append(b)
    return conflicts


def recurring_busy_intervals(target_date):
    result = []
    for r in RecurringBusy.objects.filter(weekday=target_date.weekday(), is_active=True):
        if r.active_from and target_date < r.active_from:
            continue
        try:
            base_start = timezone.make_aware(datetime.combine(target_date, r.start_time))
            base_end = timezone.make_aware(datetime.combine(target_date, r.end_time))
        except Exception:
            continue
        busy_start = base_start - timedelta(minutes=r.buffer_before_minutes or 0)
        busy_end = base_end + timedelta(minutes=r.buffer_after_minutes or 0)
        result.append((busy_start, busy_end))
    return result


def conflicting_recurring(start, end, target_date):
    for bs, be in recurring_busy_intervals(target_date):
        if intervals_overlap(start, end, bs, be):
            return True
    return False


def is_slot_available(start, end, exclude_booking_id=None):
    wi = get_working_interval(start.date())
    if wi is None:
        return False
    w_start, w_end = wi
    if start < w_start or end > w_end:
        return False
    if conflicting_bookings(start, end, exclude_booking_id):
        return False
    if conflicting_events(start, end):
        return False
    if conflicting_recurring(start, end, start.date()):
        return False
    return True


def conflicting_events(start, end):
    qs = PersonalEvent.objects.filter(start_datetime__lt=end, end_datetime__gt=start)
    return list(qs)


def is_slot_available(start, end, exclude_booking_id=None):
    wi = get_working_interval(start.date())
    if wi is None:
        return False
    w_start, w_end = wi
    if start < w_start or end > w_end:
        return False
    if conflicting_bookings(start, end, exclude_booking_id):
        return False
    if conflicting_events(start, end):
        return False
    return True


def available_slots(target_date, duration_minutes, travel_minutes=0, step_minutes=15):
    wi = get_working_interval(target_date)
    if wi is None:
        return []
    w_start, w_end = wi
    slots = []
    current = w_start
    while current + timedelta(minutes=duration_minutes) <= w_end:
        end = current + timedelta(minutes=duration_minutes)
        if is_slot_available(current, end):
            slots.append(current)
        current += timedelta(minutes=step_minutes)
    return slots