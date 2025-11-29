from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from .models import Participant, UsersData
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import PreRegistration, Participant, QRRegistration
import csv
import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import PreRegistration
import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from registration.models import Participant





# ----------------------------
# User Management Views
# ----------------------------

@login_required
@user_passes_test(lambda u: u.is_superuser)
def add_user(request):
    if request.method == "POST":
        name = request.POST.get("name")
        user_id = request.POST.get("userId")
        password = request.POST.get("password")
        assign_desk = request.POST.get("assignDesk")

        # Check for duplicate userId
        if UsersData.objects.filter(userId=user_id).exists():
            messages.error(request, "User ID already exists! Choose a different ID.")
            return redirect("add_user")

        UsersData.objects.create(
            name=name,
            userId=user_id,
            password=password,
            assignDesk=assign_desk
        )
        messages.success(request, "User created successfully!")
        return redirect("users_list")

    return render(request, "add_user.html")




@login_required
@user_passes_test(lambda u: u.is_superuser)
def users_list(request):
    """Display all users and handle updates/deletions (Admin only)."""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        
        if "update_desk" in request.POST:
            new_desk = request.POST.get("assignDesk")
            UsersData.objects.filter(id=user_id).update(assignDesk=new_desk)
            messages.success(request, "Desk updated successfully.")

        elif "update_password" in request.POST:
            new_pass = request.POST.get("password")
            if new_pass:
                hashed_pass = make_password(new_pass)
                UsersData.objects.filter(id=user_id).update(password=hashed_pass)
                messages.success(request, "Password updated successfully.")
            else:
                messages.error(request, "Password cannot be empty.")

        elif "delete_user" in request.POST:
            UsersData.objects.filter(id=user_id).delete()
            messages.success(request, "User deleted successfully.")
        
        return redirect("users_list")

    users = UsersData.objects.all().order_by("-created_at")
    return render(request, "users_list.html", {"users": users})



# ----------------------------
# Authentication Views
# ----------------------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")
        else:
            context['form_error'] = "Invalid username or password."

    return render(request, "login.html", context)


# ----------------------------
# Logout View
# ----------------------------
@login_required
def logout_view(request):
    """Logout the user."""
    logout(request)
    return redirect("login")



# ----------------------------
# Profile View
# ----------------------------
@login_required
def profile_view(request):

    # Admin → show admin profile page
    if request.user.is_superuser:
        return render(request, "admin_profile.html", {
            "is_admin": True,
            "user_obj": request.user,   # Django User table
        })

    # Get user data from UsersData table
    try:
        custom_user = UsersData.objects.get(userId=request.user.username)
        logged_desk = custom_user.assignDesk
    except UsersData.DoesNotExist:
        # Fallback if user not in UsersData table
        logged_desk = None

    # Normal User → show normal profile page
    return render(request, "profile.html", {
        "is_admin": False,
        "user_obj": request.user,    
        "logged_desk": logged_desk
    })



# ----------------------------
# Home View
# ----------------------------

@login_required
def home(request):
    if request.user.is_superuser:
        # Admin view
        desk_counts = UsersData.objects.values('assignDesk') \
            .annotate(count=Count('id')) \
            .order_by('assignDesk')

        total_users = UsersData.objects.count()
        last_three = UsersData.objects.all().order_by("-created_at")[:3]

        context = {
            'is_admin': True,
            'desk_counts': desk_counts,
            'total_users': total_users,
            'last_three': last_three
        }
        return render(request, 'admin_home.html', context)

    else:
        # Regular user view
        try:
            custom_user = UsersData.objects.get(userId=request.user.username)
            logged_desk = custom_user.assignDesk
        except UsersData.DoesNotExist:
            # Fallback if user not in UsersData table
            logged_desk = None

        my_data = UsersData.objects.filter(assignDesk=logged_desk).order_by('-created_at') if logged_desk else []

        context = {
            'is_admin': False,
            'desk_name': logged_desk,
            'my_data': my_data,
        }
        return render(request, 'index.html', context)





@login_required
def admin_reports(request):
    if not request.user.is_superuser:
        return render(request, login)

    # Summary counts
    total_regist = Participant.objects.count()
    qr_regist = Participant.objects.filter(mode='qr').count()
    onspot_regist = Participant.objects.filter(mode='onspot').count()

    # Full participant list
    participants = Participant.objects.all().order_by('-id')

    # CSV Export
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="participants.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Name', 'Email', 'Contact', 'QR Code', 'Mode',
            'Organisation', 'Country'
        ])

        for p in participants:
            writer.writerow([
                p.id, p.name, p.email, p.contact, p.qr_code, p.mode,
                p.organisation, p.country
            ])

        return response

    context = {
        'is_admin': True,
        'total_regist': total_regist,
        'qr_regist': qr_regist,
        'onspot_regist': onspot_regist,
        'participants': participants,
    }

    return render(request, 'admin_report.html', context)






