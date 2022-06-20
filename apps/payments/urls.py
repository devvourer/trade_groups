from rest_framework.routers import SimpleRouter
from django.urls import path

from .views import *

router = SimpleRouter()
router.register('', PaymentOrderViewSet)
router.register('tether', PaymentOrderTetherViewSet)

urlpatterns = []

urlpatterns += router.urls
