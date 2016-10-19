from urllib.parse import quote_plus

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import PostForm
from .models import Post


def post_list(request):
    today = timezone.now().date()
    posts_list = Post.objects.all()
    if request.user.is_staff or request.user.is_superuser:
        posts_list = Post.objects.all()
    
    query = request.GET.get('q') 
    if query:
        posts_list = posts_list.filter(
                Q(title__icontains=query)|
                Q(content__icontains=query)|
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
                ).distinct()

    paginator = Paginator(posts_list, 2)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)        

    context = {
        'posts': posts,
        'title':'List',
        'today': today
    }
    return render(request, 'post_list.html', context)

def post_create(request):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Successfully created")
        return HttpResponseRedirect(instance.get_absolute_url())

    context = {
        'form': form
    }
    return render(request, 'post_form.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if post.publish > timezone.now().date() or post.draft:
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    context = {
        'post': post
    }
    return render(request, 'post_detail.html', context)

def post_update(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    post = get_object_or_404(Post, id=id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully saved")
        return HttpResponseRedirect(instance.get_absolute_url())
        
    context = {
        'title': post.title,
        'post': post,
        'form': form
    }
    return render(request, 'post_form.html', context)

def post_delete(request, id=None):
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    post = get_object_or_404(Post, id=id)
    post.delete()
    messages.success(request, "Successfully deleted")
    return redirect('posts:list')
