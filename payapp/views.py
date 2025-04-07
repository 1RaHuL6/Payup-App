from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import UserDetails
from django.db import transaction
from .forms import PaymentForm
from .models import Transaction, PaymentRequest, Notification
from django.utils.timezone import now
from decimal import Decimal
import requests
from .thrift_client import get_timestamp_from_thrift
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
    notifications = Notification.objects.filter(receiver=request.user, is_read=False).order_by('-timestamp')

    return render(request, 'payapp/home.html', {
        # pass values to template
        'users': users,
        'user_balance': user_details.balance,
        'user_currency': user_details.currency,
        'transactions': transactions,
        'payment_requests': payment_requests,
        'notifications': notifications,
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
                        #get converted amount
                        conversion_url = f"http://127.0.0.1:8000/webapps2025/conversion/{sender_details.currency}/{receiver_details.currency}/{amount}/"
                        response = requests.get(conversion_url)

                        if response.status_code == 200:
                            json_response = response.json()
                            converted_amount = Decimal(str(json_response.get('converted_amount', amount)))


                        else:
                            messages.error(request, f"Currency conversion failed: {response.text}")
                            return redirect('home')

                        sender_details.balance -= amount
                        sender_details.save()

                       #use converted amount to add balance
                        receiver_details.balance += converted_amount
                        receiver_details.save()

                        timestamp = get_timestamp_from_thrift()

                        Transaction.objects.create(
                            sender=sender_details.user,
                            receiver=receiver_details.user,
                            amount=converted_amount,
                            currency=receiver_details.currency,
                            timestamp=timestamp
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
    try:
        # Wrap in a try-except to catch where recursion might happen
        with transaction.atomic():
            receiver_details = get_object_or_404(UserDetails, user__id=user_id)
            sender_details = get_object_or_404(UserDetails, user=request.user)

            # Check if a pending request already exists
            if PaymentRequest.objects.filter(sender=request.user, receiver=receiver_details.user, status='pending').exists():
                messages.error(request, "Payment request already sent.")
                return redirect('home')

            if request.method == "POST":
                amount = request.POST.get('amount')

                # Create a payment request
                payment_request = PaymentRequest.objects.create(
                    sender=sender_details.user,
                    receiver=receiver_details.user,
                    amount=amount,
                    currency=sender_details.currency,
                    status='pending',
                )

                # Create a notification for the receiver
                Notification.objects.create(
                    receiver=receiver_details.user,
                    sender=sender_details.user,
                    payment_request=payment_request,
                    message=f"You have a new payment request of {sender_details.currency}{amount} from {sender_details.user.first_name}.",
                )

                messages.success(request, f"Payment request of {sender_details.currency}{amount} sent to {receiver_details.user.first_name}!")
                return redirect('home')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

    return render(request, 'payapp/request_payment.html', {'receiver': receiver_details})



@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    notification.is_read = True
    notification.save()
    return redirect('home')


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


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.receiver == request.user:  # Make sure the logged-in user is the receiver
        notification.is_read = True
        notification.save()

    return redirect('home')  # Redirect back to the home page