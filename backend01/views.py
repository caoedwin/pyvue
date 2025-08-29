from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Books, UserInfo
from .serializer import BooksSerializer, UserInfoSerializer
from rest_framework.renderers import JSONRenderer
from django_filters import rest_framework as df_filters
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication

class LoginView(APIView):
    authentication_classes = []
    permission_classes = []#这本身就是为了获取token，所以不能还需要token菜呢个获取

    def get(self, request):
        return Response({
            'message': '请使用POST方法登录',
            'example_request': {
                'account': 'your_username',
                'password': 'your_password'
            }
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request):
        account = request.data.get('account')
        password = request.data.get('password')
        # print(account,password)

        try:
            user = UserInfo.objects.get(account=account)
            if user.check_password(password) and user.is_active:
                refresh = RefreshToken.for_user(user)
                serializer = UserInfoSerializer(user)
                request.session['is_login_pyvue'] = True
                request.session['user_id_pyvue'] = user.id
                request.session['user_name_pyvue'] = user.username
                request.session['CNname_pyvue'] = user.CNname
                request.session['account_pyvue'] = account
                request.session['access_pyvue'] = str(refresh.access_token)
                # request.session['Skin'] = "/static/src/blue.jpg"
                request.session.set_expiry(5 * 12 * 60 * 60)
                online_user = request.session.get('account_pyvue', '')
                print(online_user,"online_userlogin")
                return Response({
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': serializer.data
                })
        except UserInfo.DoesNotExist:
            pass

        return Response({'error': '账号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'message': 'Logout successful'})


class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]  # 添加这行
    permission_classes = [IsAuthenticated]  # 添加这行

    def get(self, request):
        user = request.user
        serializer = UserInfoSerializer(user)
        # print(user,serializer,'userinfo')
        return Response(serializer.data)

class CustomJsonRender(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            response = renderer_context['response']
            code = 0 if response.status_code < 400 else response.status_code
            msg = 'success'
            res = {
                'code': code,
                'msg': msg,
                'data': data,
            }
            return super().render(res, accepted_media_type, renderer_context)
        return super().render(data, accepted_media_type, renderer_context)


class bookFilter(df_filters.FilterSet):
    name = df_filters.CharFilter(field_name='name', lookup_expr='icontains')
    author = df_filters.CharFilter(field_name='author')

    class Meta:
        model = Books
        fields = ['name', 'author']


class MyFormatResultsSetPagination(PageNumberPagination):
    page_size_query_param = "page_size"
    page_query_param = 'page'
    page_size = 10
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'results': data,
            'pagination': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,
            'page': self.page.start_index() // self.page.paginator.per_page + 1
        })


class BooksViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all().order_by('-author')
    serializer_class = BooksSerializer
    renderer_classes = (CustomJsonRender,)
    pagination_class = MyFormatResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_class = bookFilter
    search_fields = ['name', 'author']