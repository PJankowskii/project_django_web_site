from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, Income
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from user_preferences.models import UserPreference


# Create your views here.
@login_required(login_url='login')
def index(request):
    sources = Source.objects.all()
    incomes = Income.objects.filter(owner=request.user)
    paginator = Paginator(incomes, 3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'incomes': incomes,
        'page_obj': page_obj,
        'currency': currency,
    }
    return render(request, 'incomes/index.html', context)


@login_required(login_url='login')
def add_income(request):
    sources = Source.objects.all()
    context = {
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
            messages.error(request, 'Amount is require.')
            return render(request, 'incomes/add_income.html', context)

        if not description:
            messages.error(request, 'Description is require.')
            return render(request, 'incomes/add_income.html', context)

        if not date:
            messages.error(request, 'Date is require.')
            return render(request, 'incomes/add_income.html', context)

        Income.objects.create(owner=request.user, amount=amount, date=date, source=source, description=description)
        messages.success(request, 'Income saved successfully.')
        return redirect('incomes')


@login_required(login_url='login')
def edit_income(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
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
            messages.error(request, 'Amount is require.')
            return render(request, 'incomes/edit_income.html', context)
        if not description:
            messages.error(request, 'Description is require.')
            return render(request, 'incomes/edit_income.html', context)
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description
        income.save()
        messages.success(request, 'Income saved successfully.')
        return redirect('incomes')


@login_required(login_url='login')
def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Income removed.')
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
