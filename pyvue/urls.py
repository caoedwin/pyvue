from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from backend01 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('backend01.urls')),
    path('IntelligentCabinet/', include('IntelligentCabinet.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('', TemplateView.as_view(template_name='index.html')),
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),  # 捕获所有路由
]