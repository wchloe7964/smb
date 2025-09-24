from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Conversation, Message
from accounts.models import Account, Transaction
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

@login_required
def ai_assistant(request):
    return render(request, 'ai_assistant/chat.html')

@csrf_exempt
@login_required
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            
            if not user_message:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Generate AI response based on user message
            response = generate_ai_response(request.user, user_message)
            
            # Save conversation
            conversation, created = Conversation.objects.get_or_create(user=request.user)
            Message.objects.create(conversation=conversation, content=user_message, is_user=True)
            Message.objects.create(conversation=conversation, content=response, is_user=False)
            
            return JsonResponse({'response': response})
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def generate_ai_response(user, message):
    """Simple rule-based AI assistant"""
    message_lower = message.lower()
    
    # Get user's financial data
    accounts = Account.objects.filter(user=user)
    total_balance = sum(account.balance for account in accounts)
    
    # Check balance queries
    if any(word in message_lower for word in ['balance', 'how much', 'money']):
        account_balances = "\n".join([f"- {acc.get_account_type_display()}: ${acc.balance:,.2f}" for acc in accounts])
        return f"Here are your current account balances:\n{account_balances}\n\nTotal Balance: ${total_balance:,.2f}"
    
    # Spending analysis
    elif any(word in message_lower for word in ['spend', 'spending', 'where money', 'expense']):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        spending = Transaction.objects.filter(
            account__user=user,
            transaction_type='debit',
            date__gte=thirty_days_ago
        ).values('category').annotate(total=Sum('amount'))
        
        if spending:
            spending_text = "\n".join([f"- {item['category'].title()}: ${item['total']:,.2f}" for item in spending])
            total_spent = sum(item['total'] for item in spending)
            return f"Here's your spending in the last 30 days:\n{spending_text}\n\nTotal spent: ${total_spent:,.2f}"
        else:
            return "I don't see any spending transactions in the last 30 days."
    
    # Savings advice
    elif any(word in message_lower for word in ['save', 'saving', 'budget']):
        return "Based on your spending patterns, I recommend:\n1. Set up automatic transfers to savings\n2. Review your subscription payments\n3. Consider rounding up transactions to save extra\nWould you like me to help set up any of these?"
    
    # Transaction history
    elif any(word in message_lower for word in ['transaction', 'history', 'recent']):
        recent = Transaction.objects.filter(account__user=user).order_by('-date')[:5]
        if recent:
            transactions = "\n".join([f"- {t.date.strftime('%m/%d')} {t.description}: ${t.amount}" for t in recent])
            return f"Your recent transactions:\n{transactions}"
        else:
            return "No recent transactions found."
    
    # Greeting
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'hola']):
        return f"Hello {user.username}! I'm your SmartBank AI assistant. I can help you with:\n• Account balances\n• Spending analysis\n• Savings advice\n• Transaction history\n\nHow can I help you today?"
    
    # Help
    elif any(word in message_lower for word in ['help', 'what can you do']):
        return """I can help you with various banking tasks:

• Check account balances
• Analyze your spending habits
• Provide savings recommendations
• Show recent transactions
• Answer questions about your finances

Just ask me anything about your accounts!"""

    # Default response
    else:
        return "I understand you're asking about: '" + message + "'.\n\nI'm designed to help with banking-related questions. You can ask me about your balances, spending, or transactions. Would you like to try one of those topics?"