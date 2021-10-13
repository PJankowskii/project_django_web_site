from django.contrib import admin
from .models import Expense, Category


# Register your models here.
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'owner', 'category', 'date')
    list_per_page = 20


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category, CategoryAdmin)
