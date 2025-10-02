from django.shortcuts import render, redirect
from django.contrib.auth import login,logout, authenticate
from django.contrib import messages
from .models import UserDetails
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import user_passes_test
from .forms import AdminRegistrationForm,RegistrationForm
from payapp.models import Transaction
import requests
from decimal import Decimal
from payapp.views import home

#admin1
#admin1


# CR7
# Cr7@12345

# LM10
# Lm10@12345

#KDB
#Kevin@12345





# User Login view
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



BASE_CURRENCY = "GBP"  # Default base currency
INITIAL_BALANCE = 1000  # Default balance, Welcome bonus!

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            currency = form.cleaned_data['currency']

            # Calling currency conversion REST API
            conversion_url = f"http://127.0.0.1:8000/webapps2025/conversion/{BASE_CURRENCY}/{currency}/{INITIAL_BALANCE}/"
            try:
                response = requests.get(conversion_url)

                if response.status_code == 200:
                    json_response = response.json()

                    converted_balance = json_response.get('converted_amount', INITIAL_BALANCE)

                    converted_balance = Decimal(str(converted_balance))

                else:

                    converted_balance = INITIAL_BALANCE  # default balance in case of API error

            except requests.RequestException as e:
                converted_balance = INITIAL_BALANCE  # setting back to default balance amount

            user_details, created = UserDetails.objects.get_or_create(user=user)
            user_details.currency = currency
            user_details.balance = converted_balance
            user_details.save(force_update=True)



            login(request, user)

            return redirect('home')

        else:
            print("❌ Form is invalid:", form.errors)

    else:
        form = RegistrationForm()

    return render(request, 'register/Register.html', {'form': form})
# Logout view
def logout_view(request):
    print(f"Logging out user: {request.user.username} (Session ID: {request.session.session_key})")

    logout(request)
    messages.success(request, 'You have successfully logged out.')


    return redirect('login')

# Admin register view
@user_passes_test(lambda u: u.is_superuser)
def register_admin(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New administrator created successfully.')
            return redirect('admin:index')
        else:
            messages.error(request, 'There was an error creating the administrator.')
    else:
        form = AdminRegistrationForm()

    return render(request, 'register/admin_register.html', {'form': form})

# Admin login view
def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, 'register/admin_login.html')

def is_admin(user):
    return user.is_superuser

# Admin dashboard view
@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.all().order_by('-date_joined')
    transactions = Transaction.objects.all().order_by('-timestamp')
    user_balances = {user.id: get_user_balance(user) for user in users}

    return render(request, 'register/admin_dashboard.html', {'users': users,
                                                             'transactions': transactions,
                                                             'user_balances': user_balances })

# Admin register view
@user_passes_test(is_admin)  # Only admins can access
def admin_register_view(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New administrator created successfully.')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Error creating administrator.')
    else:
        form = AdminRegistrationForm()

    return render(request, 'register/admin_register.html', {'form': form})


def get_user_balance(user):
    try:
        user_details = UserDetails.objects.get(user=user)
        return user_details.balance
    except UserDetails.DoesNotExist:
        return None