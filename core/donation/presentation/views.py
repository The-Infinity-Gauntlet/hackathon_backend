from core.donation.infra.repository import MercadoPagoRepository
from core.donation.app.services import DonationService
from core.donation.domain.entities import Payment
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import json

repo = MercadoPagoRepository()
service = DonationService(repository=repo)

@csrf_exempt
def paymentPix(request):
    if request.method == "POST":
        data = json.loads()
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            description=data.get("description"),
            payment_method_id=data.get("payment_method_id"),
            email=data["payer"]["email"],
            identification_number=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"]
        )
        result = service.pay_with_pix(payment)
        return JsonResponse(result, safe=False)
    return JsonResponse({"error": "Method not allowed"})

@csrf_exempt
def paymentCard(request):
    if request.method == "POST":
        data = json.loads()
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            token=data.get("token"),
            description=data.get("description"),
            installments=data.get("installments"),
            payment_method_id=data.get("payment_method_id"),
            issuer_id=data.get("issuer_id"),
            email=data["payer"]["email"],
            identification_number=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"]
        )
        result = service.pay_with_card(payment)
        return JsonResponse(result, safe=False)
    return JsonResponse({"error": "Method not allowed"})

@csrf_exempt
def paymentTicket(request):
    if request.method == "POST":
        data = json.loads()
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            description=data.get("description"),
            payment_method_id=data.get("payment_method_id"),
            email=data["payer"]["email"],
            identification_number=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"],
            address_id=["address_id"]
        )
        result = service.pay_with_pix(payment)
        return JsonResponse(result, safe=False)
    return JsonResponse({"error": "Method not allowed"})