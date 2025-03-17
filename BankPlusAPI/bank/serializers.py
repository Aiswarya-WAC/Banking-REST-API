from bank.models import BankAccount, Transaction
from rest_framework import serializers

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'amount', 'transaction_type', 'status']

    def get_status(self, obj):
        return "Deposit Successful" if obj.transaction_type == Transaction.DEPOSIT else "Withdrawal Successful"
