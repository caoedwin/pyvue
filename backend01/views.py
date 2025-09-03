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
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import random
from django.core.cache import cache
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from django.conf import settings

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



@method_decorator(csrf_exempt, name='dispatch')
class SendVerificationCodeView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code_type = request.data.get('type', 'register')

        if not phone:
            return Response({'error': '手机号不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证手机号码格式
        if not phone.startswith('1') or len(phone) != 11:
            return Response({'error': '手机号码格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        # 生成6位验证码
        code = ''.join(random.choices('0123456789', k=6))

        # 存储到缓存（5分钟有效）
        cache_key = f'{code_type}_code_{phone}'
        cache.set(cache_key, code, 300)

        # 发送短信
        try:
            self.send_sms(phone, code)
            return Response({'message': '验证码已发送'})
        except Exception as e:
            print(f'短信发送失败: {e}')
            return Response({'error': '短信发送失败，请稍后重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def send_sms(self, phone, code):
        """使用阿里云短信服务发送验证码"""
        # 创建AcsClient实例
        client = AcsClient(
            settings.ALIYUN_ACCESS_KEY_ID,
            settings.ALIYUN_ACCESS_KEY_SECRET,
            'default'
        )

        # 创建request对象
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')

        # 设置请求参数
        request.add_query_param('RegionId', "cn-hangzhou")
        request.add_query_param('PhoneNumbers', phone)
        request.add_query_param('SignName', settings.ALIYUN_SMS_SIGN_NAME)
        request.add_query_param('TemplateCode', settings.ALIYUN_SMS_TEMPLATE_CODE)
        request.add_query_param('TemplateParam', f'{{"code":"{code}"}}')

        # 发送请求
        response = client.do_action_with_exception(request)
        return response

# import requests
# import time
# import hashlib
# import random
# # 腾讯云短信服务（无需额外 SDK）
# class SendVerificationCodeView(APIView):
#     def send_sms(self, phone, code):
#         # 腾讯云短信服务API参数
#         secret_id = settings.TENCENT_SECRET_ID
#         secret_key = settings.TENCENT_SECRET_KEY
#         sdkappid = settings.TENCENT_SMS_APP_ID
#         sign_name = settings.TENCENT_SMS_SIGN_NAME
#         template_id = settings.TENCENT_SMS_TEMPLATE_ID
#
#         # 构造请求
#         url = "https://sms.tencentcloudapi.com/"
#         params = {
#             "Action": "SendSms",
#             "Version": "2021-01-11",
#             "Region": "ap-guangzhou",
#             "SmsSdkAppId": sdkappid,
#             "SignName": sign_name,
#             "TemplateId": template_id,
#             "PhoneNumberSet": [f"+86{phone}"],
#             "TemplateParamSet": [code]
#         }
#
#         # 生成签名
#         timestamp = int(time.time())
#         nonce = random.randint(1, 100000)
#         params["Timestamp"] = timestamp
#         params["Nonce"] = nonce
#
#         # 排序参数
#         sorted_params = sorted(params.items())
#         # 构造签名字符串
#         sign_str = "POSTsms.tencentcloudapi.com/?"
#         sign_str += "&".join([f"{k}={v}" for k, v in sorted_params])
#
#         # 计算签名
#         signature = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()
#         signature = hmac.new(secret_key.encode('utf-8'), signature.encode('utf-8'), hashlib.sha256).hexdigest()
#
#         # 添加签名头
#         headers = {
#             "Authorization": f"TC3-HMAC-SHA256 Credential={secret_id}, SignedHeaders=content-type;host, Signature={signature}",
#             "Content-Type": "application/json",
#             "X-TC-Action": "SendSms",
#             "X-TC-Timestamp": str(timestamp),
#             "X-TC-Version": "2021-01-11",
#             "X-TC-Region": "ap-guangzhou"
#         }
#
#         # 发送请求
#         response = requests.post(url, headers=headers, json=params)
#         return response.json()

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        code = request.data.get('code')
        password = request.data.get('password')

        # 验证验证码
        cache_key = f'register_code_{phone}'
        cached_code = cache.get(cache_key)

        if not cached_code or cached_code != code:
            return Response({'error': '验证码错误或已过期'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建用户
        user = UserInfo.objects.create(
            username=phone,
            account=phone,
            # ...其他字段
        )
        user.set_password(password)
        user.save()

        # 清除验证码
        cache.delete(cache_key)

        return Response({'message': '注册成功'})

@method_decorator(csrf_exempt, name='dispatch')
class ResetPasswordView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        # 实际项目中应验证token有效性
        user = UserInfo.objects.filter(account=phone).first()
        if not user:
            return Response({'error': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': '密码重置成功'})