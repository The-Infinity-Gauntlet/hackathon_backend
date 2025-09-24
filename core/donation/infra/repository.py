import os, uuid
from django.http import JsonResponse, HttpResponseServerError
from core.donation.domain.entities import Payment
from core.donation.domain.repository import DonationRepository

payment_status = {}


class MercadoPagoRepository:
    def __init__(self):
        try:
            import mercadopago  # type: ignore
        except ModuleNotFoundError as e:
            raise RuntimeError(
                "mercadopago package not installed. Install it to use donation endpoints."
            ) from e
        self._mp = mercadopago
        self.sdk = mercadopago.SDK(os.getenv("ACCESS_TOKEN"))

    def paymentPix(self, payment: Payment):
        request_options = self._mp.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": str(uuid.uuid4())}

        payment_data = {
            "transaction_amount": payment.amount,  # transaction_amount
            "description": payment.description,
            "payment_method_id": payment.payment_method_id,
            "payer": {
                "email": payment.email,
                "first_name": payment.first_name,
                "last_name": payment.last_name,
                "identification": {
                    "type": payment.identification_type,
                    "number": payment.identification_number,
                },
            },
        }

        response = self.sdk.payment().create(payment_data, request_options)
        payment = response["response"]

        return JsonResponse(payment, safe=False)

    def paymentCard(self, payment: Payment):
        request_options = self._mp.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": str(uuid.uuid4())}

        payment_data = {
            "transaction_amount": payment.amount,
            "token": payment.token,
            "description": payment.description,
            "installments": payment.installments,
            "payment_method_id": payment.payment_method_id,
            "issuer_id": payment.issuer_id,
            "payer": {
                "email": payment.email,
                "identification": {
                    "type": payment.identification_type,
                    "number": payment.identification_number,
                },
            },
        }

        response = self.sdk.payment().create(payment_data, request_options)
        payment = response["response"]

        return JsonResponse(payment, safe=False)

    def paymentTicket(self, payment: Payment):
        request_options = self._mp.config.RequestOptions()
        request_options.custom_headers = {"x-idempotency-key": str(uuid.uuid4())}

        payment_data = {
            "transaction_amount": payment.amount,
            "description": payment.description,
            "payment_method_id": payment.payment_method_id,
            "payer": {
                "email": payment.email,
                "first_name": payment.first_name,
                "last_name": payment.last_name,
                "identification": {
                    "type": payment.identification_type,
                    "number": payment.identification_number,
                },
                "address": {
                    "zip_code": payment.zip_code,
                    "street_name": payment.street_name,
                    "street_number": payment.street_number,
                    "neighborhood": payment.neighborhood,
                    "city": payment.city,
                    "federal_unit": payment.federal_unit,
                },
            },
        }

        response = self.sdk.payment().create(payment_data, request_options)
        payment = response["response"]

        return JsonResponse(payment, safe=False)

    def saved_card(self, payment: Payment):
        # Cria um cliente para ser associado ao cartão
        customer_data = {
            "email": payment.email,
        }
        client_response = self.sdk.customer().create(customer_data)
        customer = client_response["response"]

        # Cria o cartão associado ao cliente
        card_data = {
            "token": payment.token,
            "payment_method_id": payment.payment_method_id,
        }
        card_response = self.sdk.card().create(customer["id"], card_data)
        card = card_response["response"]
        return JsonResponse(card, safe=False)
    
class MercadoPagoWebhookRepository(DonationRepository):
    def payment_with_pix(self, donation: Payment):
        raise NotImplementedError("Este repo não implementa pagamentos.")

    def payment_with_card(self, donation: Payment):
        raise NotImplementedError("Este repo não implementa pagamentos.")

    def payment_with_ticket(self, donation: Payment):
        raise NotImplementedError("Este repo não implementa pagamentos.")

    def saved_card(self, donation: Payment):
        raise NotImplementedError("Este repo não implementa pagamentos.")

    def createWebhook(self, data: dict):
        payment_data = data.get("data", {})
        payment_id = payment_data.get("id")
        status = data.get("data", {}).get("status")

        if payment_id and status:
            payment_status[payment_id] = status
            print(f"[Webhook] Pagamento {payment_id} com status {status} recebido")
        else:
            print("[Webhook] Dados incompletos recebidos")
        
        return {"payment_id": payment_id, "status": payment_status}
