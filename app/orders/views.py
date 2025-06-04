from rest_framework import viewsets
from .models import Order, Order_Item
from .serializers import OrderSerializer, Order_ItemSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOrderOwner, IsOrder_Item_Owner

from django.conf import settings
import stripe
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
import time




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

            # 4. Mark the order as paid
            order.is_paid = True
            order.save()

            return Response({"status": "success", "payment_intent": intent.id})
        except Exception as e:
            return Response({"error": str(e)}, status=400)