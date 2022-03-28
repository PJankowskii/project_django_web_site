from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = \
    [
        path('', views.index, name="dashboard"),
        path('summary-last-month-expenses', views.summary_last_month_expenses, name="summary-last-month-expenses"),
        path('summary-last-month-incomes', views.summary_last_month_incomes, name="summary-last-month-incomes"),
    ]
