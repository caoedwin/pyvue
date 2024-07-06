from django.shortcuts import render

from django.views.decorators.http import require_http_methods
from django.http import HttpResponse,JsonResponse
import json
from .models import Books
# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import BasePermission
from .models import Books, UserInfo
from .serializer import BooksSerializer

# 自定义权限
class MyPermission(BasePermission):
    message = 'VIP用户才能访问'

    def has_permission(self, request, view):
        """
        自定义权限只有VIP用户才能访问
        """
        # 因为在进行权限判断之前已经做了认证判断，所以这里可以直接拿到request.user
        # print(request.user)
        # if request.user and request.user.type == 2:  # 如果是VIP用户
        #     return True
        # else:
        #     return False
        current_user = request.session.get('user_name')
        onlineuser = request.session.get('account')
        roles = []
        onlineuser = request.session.get('account')
        # print(UserInfo.objects.get(account=onlineuser))
        for i in UserInfo.objects.get(account=onlineuser).role.all():
            roles.append(i.name)
        # print(roles)
        if onlineuser and 'admin' in roles:# 如果DQA用户
            return True
        else:
            return False


from rest_framework.renderers import JSONRenderer
class CustomJsonRender(JSONRenderer):
    """ 自定义返回数据 Json格式
    {
        "code": 0,
        "msg": "success",
        "data": { ... }
    }
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context:
            # print(renderer_context)
            # print(renderer_context['request'])
            print(renderer_context['request'].method)
            if renderer_context['request'].method == "GET":
                print(renderer_context['request'].GET)
            if renderer_context['request'].method == "POST":
                print(renderer_context['request'].POST)
                #print(renderer_context['request'].body)#会报错“django.http.request.RawPostDataException: You cannot access body after reading from request's data stream”显然，一旦你使用django-rest-framework，你必须使用request.data
                print(renderer_context['request'].data)#根据获得的参数就可以通过数据处理再json数据res中返回前端定制的数据
            response = renderer_context['response']
            # print(response)
            code = 0 if int(response.status_code / 100) == 2 else response.status_code
            msg = 'success'
            if isinstance(data, dict):
                msg = data.pop('msg', msg)
                code = data.pop('code', code)
                data = data.pop('data', data)
            if code != 0 and data:
                msg = data.pop('detail', 'failed')
            response.status_code = 200
            res = {
                'code': code,
                'msg': msg,
                'data': data,
            }
            # print(res)
            return super().render(res, accepted_media_type, renderer_context)
        else:
            return super().render(data, accepted_media_type, renderer_context)


from django_filters import rest_framework as df_filters
from .models import *
class bookFilter(df_filters.FilterSet):
    """
    过滤器
    """
    name = df_filters.CharFilter(field_name='name', lookup_expr='icontains')
    author = df_filters.CharFilter(field_name='author')
    # add_time = django_filters.CharFilter(name='add_time')

    class Meta:
        model = Books
        fields = ['name', 'author', ]

from rest_framework.pagination import PageNumberPagination
from rest_framework.pagination import Response
class MyFormatResultsSetPagination(PageNumberPagination):

    page_size_query_param = "page_size"
    page_query_param = 'page'
    page_size = 10
    max_page_size = 1000

    """
    自定义分页方法
    """
    def get_paginated_response(self, data):
        """
        设置返回内容格式
        """
        return Response({
            'results': data,
            'pagination': self.page.paginator.count,
            'page_size': self.page.paginator.per_page,
            'page': self.page.start_index() // self.page.paginator.per_page + 1
        })

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django_filters import rest_framework
class BooksViewSet(viewsets.ModelViewSet):
    queryset = Books.objects.all().order_by('-author')
    serializer_class = BooksSerializer
    renderer_classes = (CustomJsonRender,)
    # permission_classes = [MyPermission, ]#可以参考DDIS里面的CQM和PersonalInfo接口，和DMS里面的app01里面的ImportPersonalInfo登录获取token后获取数据
    pagination_class = MyFormatResultsSetPagination
    filter_backends = (rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_class = bookFilter
    search_fields = ['name', 'author', ]