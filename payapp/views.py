from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import UserDetails
from django.db import transaction
from .forms import PaymentForm
from .models import Transaction, PaymentRequest
from django.utils.timezone import now

# Home page view
@login_required(login_url='/webapps2025/login/')
def home(request):
    # Get all users excluding the logged-in user and admins
    users = UserDetails.objects.select_related('user').filter(
        user__is_superuser=False
    ).exclude(user=request.user)

    user_details = UserDetails.objects.get(user=request.user)

    # transactions related to the logged-in user
    transactions = Transaction.objects.filter(
        sender=request.user
    ) | Transaction.objects.filter(
        receiver=request.user
    )
    received_requests = PaymentRequest.objects.filter(receiver=request.user, status='pending')

    #  all payment requests
    payment_requests = PaymentRequest.objects.filter(receiver=request.user)

    return render(request, 'payapp/home.html', {
        # pass values to template
        'users': users,
        'user_balance': user_details.balance,
        'user_currency': user_details.currency,
        'transactions': transactions,
        'payment_requests': payment_requests,
    })

# payment view
@login_required
def make_payment(request, user_id):
    receiver_details = get_object_or_404(UserDetails, user__id=user_id)  #  UserDetails of receiver
    sender_details = get_object_or_404(UserDetails, user=request.user)  #UserDetails of sender

    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            if sender_details.balance < amount:
                messages.error(request, "Insufficient balance!")
            else:
                try:
                    with transaction.atomic():
                        sender_details.balance -= amount
                        receiver_details.balance += amount
                        sender_details.save()
                        receiver_details.save()


                        Transaction.objects.create(
                            sender=sender_details.user,
                            receiver=receiver_details.user,
                            amount=amount,
                            timestamp=now()
                        )


                    messages.success(request, f"Payment of £{amount} sent to {receiver_details.user.first_name}!")
                    return redirect('home')

                except Exception as e:

                    messages.error(request, f"An error occurred: {e}")

    else:
        form = PaymentForm()

    return render(request, 'payapp/make_payment.html', {'form': form, 'receiver': receiver_details})

# Request payment view
@login_required
def request_payment(request, user_id):
    receiver_details = get_object_or_404(UserDetails, user__id=user_id)  # UserDetails of receiver
    sender_details = get_object_or_404(UserDetails, user=request.user)  # UserDetails of sender

    #check
    if PaymentRequest.objects.filter(sender=request.user, receiver=receiver_details.user, status='pending').exists():
        messages.error(request, "Payment request already sent.")
        return redirect('home')


    if request.method == "POST":
        amount = request.POST.get('amount')


        payment_request = PaymentRequest.objects.create(
            sender=sender_details.user,
            receiver=receiver_details.user,
            amount=amount,
            currency=sender_details.currency,
            status='pending',
        )
        messages.success(request, f"Payment request of £{amount} sent to {receiver_details.user.first_name}!")
        return redirect('home')

    return render(request, 'payapp/request_payment.html', {'receiver': receiver_details})

# Accept payment view
@login_required
def accept_payment(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id, receiver=request.user, status='pending')

    sender_details = UserDetails.objects.get(user=payment_request.sender)
    receiver_details = UserDetails.objects.get(user=request.user)


    sender_details.balance -= payment_request.amount
    receiver_details.balance += payment_request.amount
    sender_details.save()
    receiver_details.save()


    transaction = Transaction.objects.create(
        sender=payment_request.sender,
        receiver=payment_request.receiver,
        amount=payment_request.amount,
        currency=payment_request.currency,
        timestamp=now(),
    )


    payment_request.status = 'accepted'
    payment_request.save()

    messages.success(request, f"Payment request of £{payment_request.amount} accepted.")
    return redirect('home')

# Reject payment view
@login_required
def reject_payment(request, request_id):
    payment_request = get_object_or_404(PaymentRequest, id=request_id, receiver=request.user, status='pending')


    payment_request.status = 'rejected'
    payment_request.save()

    messages.success(request, f"Payment request of £{payment_request.amount} rejected.")
    return redirect('home')


def handle_payment_request(request, request_id, action):
    payment_request = get_object_or_404(PaymentRequest, id=request_id)


    if request.user != payment_request.receiver:
        messages.error(request, "You are not authorized to perform this action.")
        return redirect('home')

    if action == "accept":

        payment_request.status = "accepted"
        payment_request.save()

        # Update balances
        sender_details = get_object_or_404(UserDetails, user=payment_request.sender)
        receiver_details = get_object_or_404(UserDetails, user=payment_request.receiver)

        if sender_details.balance >= payment_request.amount:
            sender_details.balance -= payment_request.amount
            receiver_details.balance += payment_request.amount
            sender_details.save()
            receiver_details.save()

            messages.success(request, f"You accepted the payment request of £{payment_request.amount}.")
        else:
            messages.error(request, "Sender does not have enough balance. Payment request cannot be processed.")

    elif action == "reject":
        payment_request.status = "rejected"
        payment_request.save()
        messages.info(request, "You rejected the payment request.")

    return redirect('home')