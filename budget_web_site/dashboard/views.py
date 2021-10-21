from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_preferences.models import UserPreference
from expenses.models import Expense, Category
from incomes.models import Source, Income
from django.core.paginator import Paginator


# Create your views here.
@login_required(login_url='login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)

    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user)

    paginator_expenses = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj_expenses = Paginator.get_page(paginator_expenses, page_number)

    paginator_incomes = Paginator(incomes, 5)
    page_obj_incomes = Paginator.get_page(paginator_incomes, page_number)

    currency = UserPreference.objects.get(user=request.user).currency
    context = \
        {
            'expenses': expenses,
            'incomes': incomes,
            'page_obj_expenses': page_obj_expenses,
            'page_obj_incomes': page_obj_incomes,
            'currency': currency,
        }
    return render(request, 'dashboard/index.html', context)
