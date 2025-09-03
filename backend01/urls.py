from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('books', views.BooksViewSet)

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('send_verification_code/', views.SendVerificationCodeView.as_view(), name='send_verification_code'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('reset_password/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('userinfo/', views.UserInfoView.as_view(), name='userinfo'),
    path('', include(router.urls)),
]