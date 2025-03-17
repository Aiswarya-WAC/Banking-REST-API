from django.db import models
from django.contrib.auth.models import User

class BankAccount(models.Model):
    account_number = models.CharField(max_length=20, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.owner.username} - {self.account_number}"

class Transaction(models.Model):
    DEPOSIT = 'Deposit'
    WITHDRAWAL = 'Withdrawal'
    TRANSACTION_TYPES = [(DEPOSIT, 'Deposit'), (WITHDRAWAL, 'Withdrawal')]

    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateTimeField(auto_now_add=True)