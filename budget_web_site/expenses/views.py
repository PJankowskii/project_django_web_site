from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
# from user_preferences.models import UserPreference
import datetime

from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum


# Create your views here.
@login_required(login_url='login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user).order_by('-id')
    paginator = Paginator(expenses, 15)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    todays_date = datetime.date.today()
    # currency
    # currency = UserPreference.objects.get(user=request.user).currency
    context = \
        {
            'expenses': expenses,
            'page_obj': page_obj,
            # 'currency': currency,
            'todays_date': todays_date,
        }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='login')
def add_expense(request):
    categories = Category.objects.all()
    context = \
        {
            'categories': categories,
            'values': request.POST
        }
    if request.method == "GET":
        return render(request, 'expenses/add_expense.html', context)

    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        # import pdb
        # pdb.set_trace()
        if not amount:
            messages.error(request, 'Amount is require')
            return render(request, 'expenses/add_expense.html', context)
        if not description:
            messages.error(request, 'Description is require')
            return render(request, 'expenses/add_expense.html', context)
        if not category:
            messages.error(request, 'Category is require')
            return render(request, 'expenses/add_expense.html', context)
        if not date:
            messages.error(request, 'Date is require')
            return render(request, 'expenses/add_expense.html', context)
        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        messages.success(request, 'Expense added successfully')
        return redirect('expenses')


@login_required(login_url='login')
def edit_expense(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()
    context = \
        {
            'expense': expense,
            'values': expense,
            'categories': categories,
        }
    if request.method == "GET":
        return render(request, 'expenses/edit_expense.html', context)
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']
        if not amount:
            messages.error(request, 'Amount is require')
            return render(request, 'expenses/edit_expense.html', context)
        if not description:
            messages.error(request, 'Description is require')
            return render(request, 'expenses/edit_expense.html', context)
        if not category:
            messages.error(request, 'Category is require')
            return render(request, 'expenses/edit_expense.html', context)
        if not date:
            messages.error(request, 'Date is require')
            return render(request, 'expenses/edit_expense.html', context)
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()
        messages.success(request, 'Expense saved successfully')
        return redirect('expenses')


@login_required(login_url='login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')


@login_required(login_url='login')
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses_filter = Expense.objects.filter(amount__istartswith=search_str,
                                                 owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses_filter.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='login')
def summary_expense_category(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    three_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    current_month = todays_date - datetime.timedelta(days=30)
    expenses_six = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    expenses_three = Expense.objects.filter(owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    expenses_one = Expense.objects.filter(owner=request.user, date__gte=current_month, date__lte=todays_date)
    final_rep_six = {}
    final_rep_three = {}
    final_rep_one = {}

    def get_category(expense):
        return expense.category

    category_list_six = list(set(map(get_category, expenses_six)))
    category_list_three = list(set(map(get_category, expenses_three)))
    category_list_one = list(set(map(get_category, expenses_one)))

    def get_expense_category_amount_six(category):
        amount = 0
        filtered_by_category = expenses_six.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    def get_expense_category_amount_three(category):
        amount = 0
        filtered_by_category = expenses_three.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    def get_expense_category_amount_one(category):
        amount = 0
        filtered_by_category = expenses_one.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses_six:
        for y in category_list_six:
            final_rep_six[y] = get_expense_category_amount_six(y)

    for x in expenses_three:
        for y in category_list_three:
            final_rep_three[y] = get_expense_category_amount_three(y)

    for x in expenses_one:
        for y in category_list_one:
            final_rep_one[y] = get_expense_category_amount_one(y)

    return JsonResponse({'expense_category_data_six': final_rep_six, 'expense_category_data_three': final_rep_three,
                         'expense_category_data_one': final_rep_one}, safe=False)


@login_required(login_url='login')
def stats_expenses_view(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    three_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    current_month = todays_date - datetime.timedelta(days=30)
    expenses = Expense.objects.filter(owner=request.user)
    expenses_six = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    expenses_three = Expense.objects.filter(owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    expenses_one = Expense.objects.filter(owner=request.user, date__gte=current_month, date__lte=todays_date)
    context = \
        {
            'expenses_one': expenses_one,
            'expenses_three': expenses_three,
            'expenses_six': expenses_six,
            'expenses': expenses,
        }
    return render(request, 'expenses/stats_expenses.html', context)


@login_required(login_url='login')
def export_expenses_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses' + \
                                      str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    expenses = Expense.objects.filter(owner=request.user)
    sum = expenses.aggregate(Sum('amount'))

    html_string = render_to_string('expenses/pdf_output.html', {'expenses': expenses, 'total': sum['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        # output = open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())
    return response


@login_required(login_url='login')
def export_summary_expenses_pdf(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    three_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    current_month = todays_date - datetime.timedelta(days=30)
    expenses_six = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    expenses_three = Expense.objects.filter(owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    expenses_one = Expense.objects.filter(owner=request.user, date__gte=current_month, date__lte=todays_date)
    final_rep_six = {}
    final_rep_three = {}
    final_rep_one = {}

    def get_category(expense):
        return expense.category

    category_list_six = list(set(map(get_category, expenses_six)))
    category_list_three = list(set(map(get_category, expenses_three)))
    category_list_one = list(set(map(get_category, expenses_one)))

    def get_expense_category_amount_six(category):
        amount = 0
        filtered_by_category = expenses_six.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    def get_expense_category_amount_three(category):
        amount = 0
        filtered_by_category = expenses_three.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    def get_expense_category_amount_one(category):
        amount = 0
        filtered_by_category = expenses_one.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    for x in expenses_six:
        for y in category_list_six:
            final_rep_six[y] = get_expense_category_amount_six(y)

    for x in expenses_three:
        for y in category_list_three:
            final_rep_three[y] = get_expense_category_amount_three(y)

    for x in expenses_one:
        for y in category_list_one:
            final_rep_one[y] = get_expense_category_amount_one(y)

    sum_one = expenses_one.aggregate(Sum('amount'))
    sum_three = expenses_three.aggregate(Sum('amount'))
    sum_six = expenses_six.aggregate(Sum('amount'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Expenses' + \
                                      str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    html_string = render_to_string('expenses/pdf_output_summary_expenses.html', {'final_rep_six': final_rep_six,
                                                                                 'final_rep_three': final_rep_three,
                                                                                 'final_rep_one': final_rep_one,
                                                                                 'total_one': sum_one['amount__sum'],
                                                                                 'total_three': sum_three[
                                                                                     'amount__sum'],
                                                                                 'total_six': sum_six['amount__sum']})
    html = HTML(string=html_string)
    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        # output = open(output.name, 'rb')
        output.seek(0)
        response.write(output.read())
    return response
