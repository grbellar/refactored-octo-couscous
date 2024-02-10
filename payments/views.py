from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from accounts.models import CustomUser
import stripe
import pprint
from dotenv import load_dotenv
from base.settings import BASE_DIR
import os

load_dotenv(BASE_DIR / '.env')

#TODO: Add prod key to env variables on render.
# This is your test secret API key.
stripe.api_key = os.getenv('STRIPE_TEST_KEY')
endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')

#TODO: Need to add redirect urls for production
@require_http_methods(["POST"])
def create_checkout_session(request):

    if request.user.is_authenticated:
        current_user = request.user

    if request.method == 'POST':
        price_id = request.POST.get('price-id')
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Passing in product price id from get access buy view
                    'price': price_id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url="http://127.0.0.1:3000/my-exams",
            cancel_url="http://127.0.0.1:3000/get-access/buy",
            metadata = {
                "perf_user_id": current_user.id
            }
        )

        return redirect(checkout_session.url, code=303)

@csrf_exempt
@require_http_methods(["POST"])
def payments_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    # Verify post event came from Stripe
    #TODO: I don't think this is working correctly. This should return a 400 response but instead returns 500 when I 
    #       try to post to the endpoint using curl. See Stripe docs on how to test fulfillment endpoint.
    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, endpoint_secret
    )
    except ValueError as e:
    # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
    # Invalid signature
        return HttpResponse(status=400)

     # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session 
        session = stripe.checkout.Session.retrieve(
        event['data']['object']['id']
        )
        # Update user has paid attribute
        pprint.pprint(session)
        update_user_paid(session)

    return HttpResponse(status=200)

def update_user_paid(stripe_session):
    paid_user_id = stripe_session['metadata']['perf_user_id']
    perf_user = CustomUser.objects.get(
        id=paid_user_id
    )
    print(perf_user)
    print(perf_user.has_paid)

    perf_user.has_paid = True
    perf_user.save()

    print(perf_user.has_paid)
