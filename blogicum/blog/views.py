from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.core.paginator import Paginator
from .models import Post, Category, Comment
from .forms import CommentForm
from django.views.decorators.http import require_http_methods
from django.http import Http404

from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    def get_success_url(self):
        return f"/profile/{self.request.user.username}/"
    
# Регистрация пользователя
class UserRegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("login")

# Профиль пользователя
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = Post.objects.filter(author=profile_user).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=profile_user,
            is_published=True,
            pub_date__lte=now(),
            category__is_published=True
        ).order_by('-pub_date')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/profile.html', {
        'profile': profile_user,
        'page_obj': page_obj,
    })

# Главная страница
def index(request):
    posts = Post.objects.filter(
        pub_date__lte=now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})

# Страница категории
def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=now()
    ).order_by('-pub_date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'blog/category.html',
        {'category': category, 'page_obj': page_obj}
    )

# Страница конкретного поста
def post_detail(request, id):
    post = get_object_or_404(Post, pk=id)

    if (
        request.user != post.author
        and (
            not post.is_published
            or not post.category.is_published
            or post.pub_date > now()
        )
    ):
        raise Http404

    comments = post.comments.order_by('created_at')
    form = CommentForm()

    return render(request, 'blog/detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
    })

# Форма создания поста
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'category', 'location', 'image', 'pub_date']

# Создание поста
@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})

# Редактирование профиля
@login_required
def edit_profile(request):
    user = request.user
    class CustomUserChangeForm(UserChangeForm):
        class Meta:
            model = User
            fields = ['first_name', 'last_name', 'username', 'email']

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=user.username)
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'blog/edit_profile.html', {'form': form})

@login_required
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)

    if request.user != post.author:
        return redirect('blog:post_detail', id=post.id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post.id)

    return render(request, 'blog/create.html', {'form': form})

@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, pk=id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', id=post.id)
        # даже при невалидной форме — редирект
        return redirect('blog:post_detail', id=post.id)
    # GET-запросов на add_comment быть не должно
    return redirect('blog:post_detail', id=post.id)

@login_required
@require_http_methods(["GET", "POST"])
def edit_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post__pk=id)

    if request.user != comment.author:
        return redirect('blog:post_detail', id=id)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comments.html', {
        'form': form,
        'post': comment.post,
        'comment': comment,
        'comments': comment.post.comments.order_by('created_at')
    })

@login_required
@require_http_methods(["GET", "POST"])
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id)
    if request.user != post.author:
        return redirect('blog:post_detail', id=id)

    if request.method == "POST":
        post.delete()
        return redirect('blog:profile', username=request.user.username)

    return render(request, 'blog/detail.html', {'post': post, 'confirm_delete': True})

@login_required
@require_http_methods(["GET", "POST"])
def delete_comment(request, id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post__pk=id)
    if request.user != comment.author:
        return redirect('blog:post_detail', id=id)

    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', id=id)

    return render(request, 'blog/comments.html', {
        'form': CommentForm(instance=comment),
        'post': comment.post,
        'comment': comment,
        'confirm_delete': True,
        'comments': comment.post.comments.order_by('created_at')
    })
