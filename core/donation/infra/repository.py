import mercadopago, os, uuid
from django.http import JsonResponse
from core.donation.domain.entities import Payment

class MercadoPagoRepository:
    sdk = mercadopago.SDK(os.getenv("ACCESS_TOKEN"))

    def paymentPix(self, payment: Payment):
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': str(uuid.uuid4())
        }

        payment_data = {
            "transaction_amount": payment.amount, # transaction_amount
            "description": payment.description,
            "payment_method_id": payment.payment_method_id,
            "payer": {
                "email": payment.email,
                "first_name": payment.first_name,
                "last_name": payment.last_name,
                "identification": {
                    "type": payment.identification_type,
                    "number": payment.identification_number
                }
            }
        }

        response = self.sdk.payment().create(payment_data, request_options)
        payment = response["response"]

        return JsonResponse(payment, safe=False)
    
    def paymentCard(self, payment: Payment):
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': str(uuid.uuid4())
        }

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
                    "number": payment.identification_number
                }
            }
        }

        response = self.sdk.payment().create(payment_data, request_options)
        payment = response["response"]

        return JsonResponse(payment, safe=False)
    
    def paymentTicket(self, payment: Payment):
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': str(uuid.uuid4())
        }

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
                    "number": payment.identification_number
                },
                "address": {
                    "zip_code": payment.zip_code,
                    "street_name": payment.street_name,
                    "street_number": payment.street_number,
                    "neighborhood": payment.neighborhood,
                    "city": payment.city,
                    "federal_unit": payment.federal_unit
                }
            }
        }

        response = self.sdk.payment().create(payment_data, request_options)
        payment = response["response"]

        return JsonResponse(payment, safe=False)