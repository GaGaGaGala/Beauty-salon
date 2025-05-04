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
    path('catalog/list_detail', catalog_views.list_detail, name='list_detail'),
    path('catalog/free_window', catalog_views.free_window, name='free_window'),
    path('catalog/price_manicure', catalog_views.price_manicure, name='price_manicure'),
    path('catalog/portfolio', catalog_views.portfolio, name='portfolio'),
    path('catalog/price_list', catalog_views.price_list, name='price_list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
