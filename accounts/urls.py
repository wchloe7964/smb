from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transaction/<uuid:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('goals/', views.financial_goals, name='financial_goals'),
]