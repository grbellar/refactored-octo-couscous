from django.shortcuts import redirect, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from accounts.models import CustomUser
import stripe
from dotenv import load_dotenv
from base.settings import BASE_DIR
import os

load_dotenv(BASE_DIR / '.env')

stripe.api_key = os.getenv('STRIPE_KEY')
endpoint_secret = os.getenv('STRIPE_ENDPOINT_SECRET')

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
            allow_promotion_codes=True,
            success_url=os.getenv('SUCCESS_URL'),
            cancel_url=os.getenv('CANCEL_URL'),
            metadata = {
                "perf_user_uuid": current_user.uuid,
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
        event['data']['object']['id'],
        expand=['line_items'],
        )
        # Update user has paid v2 attribute
        update_has_paid(session)

    return HttpResponse(status=200)


def update_has_paid(stripe_session):
    paid_user_uuid = stripe_session['metadata']['perf_user_uuid']
    perf_user = CustomUser.objects.get(
        uuid=paid_user_uuid
    )
    #TODO: Need to disable get accesss buy page once a user has paid. If they can't 
    # get to the page anymore than it shouldn't be necessary to  have this check. (I'm 
    # not sure it's stricly necessary even if they can get to the buy page.)
    if perf_user.has_paid_v2 != True: # Only try to update this first time through
        perf_user.has_paid_v2 = True
        perf_user.save()
