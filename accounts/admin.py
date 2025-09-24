from django.contrib import admin
from .models import Account, Transaction, FinancialGoal, Budget

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'account_type', 'balance', 'created_at']
    list_filter = ['account_type', 'created_at']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['account', 'amount', 'transaction_type', 'category', 'date']
    list_filter = ['transaction_type', 'category', 'date']

@admin.register(FinancialGoal)
class FinancialGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'target_amount', 'current_amount', 'target_date']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'monthly_limit', 'current_spending']