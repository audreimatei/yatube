from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page
from posts.forms import CommentForm, GroupForm, PostForm, ProfileForm
from posts.models import Comment, Follow, Group, Post, Profile, User
from posts.utils import get_page_obj

from yatube.settings import CACHE_TIMEOUT, CHARS_SHOWN


@cache_page(timeout=CACHE_TIMEOUT, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    context = {
        'page_name': 'index',
        'page_obj': get_page_obj(request, posts),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'page_obj': get_page_obj(request, posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author)
    followers_num = Follow.objects.filter(author=author).count()
    following_num = Follow.objects.filter(user=author).count()
    context = {
        'author': author,
        'posts_num': posts.count(),
        'page_obj': get_page_obj(request, posts),
        'followers_num': followers_num,
        'following_num': following_num
    }
    if request.user.is_authenticated:
        context['following'] = Follow.objects.filter(
            user=request.user, author=author).exists()
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    num_posts = Post.objects.filter(author=post.author).count()
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'num_posts': num_posts,
        'num_comments': comments.count(),
        'CHARS_SHOWN': CHARS_SHOWN,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user == post.author:
        Post.objects.filter(id=post_id).delete()
    return redirect('posts:profile', post.author.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post_id': post.id
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    redirect_url = reverse(
        'posts:post_detail',
        kwargs={'post_id': post_id}
    ) + '#comments'
    return redirect(redirect_url)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).values_list(
        'author', flat=True)
    posts = Post.objects.filter(author__in=following)
    context = {
        'page_name': 'follow_index',
        'page_obj': get_page_obj(request, posts)
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username)


@login_required
def profile_edit(request, username):
    if request.user.username != username:
        return redirect('posts:profile', username)
    profile = get_object_or_404(Profile, user=request.user)
    form = ProfileForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=profile
    )
    if form.is_valid():
        form.save()
        return redirect('posts:profile', username)
    context = {
        'form': form,
        'username': username
    }
    return render(request, 'posts/profile_edit.html', context)


@login_required
def group_create(request):
    form = GroupForm(
        data=request.POST or None,
    )
    if form.is_valid():
        group = form.save(commit=False)
        group.creator = request.user
        group.save()
        return redirect('posts:group_list', group.slug)
    return render(request, 'posts/group_create.html', {'form': form})


@login_required
def group_edit(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if request.user != group.creator:
        return redirect('posts:group_list', group.slug)
    form = GroupForm(
        data=request.POST or None,
        instance=group
    )
    if form.is_valid():
        form.save()
        return redirect('posts:group_list', group.slug)
    context = {
        'form': form,
        'slug': group.slug
    }
    return render(request, 'posts/group_create.html', context)


@login_required
def group_delete(request, slug):
    group = get_object_or_404(Group, slug=slug)
    if request.user == group.creator:
        Group.objects.filter(slug=group.slug).delete()
    return redirect('posts:index')
