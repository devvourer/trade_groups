from django.contrib import admin
from django.utils.safestring import mark_safe

from apps.copytrade.admin import TradeGroupInline, MembershipInline
from apps.payments.admin import PaymentOrderInline, WithdrawInline, PaymentOrderTetherInline

from .models import User, Trader, Document, DocumentImage, Balance, Banner, QA, Rating
from import_export.admin import ImportExportMixin

admin.site.register(Banner)
admin.site.register(QA)
admin.site.register(Rating)


class BalanceInline(admin.TabularInline):
    model = Balance
    extra = 0
    can_delete = False


class DocumentImageInline(admin.TabularInline):
    model = DocumentImage
    fields = ('image', 'get_image')
    readonly_fields = ('get_image',)
    extra = 0

    def get_image(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=240 height=320 >")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'status')
    list_display_links = list_display
    list_filter = ('status', )
    search_fields = ('user__email',)
    search_help_text = 'Поиск по почте'
    inlines = [DocumentImageInline]


@admin.register(Trader)
class TraderAdmin(admin.ModelAdmin):
    list_display = ['user', 'id']
    # readonly_fields = ['user']
    inlines = [TradeGroupInline]


@admin.register(User)
class UserAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ['id', 'email', 'phone_number']
    list_display_links = list_display
    list_filter = ('verified', 'is_trader', 'is_active')
    exclude = ('password', 'groups', 'user_permissions', 'code')
    readonly_fields = ['last_login', 'date_joined', 'is_staff', 'is_superuser']
    search_fields = ('email', 'phone_number')
    search_help_text = 'Поиск по почте или по номеру телефона'
    inlines = [BalanceInline, MembershipInline, PaymentOrderInline, PaymentOrderTetherInline, WithdrawInline]
