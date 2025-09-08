from django.urls import path
from core.donation.presentation.views import paymentPix, paymentCard, paymentTicket

urlpatterns = [
    path("card/", paymentCard),
    path("pix/", paymentPix),
    path("ticket/", paymentTicket)
]