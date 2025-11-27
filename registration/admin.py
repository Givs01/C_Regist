from django.contrib import admin
from .models import UsersData, Participant


@admin.register(UsersData)
class UsersDataAdmin(admin.ModelAdmin):
    list_display = ("name", "userId", "assignDesk", "created_at")
    search_fields = ("name", "userId", "assignDesk")
    list_filter = ("assignDesk",)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "contact", "organisation", "country", "mode", "registered_by", "registration_desk", "timestamp")
    search_fields = ("name", "email", "contact")
    list_filter = ("registration_desk", "registered_by")
