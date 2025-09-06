from core.donation.domain.repository import DonationRepository
from core.donation.domain.entities import Payment

class DonationService:
    def __init__(self, repository: DonationRepository):
        self.repository = repository
    
    def pay_with_pix(self, amount: float, description: str, first_name: str, last_name: str, payment_method_id: str, email: str, identification_type: str, identification_number: str):
        donation = Payment(amount=amount, description=description, first_name=first_name, last_name=last_name, payment_method_id=payment_method_id, email=email, identification_type=identification_type, identification_number=identification_number)
        return self.repository.paymentPix(donation)
    
    def pay_with_card(self, amount: float, token: str, description: str, installments: str, payment_method_id: str, issuer_id: str, email: str, identification_type: str, identification_number: str):
        donation = Payment(amount=amount, token=token, description=description, installments=installments, payment_method_id=payment_method_id, issuer_id=issuer_id, email=email, identification_type=identification_type, identification_number=identification_number)
        return self.repository.paymentCard(donation)
    
    def pay_with_ticket(self, amount: float, description: str, payment_method_id: str, email: str, first_name: str, last_name: str, identification_type: str, identification_number: str, address_id: int):
        donation = Payment(amount=amount, description=description, payment_method_id=payment_method_id, email=email, first_name=first_name, last_name=last_name, identification_type=identification_type, identification_number=identification_number)
        return self.repository.paymentTicket(donation)