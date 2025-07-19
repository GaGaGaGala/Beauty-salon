from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.list_of_services, name='list_of_services'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.update_profile, name='profile'),
    path('free_win/', views.free_window, name='free_window'),
    path('detail/manic/', views.list_detail_manic, name='manic'),
    path('detail/pedic/', views.detail_pedic, name='pedic'),
    path('detail/brows/', views.detail_brows, name='brows'),
    path('detail/hair/', views.detail_hair, name='hair'),
    path('price_list/', views.price_list, name='price_list'),
    path('price_manicure/', views.price_manicure, name='price_manicure'),
    path('price_pedicure/', views.price_pedicure, name='price_pedicure'),
    path('price_eyebrows/', views.price_eyebrows, name='price_eyebrows'),
    path('price_hair/', views.price_hair, name='price_hair'),
    path('about/', views.about_me, name='about'),
    path('portfolio/', views.port_im, name='port'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)