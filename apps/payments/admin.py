from django.contrib import admin

from .models import PaymentOrder, PaymentOrderTether, Withdraw, Currency
from import_export.admin import ImportExportMixin

class PaymentOrderInline(admin.TabularInline):
    model = PaymentOrder
    extra = 0
    can_delete = False


class WithdrawInline(admin.TabularInline):
    model = Withdraw
    extra = 0
    can_delete = False


class PaymentOrderTetherInline(admin.TabularInline):
    model = PaymentOrderTether
    extra = 0
    can_delete = False


@admin.register(PaymentOrder)
class PaymentOrderAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created']
    list_display_links = list_display


@admin.register(PaymentOrderTether)
class PaymentOrderTetherAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created']
    list_display_links = list_display


@admin.register(Withdraw)
class WithdrawAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['user', 'amount', 'created', 'status']
    list_display_links = list_display


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
    list_display_links = list_display
