from django.contrib.auth.models import User
from bank.models import BankAccount, Transaction
from bank.serializers import BankAccountSerializer
from rest_framework import serializers, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({'error': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password)
        account = BankAccount.objects.create(account_number=f'ACC{user.id}', owner=user, balance=0)
        return Response({'message': 'Account created', 'account_number': account.account_number}, status=status.HTTP_201_CREATED)
    
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


from decimal import Decimal

class DepositView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if Decimal(amount) <= 0:
            return Response({'error': 'Deposit amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        account = BankAccount.objects.get(owner=request.user)
        account.balance += Decimal(amount)  # Convert amount to Decimal
        account.save()
        Transaction.objects.create(account=account, amount=Decimal(amount), transaction_type=Transaction.DEPOSIT)

        return Response({'message': 'Deposit successful', 'new_balance': float(account.balance)}, status=status.HTTP_200_OK)

class WithdrawView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        account = BankAccount.objects.get(owner=request.user)

        if Decimal(amount) <= 0:
            return Response({'error': 'Withdrawal amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

        if account.balance < Decimal(amount):
            return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

        account.balance -= Decimal(amount)  # Convert amount to Decimal
        account.save()
        Transaction.objects.create(account=account, amount=Decimal(amount), transaction_type=Transaction.WITHDRAWAL)

        return Response({'message': 'Withdrawal successful', 'new_balance': float(account.balance)}, status=status.HTTP_200_OK)

from rest_framework.pagination import PageNumberPagination
from bank.serializers import TransactionSerializer

class TransactionPagination(PageNumberPagination):
    page_size = 5  # Number of transactions per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class AccountDetailsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        account = BankAccount.objects.get(owner=request.user)
        serializer = BankAccountSerializer(account)

        # Fetch transactions and apply pagination
        transactions = Transaction.objects.filter(account=account).order_by('-date')  # Change 'created_at' to 'date'
        paginator = TransactionPagination()
        paginated_transactions = paginator.paginate_queryset(transactions, request)
        transaction_serializer = TransactionSerializer(paginated_transactions, many=True)

        return paginator.get_paginated_response({
            'account_details': serializer.data,
            'transactions': transaction_serializer.data
        })
