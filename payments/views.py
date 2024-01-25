from django.shortcuts import render, redirect, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import stripe
import pprint

# This is your test secret API key.
stripe.api_key = 'sk_test_51OT4uxHnSCQ3O7d7AX4KozRzbMi7RFflkA2v9tIPaGbNThCvnZv4Ag9h3or4cCRUTRT8ZUCFivmq7nQzncDDRIEi00cslL5ZBD'
endpoint_secret = 'whsec_8ec6f3cdfb97458a49a38aabbc3b9ceb8042f718fba0953cb1646848fb08d82a'

@require_http_methods(["POST"])
def create_checkout_session(request):

    checkout_session = stripe.checkout.Session.create(
        line_items=[
            {
                # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                'price': 'price_1OT56jHnSCQ3O7d7brxHhRJn',
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url="http://127.0.0.1:3000/",
        cancel_url="http://127.0.0.1:3000/",
        metadata = {
            "perf_user_id": "XXX2007"
        }
    )

    return redirect(checkout_session.url, code=303)

@csrf_exempt
def payments_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    #TODO: This is where I can pull the meta i added to the checkout session and update Users paid status in my Database!! :):)


    # verify post event came from Stripe
    #TODO: I don't think this is working correctly. This should return a 400 response but instead returns 500 when I 
    # try to post to the endpoint using curl. See Stripe docs on how to test fulfilment endpoint.
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

    pprint.pprint(payload)

    return HttpResponse(status=200)