from rest_framework_mongoengine.routers import DefaultRouter
from . import views



router = DefaultRouter()
router.register(r'xforms', views.XFormViewSet)
router.register(r'plines', views.PowerLineViewSet)
router.register(r'pstations', views.PowerStationViewSet)
