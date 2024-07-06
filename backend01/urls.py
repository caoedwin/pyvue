from django.urls import path, include
from rest_framework.routers import DefaultRouter

from backend01 import views

router = DefaultRouter()
router.register('backend01', views.BooksViewSet)

urlpatterns = [
    path('', include(router.urls)),
]