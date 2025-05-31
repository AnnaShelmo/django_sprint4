from django.shortcuts import render

def custom_permission_denied_view(request, exception):
    return render(request, "pages/403csrf.html", status=403)

def custom_page_not_found_view(request, exception):
    return render(request, "pages/404.html", status=404)

def custom_server_error_view(request):
    return render(request, "pages/500.html", status=500)
