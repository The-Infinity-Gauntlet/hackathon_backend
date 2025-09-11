class User:
    def __init__(self, id: int | None, name: str, email: str) -> None:
        self.id: int | None = id
        self.name: str = name
        self.email: str = email
