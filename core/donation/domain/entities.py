class Payment:
    def __init__(self, amount: float, description: str, payment_method_id: str, email: str,identification_type: str, identification_number: str, token: str=None, first_name: str=None, last_name: str=None, installments: str=None, 
    issuer_id: str=None, zip_code: str=None, street_name: str=None, street_number: str=None, neighborhood: str=None, city: str=None, federal_unit: str=None):
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
        self.zip_code = zip_code
        self.street_name = street_name
        self.street_number = street_number
        self.neighborhood = neighborhood
        self.city = city
        self.federal_unit = federal_unit