from abc import ABC, abstractmethod

class DonationRepository(ABC):
    @abstractmethod
    def paymentPix(self):
        pass

    @abstractmethod
    def paymentCard(self):
        pass

    @abstractmethod
    def paymentTicket(self):
        pass