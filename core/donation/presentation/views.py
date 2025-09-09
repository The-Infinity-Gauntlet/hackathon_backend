from core.donation.infra.repository import MercadoPagoRepository
from core.donation.app.services import DonationService
from core.donation.domain.entities import Payment, Card
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
import json

repo = MercadoPagoRepository()
service = DonationService(repository=repo)

@csrf_exempt
def paymentPix(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            description=data.get("description"),
            payment_method_id=data.get("payment_method_id"),
            email=data["payer"]["email"],
            identification_type=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"]
        )
        result = service.pay_with_pix(payment)
        return result
    return JsonResponse({"error": "Method not allowed"})

@csrf_exempt
def paymentCard(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            token=data.get("token"),
            description=data.get("description"),
            installments=data.get("installments"),
            payment_method_id=data.get("payment_method_id"),
            issuer_id=data.get("issuer_id"),
            email=data["payer"]["email"],
            identification_type=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"]
        )
        result = service.pay_with_card(payment)
        return result
    return JsonResponse({"error": "Method not allowed"})

@csrf_exempt
def paymentTicket(request):
    if request.method == "POST":
        data = json.loads(request.body)
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            description=data.get("description"),
            payment_method_id=data.get("payment_method_id"),
            email=data["payer"]["email"],
            first_name=data["payer"]["first_name"],
            last_name=data["payer"]["last_name"],
            identification_type=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"],
            zip_code=data["payer"]["address"]["zip_code"],
            street_name=data["payer"]["address"]["street_name"],
            street_number=data["payer"]["address"]["street_number"],
            neighborhood=data["payer"]["address"]["neighborhood"],
            city=data["payer"]["address"]["city"],
            federal_unit=data["payer"]["address"]["federal_unit"]
        )
        result = service.pay_with_ticket(payment)
        return result
    return JsonResponse({"error": "Method not allowed"})

@csrf_exempt
def savedCard(request):
    if request.method == "POST":
        data = json.loads(request.body)
        card = Card(
            email=data["email"],
            token=data["token"],
            payment_method_id=data["payment_method_id"]
        )
        result = service.save_card(card)
        return result
    return JsonResponse({"error": "Method not allowed"})