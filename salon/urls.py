"""
URL configuration for salon project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from catalog import views as catalog_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', catalog_views.home, name='home'),
    path('base/', TemplateView.as_view(template_name='base.html')),
    path('catalog/', include('catalog.urls', namespace='catalog')),
    path('accounts/logout/', catalog_views.logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('catalog/signup', catalog_views.signup, name='signup'),
    path('catalog/list_of_services', catalog_views.list_of_services, name='list_of_services'),
    path('catalog/detail/manic/', catalog_views.list_detail_manic, name='manic'),
    path('catalog/detail/pedic/', catalog_views.detail_pedic, name='pedic'),
    path('catalog/detail/brows/', catalog_views.detail_brows, name='brows'),
    path('catalog/detail/hair/', catalog_views.detail_hair, name='hair'),
    path('catalog/free_window', catalog_views.free_window, name='free_window'),
    path('catalog/price_manicure', catalog_views.price_manicure, name='price_manicure'),
    path('catalog/price_pedicure', catalog_views.price_pedicure, name='price_pedicure'),
    path('catalog/price_eyebrows', catalog_views.price_eyebrows, name='price_eyebrows'),
    path('catalog/price_hair', catalog_views.price_hair, name='price_hair'),
    path('catalog/about', catalog_views.about_me, name='about'),
    path('catalog/portfolio', catalog_views.port_im, name='port'),
    path('catalog/price_list', catalog_views.price_list, name='price_list'),
    path('catalog/reg_manic', catalog_views.reg_for_manic, name='reg_man'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
