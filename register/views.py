from django.shortcuts import render, redirect
from django.contrib.auth import login,logout
from django.contrib import messages
from .forms import RegistrationForm
from .models import UserDetails
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required


# Home view
@login_required
def home(request):
    return render(request, 'register/home.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials, try again.')
    else:
        form = AuthenticationForm()

    return render(request, 'register/login.html', {'form': form})

# Register view
def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            currency = form.cleaned_data['currency']

            # For Debugging
            print(f"Form is valid. User created: {user.username}, Currency: {currency}")

            # Handle UserDetails creation or update
            if not UserDetails.objects.filter(user=user).exists():
                UserDetails.objects.create(user=user, currency=currency)
                # For Debugging
                print(f"UserDetails created for {user.username}")
            else:
                user_details = UserDetails.objects.get(user=user)
                user_details.currency = currency
                user_details.save()
                # For Debugging
                print(f"UserDetails updated for {user.username}")

            # Log in user
            login(request, user)
            # For Debugging
            print(f"User {user.username} logged in successfully.")

            # Redirect to the home page
            return redirect('home')
        else:
            # For Debugging
            print("Form is invalid:", form.errors)
    else:
        form = RegistrationForm()

    return render(request, 'register/register.html', {'form': form})

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('login')