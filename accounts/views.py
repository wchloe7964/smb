from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Account, Transaction, FinancialGoal, Budget
import random
from faker import Faker

fake = Faker()

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # Create sample data for new user
            create_sample_data(user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard(request):
    accounts = Account.objects.filter(user=request.user)
    
    # Create sample data if no accounts exist
    if not accounts.exists():
        accounts = create_sample_data(request.user)
    
    # Calculate financial health score (simplified)
    total_balance = sum(account.balance for account in accounts)
    
    # Calculate financial health score
    if total_balance > 10000:
        health_score = "Excellent"
        health_color = "text-green-600"
    elif total_balance > 5000:
        health_score = "Good"
        health_color = "text-blue-600"
    elif total_balance > 1000:
        health_score = "Fair"
        health_color = "text-yellow-600"
    else:
        health_score = "Needs Attention"
        health_color = "text-red-600"
    
    recent_transactions = Transaction.objects.filter(
        account__user=request.user
    ).order_by('-date')[:10]
    
    # Monthly spending by category
    thirty_days_ago = timezone.now() - timedelta(days=30)
    spending_by_category = Transaction.objects.filter(
        account__user=request.user,
        transaction_type='debit',
        date__gte=thirty_days_ago
    ).values('category').annotate(total=Sum('amount'))
    
    # Get financial goals
    goals = FinancialGoal.objects.filter(user=request.user)[:3]
    
    context = {
        'accounts': accounts,
        'total_balance': total_balance,
        'recent_transactions': recent_transactions,
        'spending_by_category': spending_by_category,
        'goals': goals,
        'health_score': health_score,
        'health_color': health_color,
    }
    return render(request, 'accounts/dashboard.html', context)

def create_sample_data(user):
    """Create sample accounts and transactions for demo"""
    accounts = []
    account_types = ['checking', 'savings']
    
    for acc_type in account_types:
        balance = random.randint(5000, 25000) if acc_type == 'checking' else random.randint(10000, 50000)
        account = Account.objects.create(
            user=user,
            account_type=acc_type,
            balance=balance
        )
        accounts.append(account)
        
        # Create sample transactions
        for i in range(20):
            is_debit = random.choice([True, True, True, False])  # More debits than credits
            amount = random.randint(10, 200) if is_debit else random.randint(1000, 5000)
            trans_type = 'debit' if is_debit else 'credit'
            categories = [cat[0] for cat in Transaction.CATEGORIES if cat[0] != 'income']
            category = random.choice(categories) if is_debit else 'income'
            
            Transaction.objects.create(
                account=account,
                amount=amount,
                transaction_type=trans_type,
                category=category,
                description=fake.sentence(),
                merchant=fake.company(),
                balance_after=max(0, balance - amount) if is_debit else balance + amount
            )
    
    # Create sample goals
    FinancialGoal.objects.create(
        user=user,
        name="Emergency Fund",
        target_amount=10000,
        current_amount=7500,
        target_date=timezone.now() + timedelta(days=180)
    )
    
    FinancialGoal.objects.create(
        user=user,
        name="Vacation to Hawaii",
        target_amount=5000,
        current_amount=1500,
        target_date=timezone.now() + timedelta(days=365)
    )
    
    return accounts

@login_required
def transaction_detail(request, transaction_id):
    try:
        transaction = Transaction.objects.get(transaction_id=transaction_id, account__user=request.user)
        return render(request, 'accounts/transaction_detail.html', {'transaction': transaction})
    except Transaction.DoesNotExist:
        return redirect('dashboard')

@login_required
def financial_goals(request):
    goals = FinancialGoal.objects.filter(user=request.user)
    return render(request, 'accounts/financial_goals.html', {'goals': goals})