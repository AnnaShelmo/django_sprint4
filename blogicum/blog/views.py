from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.http import Http404
from django.db.models import Count

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    def get_success_url(self):
        return reverse_lazy("blog:profile", kwargs={"username": self.request.user.username})


class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("login")


def filter_published_posts(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=now(),
        category__is_published=True,
    )


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = get_posts_with_comment_count(Post.objects.filter(author=profile_user))
    else:
        posts = get_posts_with_comment_count(filter_published_posts(Post.objects.filter(author=profile_user)))
    page_obj = paginate_queryset(posts, request)
    return render(
        request,
        "blog/profile.html",
        {"profile": profile_user, "page_obj": page_obj},
    )


def index(request):
    posts = get_posts_with_comment_count(filter_published_posts(Post.objects.all()))
    page_obj = paginate_queryset(posts, request)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, is_published=True)
    posts = get_posts_with_comment_count(filter_published_posts(Post.objects.filter(category=category)))
    page_obj = paginate_queryset(posts, request)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj},
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author and (
        not post.is_published
        or not post.category.is_published
        or post.pub_date > now()
    ):
        raise Http404

    comments = post.comments.order_by("created_at")
    form = CommentForm()

    return render(
        request,
        "blog/detail.html",
        {"post": post, "comments": comments, "form": form},
    )


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/create.html", {"form": form})


@login_required
def edit_profile(request):
    user = request.user

    class CustomUserChangeForm(UserChangeForm):
        class Meta:
            model = User
            fields = ["first_name", "last_name", "username", "email"]

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=user.username)
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, "blog/edit_profile.html", {"form": form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect("blog:post_detail", post_id=post.id)

    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post.id)

    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("blog:post_detail", post_id=post.id)
        return redirect("blog:post_detail", post_id=post.id)
    return redirect("blog:post_detail", post_id=post.id)


@login_required
@require_http_methods(["GET", "POST"])
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post__pk=post_id)

    if request.user != comment.author:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(
        request,
        "blog/detail.html",
        {
            "form": form,
            "post": comment.post,
            "comment": comment,
            "comments": comment.post.comments.order_by("created_at"),
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)

    return render(request, "blog/detail.html", {"post": post, "confirm_delete": True})


@login_required
@require_http_methods(["GET", "POST"])
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post__pk=post_id)

    if request.user != comment.author:
        return redirect("blog:post_detail", post_id=post_id)

    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)

    return render(
        request,
        "blog/detail.html",
        {
            "post": comment.post,
            "comment": comment,
            "comments": comment.post.comments.order_by("created_at"),
            "confirm_delete": True,
        },
    )


def get_posts_with_comment_count(queryset):
    return queryset.annotate(comment_count=Count("comments")).order_by("-pub_date")


def paginate_queryset(queryset, request, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
