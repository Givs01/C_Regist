from django.contrib import admin
from .models import UsersData, Participant, PreRegistration, QRRegistration


@admin.register(UsersData)
class UsersDataAdmin(admin.ModelAdmin):
    list_display = ("name", "userId", "assignDesk", "created_at")
    search_fields = ("name", "userId", "assignDesk")
    list_filter = ("assignDesk",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("qr_code", "name", "email", "contact", "organisation", "country", "mode", "registered_by", "registration_desk", "timestamp")
    search_fields = ("name", "email", "contact")
    list_filter = ("registration_desk", "registered_by")


@admin.register(PreRegistration)
class PreRegistrationAdmin(admin.ModelAdmin):
    list_display = ("qr_code", "name", "email", "contact", "organisation", "country", "updated_at")
    search_fields = ("qr_code", "name", "email", "contact")
    list_filter = ("country",)
    ordering = ("qr_code",)


@admin.register(QRRegistration)
class QRRegistrationAdmin(admin.ModelAdmin):
    list_display = ("qr_code", "scanned_by", "desk_name", "scanned_at")
    search_fields = ("qr_code", "scanned_by__username")

