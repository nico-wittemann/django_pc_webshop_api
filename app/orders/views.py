from rest_framework import viewsets
from .models import Order, Order_Item
from .serializers import OrderSerializer, Order_ItemSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOrderOwner, IsOrder_Item_Owner

#Payment
from django.conf import settings
import stripe
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
import time

#Webhook
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Order
from django.core.mail import send_mail




class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwner]
    ordering = ['created_at']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(user_id=self.request.user.id)


class Order_ItemViewSet(viewsets.ModelViewSet):
    queryset = Order_Item.objects.all()
    serializer_class = Order_ItemSerializer
    permission_classes = [IsAuthenticated, IsOrder_Item_Owner]
    ordering = ['id']



#Payment
stripe.api_key = settings.STRIPE_SECRET_KEY

class OrderPaymentViewSet(GenericViewSet):
    def create(self, request):
        data = request.data
        try:
            order_id = data.get("order_id")
            name = data.get("name")
            email = data.get("email")
            iban = data.get("iban")

            # 1. Retrieve the order from the database
            order = Order.objects.get(id=order_id, user=request.user)

            #
            # Prevent duplicate payment
            if order.is_paid:
                return Response({"error": "This order has already been paid."}, status=400)

            # 2. Create a SEPA Direct Debit PaymentMethod with Stripe
            payment_method = stripe.PaymentMethod.create(
                type="sepa_debit",
                sepa_debit={"iban": iban},
                billing_details={"name": name, "email": email}
            )

            # 3. Create a PaymentIntent using this PaymentMethod
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Amount in cents
                currency="eur",
                payment_method=payment_method.id,
                payment_method_types=["sepa_debit"],  # Restrict to SEPA Direct Debit only
                confirm=True,  # Immediately attempt to confirm the payment
                mandate_data={  # Provide SEPA Direct Debit mandate information
                    "customer_acceptance": {
                        "type": "offline",  # Customer accepted the mandate outside of Stripe
                        "accepted_at": int(time.time()),  # Current timestamp
                        "offline": {}
                    }
                }
            )
            # 4. Save the intent ID to the order
            order.payment_intent_id = intent.id
            order.payment_status = "pending"
            order.save()

            return Response({"status": "success", "payment_intent": intent.id})
        except Exception as e:
            return Response({"error": str(e)}, status=400)



#Webhook
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)  # Invalid payload
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)  # Invalid signature

    print(f"✅ Event received: {event['type']}")

    #  Handle successful payment
    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        intent_id = intent["id"]

        try:
            order = Order.objects.get(payment_intent_id=intent_id)
            order.is_paid = True
            order.payment_status = "succeeded"
            order.save()
            print(f"✅ Order {order.id} marked as paid via webhook.")

            #  Send confirmation email
            send_mail(
                subject="Payment received – Thank you!",
                message=(
                    f"Hi {order.user.username},\n\n"
                    f"we have received your payment for Order #{order.id}.\n"
                    f"Total: {order.total_price} {order.currency}\n\n"
                    "Thank you for your purchase!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                fail_silently=False,
            )
            print(f"📧 Confirmation email sent to {order.user.email}")

        except Order.DoesNotExist:
            print(f"⚠️ No order found with intent_id {intent_id}")

    return HttpResponse(status=200)