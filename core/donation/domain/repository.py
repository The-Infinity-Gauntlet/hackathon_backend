from abc import ABC, abstractmethod

class Donation(ABC):
    @abstractmethod
    def paymentPix(self):
        pass

    @abstractmethod
    def paymentCard(self):
        pass

    @abstractmethod
    def paymentTicket(self):
        pass