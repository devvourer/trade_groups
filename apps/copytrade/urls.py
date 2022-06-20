from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register('trade_group', TraderGroupViewSet)

urlpatterns = []

urlpatterns += router.urls
