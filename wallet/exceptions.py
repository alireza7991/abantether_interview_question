class InsufficientBalanceException(Exception):
    pass


class InvalidWithdrawalAmountException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
