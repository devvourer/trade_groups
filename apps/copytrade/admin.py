from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from .models import *

from import_export.admin import ImportExportMixin


class MembershipInline(admin.TabularInline):
    model = Membership
    readonly_fields = ('investor', 'invested_sum', 'income', 'group')
    extra = 0
    empty_value_display = '--пусто--'


class TradeGroupInline(admin.TabularInline):
    model = TradeGroup
    fields = ('title', 'created', 'status')
    readonly_fields = fields
    extra = 0


@admin.register(TradeGroup)
class TradeGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'trader', 'title', 'status')
    list_display_links = ('id', 'title')
    list_filter = ('created', 'status')
    search_fields = ('trader__user__email', 'title')
    search_help_text = 'Поиск групп по трейдеру или по названию группы'
    inlines = [MembershipInline]

    readonly_fields = ('created', 'trader_binance_balance', 'investors')
    exclude = ('slug', )
    empty_value_display = '--пусто--'


@admin.register(Membership)
class MembershipAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'group', 'investor', 'invested_sum')
    list_display_links = ('id',)
    # list_filter = ('group', 'investor')
    search_fields = ('group__title', 'investor__email')
    search_help_text = 'Поиск по названию группы или по почте инвестора'
