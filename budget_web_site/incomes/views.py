from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, Income
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
    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user).order_by('-id')
    paginator = Paginator(incomes, 15)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    todays_date = datetime.date.today()

    # currency
    # currency = UserPreference.objects.get(user=request.user).currency
    context = \
        {
            'incomes': incomes,
            'page_obj': page_obj,
            # 'currency': currency,
            'todays_date': todays_date,
        }
    return render(request, 'incomes/index.html', context)


@login_required(login_url='login')
def add_income(request):
    sources = Source.objects.all()
    context = \
        {
            'sources': sources,
            'values': request.POST,
        }
    if request.method == "GET":
        return render(request, 'incomes/add_income.html', context)

    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        # import pdb
        # pdb.set_trace()
        if not amount:
            messages.error(request, 'Amount is require')
            return render(request, 'incomes/add_income.html', context)
        if not description:
            messages.error(request, 'Description is require')
            return render(request, 'incomes/add_income.html', context)
        if not source:
            messages.error(request, 'Source is require')
            return render(request, 'incomes/add_expense.html', context)
        if not date:
            messages.error(request, 'Date is require')
            return render(request, 'incomes/add_income.html', context)
        Income.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request, 'Income saved successfully')
        return redirect('incomes')


@login_required(login_url='login')
def edit_income(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = \
        {
            'income': income,
            'values': income,
            'sources': sources,
        }
    if request.method == "GET":
        return render(request, 'incomes/edit_income.html', context)
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']
        if not amount:
            messages.error(request, 'Amount is require')
            return render(request, 'incomes/edit_income.html', context)
        if not description:
            messages.error(request, 'Description is require')
            return render(request, 'incomes/edit_income.html', context)
        if not date:
            messages.error(request, 'Date is require')
            return render(request, 'incomes/edit_income.html', context)
        if not source:
            messages.error(request, 'Source is require')
            return render(request, 'incomes/edit_income.html', context)
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description
        income.save()
        messages.success(request, 'Income saved successfully')
        return redirect('incomes')


@login_required(login_url='login')
def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income removed')
    return redirect('incomes')


@login_required(login_url='login')
def search_incomes(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        incomes_filter = Income.objects.filter(amount__istartswith=search_str,
                                               owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            description__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = incomes_filter.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='login')
def summary_income_source(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    three_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    current_month = todays_date - datetime.timedelta(days=30)
    incomes_six = Income.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    incomes_three = Income.objects.filter(owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    incomes_one = Income.objects.filter(owner=request.user, date__gte=current_month, date__lte=todays_date)
    final_rep_six = {}
    final_rep_three = {}
    final_rep_one = {}

    def get_source(income):
        return income.source

    source_list_six = list(set(map(get_source, incomes_six)))
    source_list_three = list(set(map(get_source, incomes_three)))
    source_list_one = list(set(map(get_source, incomes_one)))

    def get_income_source_amount_six(source):
        amount = 0
        filtered_by_source = incomes_six.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    def get_income_source_amount_three(source):
        amount = 0
        filtered_by_source = incomes_three.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    def get_income_source_amount_one(source):
        amount = 0
        filtered_by_source = incomes_one.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in incomes_six:
        for y in source_list_six:
            final_rep_six[y] = get_income_source_amount_six(y)

    for x in incomes_three:
        for y in source_list_three:
            final_rep_three[y] = get_income_source_amount_three(y)

    for x in incomes_one:
        for y in source_list_one:
            final_rep_one[y] = get_income_source_amount_one(y)

    return JsonResponse({'income_source_data_six': final_rep_six, 'income_source_data_three': final_rep_three,
                         'income_source_data_one': final_rep_one}, safe=False)


@login_required(login_url='login')
def stats_incomes_view(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    three_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    current_month = todays_date - datetime.timedelta(days=30)
    incomes = Income.objects.filter(owner=request.user)
    incomes_six = Income.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    incomes_three = Income.objects.filter(owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    incomes_one = Income.objects.filter(owner=request.user, date__gte=current_month, date__lte=todays_date)
    context = \
        {
            'incomes_one': incomes_one,
            'incomes_three': incomes_three,
            'incomes_six': incomes_six,
            'incomes': incomes,
        }
    return render(request, 'incomes/stats_incomes.html', context)


@login_required(login_url='login')
def export_incomes_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Incomes' + \
                                      str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    incomes = Income.objects.filter(owner=request.user)
    sum = incomes.aggregate(Sum('amount'))

    html_string = render_to_string('incomes/pdf_output.html', {'incomes': incomes, 'total': sum['amount__sum']})
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
def export_summary_incomes_pdf(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    three_months_ago = todays_date - datetime.timedelta(days=30 * 3)
    current_month = todays_date - datetime.timedelta(days=30)
    incomes_six = Income.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    incomes_three = Income.objects.filter(owner=request.user, date__gte=three_months_ago, date__lte=todays_date)
    incomes_one = Income.objects.filter(owner=request.user, date__gte=current_month, date__lte=todays_date)
    final_rep_six = {}
    final_rep_three = {}
    final_rep_one = {}

    def get_source(income):
        return income.source

    source_list_six = list(set(map(get_source, incomes_six)))
    source_list_three = list(set(map(get_source, incomes_three)))
    source_list_one = list(set(map(get_source, incomes_one)))

    def get_income_source_amount_six(source):
        amount = 0
        filtered_by_source = incomes_six.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    def get_income_source_amount_three(source):
        amount = 0
        filtered_by_source = incomes_three.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    def get_income_source_amount_one(source):
        amount = 0
        filtered_by_source = incomes_one.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for x in incomes_six:
        for y in source_list_six:
            final_rep_six[y] = get_income_source_amount_six(y)

    for x in incomes_three:
        for y in source_list_three:
            final_rep_three[y] = get_income_source_amount_three(y)

    for x in incomes_one:
        for y in source_list_one:
            final_rep_one[y] = get_income_source_amount_one(y)

    sum_one = incomes_one.aggregate(Sum('amount'))
    sum_three = incomes_three.aggregate(Sum('amount'))
    sum_six = incomes_six.aggregate(Sum('amount'))

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Incomes' + \
                                      str(datetime.datetime.now()) + '.pdf'
    response['Content-Transfer-Encoding'] = 'binary'

    html_string = render_to_string('incomes/pdf_output_summary_incomes.html',
                                   {'final_rep_six': final_rep_six,
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
