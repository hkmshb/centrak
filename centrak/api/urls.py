from rest_framework.routers import DefaultRouter
from . import views


# register routes
router = DefaultRouter()
router.register('apiservices', views.ApiServiceInfoViewSet)
