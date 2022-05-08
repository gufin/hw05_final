from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import CommentForm, PostForm
from .models import Group, Post, Follow
from .utills import paginator_add

User = get_user_model()

POSTS_PER_PAGE = 10
HEADER_LENGTH = 30


def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.select_related('author').all()
    page_obj = paginator_add(post_list, POSTS_PER_PAGE, request)
    context = {
        'title': title,
        'page_obj': page_obj,
        'index': True
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    title = f'{group.title}'
    post_list = group.posts.all()
    page_obj = paginator_add(post_list, POSTS_PER_PAGE, request)
    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    # Здесь код запроса к модели и создание словаря контекста
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author_id=author.id)
    post_count = posts.count()
    page_obj = paginator_add(posts, POSTS_PER_PAGE, request)
    title = f'{author}'
    following = Follow.objects.filter(
        user_id=request.user.id,
        author_id=author.id
    ).exists()
    context = {
        'author': author,
        'post_count': post_count,
        'page_obj': page_obj,
        'title': title,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = context_for_detail(post)
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None)

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.pub_date = datetime.now()
            post.save()

            return redirect('posts:profile', request.user)
        else:
            title = 'Добавить запись'
            is_edit = False
            context = {
                'title': title,
                'form': form,
                'is_edit': is_edit
            }
            return render(request, 'posts/create_post.html', context)
    else:
        form = PostForm()
        title = 'Добавить запись'
        is_edit = False
        context = {
            'title': title,
            'form': form,
            'is_edit': is_edit
        }
        return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == "POST" and request.user == post.author:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id=post.pk)
    elif request.user == post.author:
        form = PostForm(instance=post)
        title = 'Отредактировать запись'
        context = {
            'form': form,
            'is_edit': True,
            'title': title,
        }
        return render(request, 'posts/create_post.html', context)
    else:
        context = context_for_detail(post)
        return render(request, 'posts/post_detail.html', context)


def context_for_detail(post):
    title = post.text[:HEADER_LENGTH]
    ps = Post.objects.select_related('author').filter(
        author_id=post.author_id)
    post_count = ps.count()
    comments = post.comments.all()
    form = CommentForm()
    return {
        'title': title,
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form': form
    }


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
    title = 'Мои подписки'
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_add(post_list, POSTS_PER_PAGE, request)
    context = {
        'title': title,
        'page_obj': page_obj,
        'index': False,
        'follow': True,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        user_id=request.user.id,
        author_id=author.id
    ).exists()
    if not following and not (request.user == author):
        Follow.objects.create(
            user_id=request.user.id,
            author_id=author.id
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow_record = Follow.objects.filter(
        user_id=request.user.id,
        author_id=author.id
    )
    following = follow_record.exists()
    if following:
        follow_record.delete()
    return redirect('posts:follow_index')
