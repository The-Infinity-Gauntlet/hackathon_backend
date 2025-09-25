from abc import ABC, abstractmethod
from core.donation.domain.entities import Payment

class DonationRepository(ABC):
    @abstractmethod
    def payment_with_pix(self, donation: Payment):
        pass

    @abstractmethod
    def payment_with_card(self, donation: Payment):
        pass

    @abstractmethod
    def payment_with_ticket(self, donation: Payment):
        pass

    @abstractmethod
    def saved_card(self, donation: Payment):
        pass

    @abstractmethod
    def createWebhook(self, data: dict):
        pass