# ----------------------------
# Onspot Registration View
# ----------------------------
@login_required
def onspot(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        organisation = request.POST.get("organisation")
        country = request.POST.get("country")
        contact = request.POST.get("contact")
        mode='onspot'

        # Check duplicate email
        if Participant.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, "onspot_form.html", {
                "name": name,
                "email": email,
                "organisation": organisation,
                "country": country,
                "contact": contact,
            })

        # Validate contact number (10 digits)
        if not contact.isdigit() or len(contact) != 10:
            messages.error(request, "Invalid mobile number!")
            return render(request, "onspot_form.html", {
                "name": name,
                "email": email,
                "organisation": organisation,
                "country": country,
                "contact_error": True,
            })


        try:
            custom_user = UsersData.objects.get(userId=request.user.username)
            desk = custom_user.assignDesk
        except UsersData.DoesNotExist:
            desk = None

        try:
            Participant.objects.create(
                name=name,
                email=email,
                contact=contact,
                organisation=organisation,
                country=country,
                registered_by=request.user,
                registration_desk=desk,
                mode=mode
            )
            messages.success(request, f"{name} - registered successfully!")
            return redirect("home")

        except IntegrityError:
            messages.error(request, "Failed to register participant. Try again!")
            # keep form values
            return render(request, "onspot_form.html", {
                "name": name,
                "email": email,
                "organisation": organisation,
                "country": country,
                "contact": contact,
                "contact_error": "Enter a valid 10-digit mobile number",
            })

    return render(request, "onspot_form.html")





# ----------------------------
# QR Registration View
# ----------------------------
@login_required
def qr(request):
    return render(request, "qr_form.html")





@login_required
def qr_register(request):
    if request.method == "POST":
        qr_code = request.POST.get("qr_code", "").strip()

        if not qr_code:
            messages.error(request, "QR Code not detected!")
            return redirect("qr")

        # Check QR exists in pre-registered list
        try:
            pre = PreRegistration.objects.get(qr_code=qr_code)
        except PreRegistration.DoesNotExist:
            messages.error(request, "QR not found! Please do On-Spot registration.")
            return redirect("onspot")

        # Prevent duplicate QR scan
        if Participant.objects.filter(email=pre.email).exists():
            messages.warning(request, f"{pre.name} already registered!")
            return redirect("qr")


        
        try:
            custom_user = UsersData.objects.get(userId=request.user.username)
            desk = custom_user.assignDesk
        except UsersData.DoesNotExist:
            desk = None

        # Log QR scan
        QRRegistration.objects.create(
            qr_code=qr_code,
            scanned_by=request.user,
            desk_name=desk,
            scanned_at=timezone.now()
        )

        # Add to main participants table
        Participant.objects.create(
            name=pre.name,
            email=pre.email,
            contact=pre.contact,
            organisation=pre.organisation,
            country=pre.country,
            registered_by=request.user,
            registration_desk=desk,
            mode="qr",
            qr_code=qr_code,
        )

        messages.success(request, f"Welcome {pre.name}! Registration completed.")
        return redirect("qr")

    return redirect("qr")




# ----------------------------
# my_Registration View
# ----------------------------
@login_required
def my_registrations(request):
    # Fetch all participants registered by the current user
    participants = Participant.objects.filter(registered_by=request.user).order_by('-timestamp')

    # Latest 3 registrations
    last_reg = participants[:5]

    # Counts
    onspot_counts = participants.filter(mode='onspot').count()
    qr_counts = participants.filter(mode='qr').count()


    context = {
        'last_reg': last_reg,
        'onspot_counts': onspot_counts,
        'qr_counts': qr_counts,
    }

    return render(request, 'my_registrations.html', context)



# ----------------------------
# csv upload
# ----------------------------

@login_required
def upload_prereg_csv(request):
    if request.method == "POST":
        csv_file = request.FILES.get("file")

        if not csv_file:
            messages.error(request, "Please upload a CSV file")
            return redirect("upload_prereg_csv")

        if not csv_file.name.endswith(".csv"):
            messages.error(request, "File must be CSV format")
            return redirect("upload_prereg_csv")

        try:
            data = csv_file.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(data))

            required_headers = {"qr_code", "name", "email", "contact", "organisation", "country"}
            if not required_headers.issubset(set(reader.fieldnames)):
                messages.error(request, "Invalid CSV headers!")
                return redirect("upload_prereg_csv")

            # Clear existing data
            PreRegistration.objects.all().delete()

            count = 0
            for row in reader:
                if not row["qr_code"].strip():
                    continue

                PreRegistration.objects.update_or_create(
                    qr_code=row["qr_code"].strip(),
                    defaults={
                        "name": row.get("name", "").strip(),
                        "email": row.get("email", "").strip(),
                        "contact": row.get("contact", "").strip(),
                        "organisation": row.get("organisation", "").strip(),
                        "country": row.get("country", "").strip() or "India",
                    }
                )
                count += 1

            messages.success(request, f"Successfully imported {count} preregistration records!")
            return redirect("upload_prereg_csv")

        except Exception as e:
            messages.error(request, f"Error reading CSV: {e}")
            return redirect("upload_prereg_csv")

    return render(request, "upload_prereg_csv.html")
