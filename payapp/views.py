
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import UserDetails
from .forms import PaymentForm
from .models import Transaction
from django.utils.timezone import now

# Home page view
@login_required(login_url='/webapps2025/login/')
def home(request):
    # Get all users excluding the logged-in user and admins
    users = UserDetails.objects.select_related('user').filter(
        user__is_superuser=False  # Exclude admins
    ).exclude(user=request.user)  # Exclude the logged-in user

    # Get the logged-in user's details
    user_details = UserDetails.objects.get(user=request.user)

    # Get the transactions related to the logged-in user (as sender or receiver)
    transactions = Transaction.objects.filter(
        sender=request.user
    ) | Transaction.objects.filter(
        receiver=request.user
    )

    return render(request, 'payapp/home.html', {
        'users': users,
        'user_balance': user_details.balance,  # Pass balance to template
        'user_currency': user_details.currency,  # Pass currency to template
        'transactions': transactions  # Pass transactions to template
    })


# Payment view
@login_required
def make_payment(request, user_id):
    receiver_details = get_object_or_404(UserDetails, user__id=user_id)  # Get UserDetails of receiver
    sender_details = get_object_or_404(UserDetails, user=request.user)  # Get UserDetails of sender

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            if sender_details.balance < amount:
                messages.error(request, "Insufficient balance!")
            else:
                # Deduct and add balance
                sender_details.balance -= amount
                receiver_details.balance += amount
                sender_details.save()
                receiver_details.save()

                # Store the transaction in the Transaction model
                transaction = Transaction.objects.create(
                    sender=sender_details.user,  # Extract User instance
                    receiver=receiver_details.user,  # Extract User instance
                    amount=amount,
                    timestamp=now()
                )

                messages.success(request, f"Payment of £{amount} sent to {receiver_details.user.first_name}!")
                return redirect('home')
    else:
        form = PaymentForm()

    return render(request, 'payapp/make_payment.html', {'form': form, 'receiver': receiver_details})
