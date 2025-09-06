class Payment:
    def __init__(self, amount: float, token: str, description: str, installments: str, payment_method_id: str, issuer_id: str, email: str, identification_type: str, identification_number: str):
        self.amount = amount
        self.token = token
        self.description = description
        self.installments = installments
        self.payment_method_id = payment_method_id
        self.issuer_id = issuer_id
        self.email = email
        self.identification_type = identification_type
        self.identification_number = identification_number