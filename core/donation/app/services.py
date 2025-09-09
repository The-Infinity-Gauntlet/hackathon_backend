from core.donation.domain.repository import DonationRepository
from core.donation.domain.entities import Payment

class DonationService:
    def __init__(self, repository: DonationRepository):
        self.repository = repository
    
    def pay_with_pix(self, payment: Payment):
        return self.repository.paymentPix(payment)
    
    def pay_with_card(self, payment: Payment):
        return self.repository.paymentCard(payment)
    
    def pay_with_ticket(self, payment: Payment):
        return self.repository.paymentTicket(payment)
    
    def save_card(self, payment: Payment):
        return self.repository.saved_card(payment)