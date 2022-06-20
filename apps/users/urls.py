from rest_framework.routers import SimpleRouter

from django.urls import path, re_path

from .views import *

router = SimpleRouter()
router.register('trader', TraderViewSet)
router.register('totp', TOTPViewSet)
router.register('', VerificationView)
router.register('', InvestorDashboardView)
router.register('', UserProfileViewSet)
router.register('history', PaymentsHistoryViewSet, basename='history')
router.register('', BalanceViewSet, basename='balance')

urlpatterns = [
    # path('totp/create/', TOTPCreateView.as_view(), name='totp-create'),
    # path('totp/verify/', TOTPVerifyView.as_view(), name='totp-verify'),
    # path('totp/delete/', TOTPDeleteView.as_view(), name='totp-delete'),
    # re_path(r'^totp/login/(?P<token>[0-9]{6})/$', TOTPVerifyView.as_view(), name='totp-login')
]

urlpatterns += router.urls
