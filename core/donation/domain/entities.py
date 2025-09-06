class Payment:
    def __init__(self, amount: float, token: str, first_name: str, last_name: str, description: str, installments: str, payment_method_id: str, issuer_id: str, email: str, identification_type: str, identification_number: str, address_id: int):
        self.amount = amount
        self.token = token
        self.first_name = first_name
        self.last_name = last_name
        self.description = description
        self.installments = installments
        self.payment_method_id = payment_method_id
        self.issuer_id = issuer_id
        self.email = email
        self.identification_type = identification_type
        self.identification_number = identification_number
        self.address_id = address_id