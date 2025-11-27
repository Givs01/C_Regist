from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Participant
from django.db.models import Count
from .models import UsersData, Participant



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
            messages.error(request, "QR Code not received!")
            return redirect("qr_register")

        # Check if qr_code is numeric
        if not qr_code.isdigit():
            messages.error(request, "Invalid QR Code format!")
            return redirect("qr_register")

        try:
            participant = Participant.objects.get(id=int(qr_code))
            messages.success(request, f"{participant.name} - registered successfully!")
        except Participant.DoesNotExist:
            messages.error(request, "Participant not found for this QR code!")

        return redirect("qr_register")

    return render(request, "qr_form.html")



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
