from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = \
    [
        path('', views.index, name="expenses"),
        path('add-expense', views.add_expense, name="add-expense"),
        path('edit-expense/<int:id>', views.edit_expense, name="edit-expense"),
        path('delete-expense/<int:id>', views.delete_expense, name="delete-expense"),
        path('search-expenses', csrf_exempt(views.search_expenses), name="search-expenses"),
        path('summary-expense-category', views.summary_expense_category, name="summary-expense-category"),
        path('stats-expenses', views.stats_expenses_view, name="stats-expenses"),
        path('export-expenses-pdf', views.export_expenses_pdf, name="export-expenses-pdf"),
    ]
