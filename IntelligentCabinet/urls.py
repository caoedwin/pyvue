from django.urls import path
from . import views
app_name = 'IntelligentCabinet'
from .views import (
    CabinetListView,
    CabinetDetailView,
    GridUpdateView,
    UserReserveView,
    UserCancelReserveView,
    ConfirmBorrowView,
    CabinetGridListView
)

urlpatterns = [
    path('cabinets/', CabinetListView.as_view()),
    path('cabinets/<int:pk>/', CabinetDetailView.as_view()),
    path('grids/<int:pk>/update/', GridUpdateView.as_view()),
    path('grids/<int:pk>/reserve/', UserReserveView.as_view()),
    path('grids/<int:pk>/cancel-reserve/', UserCancelReserveView.as_view()),
    path('grids/<int:pk>/confirm-borrow/', ConfirmBorrowView.as_view()),
    path('init-data/', CabinetGridListView.as_view()),
]