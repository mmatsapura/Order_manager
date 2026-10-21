class EmailTaken(Exception):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f'Email already registered: {email}')


class InvalidCredentials(Exception):
    def __init__(self) -> None:
        super().__init__('Invalid credentials:')


class InvalidToken(Exception):
    def __init__(self) -> None:
        super().__init__('Invalid token:')


class ProductNameTaken(Exception):
    def __init__(self, name) -> None:
        self.name = name
        super().__init__(f'Product {name} already taken')


class ProductNotFound(Exception):
    def __init__(self) -> None:
        super().__init__('Product not passed')


class OrderNotFound(Exception):
    def __init__(self) -> None:
        super().__init__('Order not found')


class QueueUnavailable(Exception):
    def __init__(self) -> None:
        super().__init__('Queue unavailable')


class OrderCanNotBeCancelled(Exception):
    def __init__(self, status: str) -> None:
        self.status = status
        super().__init__(f"Order can't be cancelled: {status}")


class OrderCannotBeUpdated(Exception):
    def __init__(self) -> None:
        super().__init__("Order can't be updated")
