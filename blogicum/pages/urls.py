from django.urls import path
from .views import AboutView, RulesView

app_name = "pages"

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
    path("rules/", RulesView.as_view(), name="rules"),
]

handler403 = "pages.views.custom_permission_denied_view"
handler404 = "pages.views.custom_page_not_found_view"
handler500 = "pages.views.custom_server_error_view"
