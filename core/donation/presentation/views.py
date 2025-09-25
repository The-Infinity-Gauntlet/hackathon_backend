from core.donation.infra.repository import MercadoPagoRepository, MercadoPagoWebhookRepository, payment_status
from core.donation.app.services import DonationService
from core.donation.domain.entities import Payment, Card
from django.views.decorators.csrf import csrf_exempt
from django.http.response import JsonResponse
from rest_framework.response import Response
from rest_framework import status
import json

repo = MercadoPagoRepository()
repoWebhook = MercadoPagoWebhookRepository()
service = DonationService(repository=repo)
serviceWebhook = DonationService(repository=repoWebhook)

def _get_service():
    try:
        repo = MercadoPagoRepository()
        return DonationService(repository=repo)
    except RuntimeError as e:
        return None

@csrf_exempt
def paymentPix(request):
    if request.method == "POST":
        service = _get_service()
        if service is None:
            return JsonResponse({"error": "mercadopago not installed"}, status=503)
        data = json.loads(request.body)
        payment = Payment(
            amount=float(data.get("transaction_amount")),
            description=data.get("description"),
            payment_method_id=data.get("payment_method_id"),
            email=data["payer"]["email"],
            identification_type=data["payer"]["identification"]["type"],
            identification_number=data["payer"]["identification"]["number"],
        )
        result = service.pay_with_pix(payment)
        result_data = json.loads(result.content)
        print("Dados da resposta: ", result_data)
        payment_status[result_data['id']] = result_data['status']
        return JsonResponse(result_data, safe=False)
    return JsonResponse({"error": "Method not allowed"})


@csrf_exempt
def paymentCard(request):
    if request.method == "POST":
        service = _get_service()
        if service is None:
            return JsonResponse({"error": "mercadopago not installed"}, status=503)
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
            identification_number=data["payer"]["identification"]["number"],
        )
        result = service.pay_with_card(payment)
        return result
    return JsonResponse({"error": "Method not allowed"})


@csrf_exempt
def paymentTicket(request):
    if request.method == "POST":
        service = _get_service()
        if service is None:
            return JsonResponse({"error": "mercadopago not installed"}, status=503)
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
            federal_unit=data["payer"]["address"]["federal_unit"],
        )
        result = service.pay_with_ticket(payment)
        return result
    return JsonResponse({"error": "Method not allowed"})


@csrf_exempt
def savedCard(request):
    if request.method == "POST":
        service = _get_service()
        if service is None:
            return JsonResponse({"error": "mercadopago not installed"}, status=503)
        data = json.loads(request.body)
        card = Card(
            email=data["email"],
            token=data["token"],
            payment_method_id=data["payment_method_id"],
        )
        result = service.save_card(card)
        return result
    return JsonResponse({"error": "Method not allowed"})

@csrf_exempt
def createWebhook(request):
    try:
        webhook_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    result = serviceWebhook.create_webhook(webhook_data)
    return JsonResponse(result, status=200)

@csrf_exempt
def getStatus(request, payment_id):
    #status = payment_status.get(payment_id)
    #if status:
        #return JsonResponse({"payment_id": payment_id, "status": status})
    #return JsonResponse({"error": "Pagamento não encontrado"}, status=404)
    try:
        mp_repo = MercadoPagoRepository()
        payment = mp_repo.sdk.payment().get(payment_id)
        return JsonResponse(payment["response"])
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)