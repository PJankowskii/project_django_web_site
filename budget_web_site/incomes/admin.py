from django.contrib import admin
from .models import Income, Source


# Register your models here.
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'owner', 'source', 'date')
    list_per_page = 20


class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Income, IncomeAdmin)
admin.site.register(Source, SourceAdmin)
