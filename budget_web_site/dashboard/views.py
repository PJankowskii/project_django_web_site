from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from user_preferences.models import UserPreference
from expenses.models import Expense, Category
from incomes.models import Source, Income
from django.core.paginator import Paginator
import datetime
from django.http import JsonResponse
from django.db.models import Sum
import calendar


# Create your views here.
@login_required(login_url='login')
def index(request):
    budget = 0
    daily_average = 0

    todays_date = datetime.date.today()

    last_month = todays_date - datetime.timedelta(days=30)
    expenses_one = Expense.objects.filter(owner=request.user, date__gte=last_month, date__lte=todays_date)
    incomes_one = Income.objects.filter(owner=request.user, date__gte=last_month, date__lte=todays_date)

    current_month_days = calendar.monthrange(todays_date.year, todays_date.month)[1]
    present_day = todays_date.day
    budget_denominator = current_month_days - present_day

    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user).order_by('-id')

    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user).order_by('-id')

    expenses_amount_sum_dict = Expense.objects.filter(owner=request.user, date__lte=todays_date).aggregate(
        Sum('amount'))
    incomes_amount_sum_dict = Income.objects.filter(owner=request.user, date__lte=todays_date).aggregate(Sum('amount'))
    expenses_amount_sum = expenses_amount_sum_dict.get('amount__sum')
    incomes_amount_sum = incomes_amount_sum_dict.get('amount__sum')

    if incomes_amount_sum and expenses_amount_sum is not None:
        budget += round((incomes_amount_sum - expenses_amount_sum), 2)
    if expenses_amount_sum is None and incomes_amount_sum is not None:
        budget += round(incomes_amount_sum, 2)
    if incomes_amount_sum is None and expenses_amount_sum is not None:
        budget += round((0 - expenses_amount_sum), 2)
    if incomes_amount_sum and expenses_amount_sum is None:
        budget += 0

    if budget_denominator == 0:
        daily_average += round(budget, 2)
    else:
        daily_average += round((budget / budget_denominator), 2)
        
    paginator_expenses = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj_expenses = Paginator.get_page(paginator_expenses, page_number)

    paginator_incomes = Paginator(incomes, 5)
    page_obj_incomes = Paginator.get_page(paginator_incomes, page_number)

    # CURRENCY
    # currency = UserPreference.objects.get(user=request.user).currency
    context = \
        {
            'expenses': expenses,
            'incomes': incomes,
            'page_obj_expenses': page_obj_expenses,
            'page_obj_incomes': page_obj_incomes,
            # 'currency': currency,
            'todays_date': todays_date,
            'budget': budget,
            'daily_average': daily_average,
            'expenses_one': expenses_one,
            'incomes_one': incomes_one,
        }
    return render(request, 'dashboard/index.html', context)


@login_required(login_url='login')
def summary_last_month_expenses(request):
    todays_date = datetime.date.today()
    last_month = todays_date - datetime.timedelta(days=30)
    expenses = Expense.objects.filter(owner=request.user, date__gte=last_month, date__lte=todays_date)

    final_rep = {}

    def get_category(expense):
        return expense.category

    category_list = list(set(map(get_category, expenses)))

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses:
        for y in category_list:
            final_rep[y] = get_expense_category_amount(y)

    return JsonResponse({'expense_category_data': final_rep}, safe=False)


@login_required(login_url='login')
def summary_last_month_incomes(request):
    todays_date = datetime.date.today()
    last_month = todays_date - datetime.timedelta(days=30)
    incomes = Income.objects.filter(owner=request.user, date__gte=last_month, date__lte=todays_date)

    final_rep = {}

    def get_source(income):
        return income.source

    source_list = list(set(map(get_source, incomes)))

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in incomes:
        for y in source_list:
            final_rep[y] = get_income_source_amount(y)

    return JsonResponse({'income_source_data': final_rep}, safe=False)
