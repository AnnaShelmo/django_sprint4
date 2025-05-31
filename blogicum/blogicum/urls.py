from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import UserRegisterView, CustomLoginView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/registration/', UserRegisterView.as_view(), name='registration'),
    path('auth/login/', CustomLoginView.as_view(), name='login'),
    path("auth/", include("django.contrib.auth.urls")),
    
]

handler403 = 'blogicum.views.custom_permission_denied_view'
handler404 = 'blogicum.views.custom_page_not_found_view'
handler500 = 'blogicum.views.custom_server_error_view'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
