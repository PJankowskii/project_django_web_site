from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = \
    [
        path('', views.index, name="incomes"),
        path('add-income', views.add_income, name="add-income"),
        path('edit-income/<int:id>', views.edit_income, name="edit-income"),
        path('delete-income/<int:id>', views.delete_income, name="delete-income"),
        path('search-incomes', csrf_exempt(views.search_incomes), name="search-incomes"),
        path('summary-income-source', views.summary_income_source, name="summary-income-source"),
        path('stats-incomes', views.stats_incomes_view, name="stats-incomes"),
        path('export-incomes-pdf', views.export_incomes_pdf, name="export-incomes-pdf"),
        path('export-summary-incomes-pdf', views.export_summary_incomes_pdf, name="export-summary-incomes-pdf"),
    ]
