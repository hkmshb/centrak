from rest_framework_mongoengine.routers import DefaultRouter
from . import views



router = DefaultRouter()
router.register(r'xforms', views.XFormViewSet)
