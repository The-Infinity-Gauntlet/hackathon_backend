from django.urls import path
from core.donation.presentation.views import paymentPix, paymentCard, paymentTicket, savedCard, createWebhook, getStatus

urlpatterns = [
    path("card/", paymentCard),
    path("pix/", paymentPix),
    path("ticket/", paymentTicket),
    path("saved/", savedCard),
    path("webhook/", createWebhook),
    path("status/<str:payment_id>/", getStatus), 
]