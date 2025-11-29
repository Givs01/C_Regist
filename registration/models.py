from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# ----------------------------
# User Management
# ----------------------------

class UsersData(models.Model):
    name = models.CharField(max_length=100)
    userId = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    assignDesk = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)

        super().save(*args, **kwargs)
        if not User.objects.filter(username=self.userId).exists():
            User.objects.create(
                username=self.userId,
                first_name=self.name,
                password=self.password,
                is_active=True,
            )



# ----------------------------
# QR Scan
# ----------------------------
class QRRegistration(models.Model):
    qr_code = models.CharField(max_length=100, unique=True)

    scanned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="qr_scans"
    )
    scanned_at = models.DateTimeField(auto_now_add=True)

    desk_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.qr_code} scanned by {self.scanned_by}"

        


# ----------------------------
# On-spot Registration
# ----------------------------

class Participant(models.Model):
    qr_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    organisation = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")

    # Who registered this participant
    registered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="registered_participants"
    )

    # User must have desk attribute
    registration_desk = models.CharField(max_length=100, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    mode = models.CharField(max_length=20, default="onspot")

    def __str__(self):
        return f"{self.name} - {self.email}"





# ----------------------------
# Pre-Registration
# ----------------------------

class PreRegistration(models.Model):
    qr_code = models.CharField(max_length=100, unique=True)

    name = models.CharField(max_length=150)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    organisation = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=100, default="India")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.qr_code}"
