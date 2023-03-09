from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.cache import cache_page
from django.core.paginator import Paginator
from django.conf import settings
from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups_posts.all()
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author__username=author).count()
    post_list = Post.objects.filter(author__username=author)
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    user = request.user
    following = (
        user.is_authenticated
        and Follow.objects.
        filter(user=user, author=author).exists()
    )
    context = {
        'page_obj': page_obj,
        'posts_count': posts_count,
        'author': author,
        'following': following,
        'user': user,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = User.objects.get(id=post.author_id)
    comments = Comment.objects.filter(post_id=post_id)
    posts_count = Post.objects.filter(author__username=author).count()
    form = CommentForm()
    context = {
        'post': post,
        'posts_count': posts_count,
        'author': author,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect(f'/profile/{new_post.author}/')
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None,
                        files=request.FILES or None,
                        instance=post
                        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        else:
            context = {
                'post': post,
                'form': form,
                'is_edit': True,
            }
            return render(request, 'posts/create_post.html', context)
    form = PostForm(instance=post)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, settings.NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        Follow.objects.create(author=user, user=request.user)
    return render(request, 'posts/index.html')


@login_required
def profile_unfollow(request, username):
    user = User.objects.get(username=username)
    Follow.objects.filter(author=user, user=request.user).delete()
    return render(request, 'posts/index.html')
