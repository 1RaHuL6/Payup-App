from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from register.models import UserDetails
from django.db import transaction
from .forms import PaymentForm
from .models import Transaction, PaymentRequest
from decimal import Decimal
import requests
from .thrift_client import get_timestamp_from_thrift




from django.shortcuts import render
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

    # Debugging: print the logged-in user's ID and the receiver's ID in the database
    print("Logged-in user ID:", request.user.id)

    # Get all pending payment requests where the receiver is the logged-in user and is unread (is_read=False)
    pending_requests = PaymentRequest.objects.filter(
        receiver=request.user, status='pending', is_read=False
    )

    # Debugging: print the pending requests to see if any are fetched
    print("Pending requests:", pending_requests)

    return render(request, 'payapp/home.html', {
        'users': users,
        'user_balance': user_details.balance,
        'user_currency': user_details.currency,
        'transactions': transactions,
        'pending_requests': pending_requests,
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
        with transaction.atomic():
            # Get receiver's UserDetails and User object
            receiver_details = get_object_or_404(UserDetails, user__id=user_id)
            receiver = receiver_details.user
            sender = request.user

            if request.method == 'POST':
                amount = request.POST.get('amount')
                currency = receiver_details.currency



                # Basic validation
                if not amount or float(amount) <= 0:
                    messages.error(request, "Invalid amount entered.")
                    return redirect('request_payment', user_id=user_id)

                # Prevent duplicate pending requests
                if PaymentRequest.objects.filter(sender=sender, receiver=receiver, status='pending').exists():
                    messages.error(request, "Payment request already sent.")
                    return redirect('home')


                PaymentRequest.objects.create(
                    sender=sender,
                    receiver=receiver,
                    amount=amount,
                    currency=currency,
                )

                messages.success(request, f"Payment request of {currency}{amount} sent to {receiver.first_name}!")
                return redirect('home')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

    return render(request, 'payapp/request_payment.html', {'receiver': receiver_details})

# Accept payment
@login_required
def accept_request(request, request_id):
    try:
        # Fetch the payment request, but don't change its status yet
        payment_request = get_object_or_404(PaymentRequest, id=request_id, receiver=request.user, status='pending')

        # Process the payment as usual
        receiver_details = get_object_or_404(UserDetails, user=request.user)
        sender_details = get_object_or_404(UserDetails, user=payment_request.sender)

        if request.method == "POST":
            form = PaymentForm(request.POST)
            if form.is_valid():
                amount = form.cleaned_data['amount']

                if sender_details.balance < amount:
                    messages.error(request, "Insufficient balance!")
                    return redirect('make_payment', user_id=payment_request.sender.id)
                else:
                    try:
                        with transaction.atomic():
                            # Currency conversion logic
                            conversion_url = f"http://127.0.0.1:8000/webapps2025/conversion/{sender_details.currency}/{receiver_details.currency}/{amount}/"
                            response = requests.get(conversion_url)

                            if response.status_code == 200:
                                json_response = response.json()
                                converted_amount = Decimal(str(json_response.get('converted_amount', amount)))
                            else:
                                messages.error(request, f"Currency conversion failed: {response.text}")
                                return redirect('home')

                            # Update sender and receiver balances
                            sender_details.balance -= amount
                            sender_details.save()

                            receiver_details.balance += converted_amount
                            receiver_details.save()

                            # Create transaction entry
                            timestamp = get_timestamp_from_thrift()
                            Transaction.objects.create(
                                sender=sender_details.user,
                                receiver=receiver_details.user,
                                amount=converted_amount,
                                currency=receiver_details.currency,
                                timestamp=timestamp
                            )

                        # After successful payment, change the payment request status to 'accepted'
                        payment_request.status = 'accepted'
                        payment_request.is_read = True
                        payment_request.save()

                        # Success message
                        messages.success(request, f"Payment of £{amount} sent to {receiver_details.user.first_name}!")
                        return redirect('home')

                    except Exception as e:
                        messages.error(request, f"An error occurred: {e}")
        else:
            form = PaymentForm()

        return render(request, 'payapp/make_payment.html', {'form': form, 'receiver': receiver_details})

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')



# Reject payment
@login_required
def reject_request(request, request_id):
    try:
        payment_request = get_object_or_404(PaymentRequest, id=request_id, receiver=request.user, status='pending')

        # Mark as rejected and read
        payment_request.status = 'rejected'
        payment_request.is_read = True
        payment_request.save()

        messages.success(request, f"Payment request from {payment_request.sender.username} has been rejected.")
        return redirect('home')

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')