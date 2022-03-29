from django.contrib import admin
from .models import Saving, TypeSaving


# Register your models here.
class SavingAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'owner', 'type_saving', 'date')
    list_per_page = 20


class TypeSavingAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_per_page = 20


admin.site.register(Saving, SavingAdmin)
admin.site.register(TypeSaving, TypeSavingAdmin)
