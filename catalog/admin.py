from django.contrib import admin
from .models import (
    Profile, Client, Service, Image, Comment, Booking,
    WorkingSchedule, ScheduleException, DayPlan, PersonalEvent,
    Review, PortfolioImage, PortfolioImageReaction,
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "district", "location")
    search_fields = ("user__username", "phone", "district", "location")


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "duration_minutes", "is_active", "updated_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "description")


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "services", "author", "created_at")
    search_fields = ("content",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "service", "status", "desired_datetime", "confirmed_start", "confirmed_end")
    list_filter = ("status", "service__category")
    search_fields = ("client__username", "service__title", "client_district")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WorkingSchedule)
class WorkingScheduleAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "is_working", "start_time", "end_time")


@admin.register(ScheduleException)
class ScheduleExceptionAdmin(admin.ModelAdmin):
    list_display = ("date", "is_working", "start_time", "end_time", "reason")
    search_fields = ("reason",)


@admin.register(DayPlan)
class DayPlanAdmin(admin.ModelAdmin):
    list_display = ("date", "start_time", "start_location")


@admin.register(PersonalEvent)
class PersonalEventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "start_datetime", "end_datetime")
    list_filter = ("event_type",)
    search_fields = ("title", "comment")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "service", "rating", "status", "likes_count", "dislikes_count", "created_at")
    list_filter = ("status", "rating")
    search_fields = ("text", "client__username")

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = "Лайки"

    def dislikes_count(self, obj):
        return obj.dislikes.count()
    dislikes_count.short_description = "Дизлайки"


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "is_published", "created_at")
    list_filter = ("category", "is_published")
    search_fields = ("title", "description")


@admin.register(PortfolioImageReaction)
class PortfolioImageReactionAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "user", "reaction", "created_at")
    list_filter = ("reaction", "created_at")
    search_fields = ("user__username",)
