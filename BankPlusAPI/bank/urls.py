from django.urls import path

from bank.views import AccountDetailsView, DepositView, LoginView, RegisterView, WithdrawView

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('accounts/deposit/', DepositView.as_view()),
    path('accounts/withdraw/', WithdrawView.as_view()),
    path('accounts/', AccountDetailsView.as_view()),
]
