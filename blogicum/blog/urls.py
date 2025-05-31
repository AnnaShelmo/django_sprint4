from django.urls import path
from .views import (
    index, category_posts, post_detail, create_post,
    profile, UserRegisterView, edit_profile, edit_post, edit_comment, add_comment, delete_post, delete_comment
)

app_name = "blog"

urlpatterns = [
    path("", index, name="index"),
    path("category/<slug:category_slug>/", category_posts, name="category_posts"),
    path("posts/<int:id>/", post_detail, name="post_detail"),
    path("posts/create/", create_post, name="create_post"),
    path("auth/registration/", UserRegisterView.as_view(), name="registration"),
    path("profile/<str:username>/", profile, name="profile"),
    path("edit-profile/", edit_profile, name="edit_profile"),
    path('posts/<int:id>/edit/', edit_post, name='edit_post'),
    path('posts/<int:id>/comment/', add_comment, name='add_comment'),
    path('posts/<int:id>/edit_comment/<int:comment_id>/', edit_comment, name='edit_comment'),
    path('posts/<int:id>/delete/', delete_post, name='delete_post'),
    path('posts/<int:id>/delete_comment/<int:comment_id>/', delete_comment, name='delete_comment'),  
]
