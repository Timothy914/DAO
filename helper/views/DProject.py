from django import forms
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from ..models import *
from .settings import *
import datetime
import math


class ModifyForm(forms.Form):
    title = forms.CharField(label='标题', max_length=50,
                            widget=forms.TextInput(attrs={'class': 'form-control form-control-user mb-5'}))
    content = forms.CharField(label='项目描述', widget=forms.Textarea(attrs={'class': 'form-control form-control-user mb-5'}))


@login_required
def home(request):
    user = request.user

    dprojects = DProject.objects.filter(user_id__exact=user.id).order_by('-modified_time')
    collections = Collection.objects.filter(user_id__exact=user.id).order_by('-dproject__collect_amount')
    return render(request, '../templates/dproject/home.html',
                  {
                      'dprojects': dprojects,
                      'collections': collections
                  })


@login_required
def dproject(request, pk):
    dproject = get_object_or_404(DProject, pk=pk)
    user: User = request.user
    if user.collection_set.filter(dproject_id__exact=dproject.pk).count() == 0:
        is_collected = False
    else:
        is_collected = True
    comments = dproject.comment_set.all().order_by('created_time')
    if request.method == 'POST':
        delete_comment = request.POST.get('delete_comment')
        create_comment = request.POST.get('create_comment')
        collect_dproject = request.POST.get('collect_dproject')
        if not (delete_comment is None):
            try:
                comment = Comment.objects.filter(user_id__exact=user.id,
                                                 dproject_id__exact=dproject.id,
                                                 content__exact=delete_comment)[0]
                comment.delete()
            except IndexError:
                pass

        if not (collect_dproject is None):
            collection = Collection.objects.filter(user_id__exact=user.id, dproject_id__exact=dproject.id)
            if len(collection) == 0:
                new_collection = Collection(user=user, dproject=dproject)
                dproject.collect_amount += 1
                dproject.save()
                new_collection.save()
                is_collected = True
            else:
                collection.delete()
                is_collected = False

        if not (create_comment is None):
            new_comment = Comment(user=user, dproject=dproject, content=create_comment)
            new_comment.save()
    else:
        dproject.pageview += 1
        dproject.save()

    return render(request, '../templates/dproject/dproject.html',
                  {'dproject': dproject, 'comments': comments, 'user': user, 'is_collected': is_collected})


@login_required
def modify(request, pk):
    dproject = get_object_or_404(DProject, pk=pk)
    if dproject.user != request.user:
        return HttpResponseForbidden

    if request.method == "POST":
        form = ModifyForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            dproject.title = title
            dproject.content = content
            dproject.save()
            return HttpResponseRedirect(reverse('helper:dproject_page', args=(dproject.id,)))
    else:
        form = ModifyForm(initial={'title': dproject.title, 'content': dproject.content})

    return render(request, '../templates/dproject/modify.html', {'form': form})


@login_required
def delete(request, pk):
    dproject = get_object_or_404(DProject, pk=pk)
    if dproject.user != request.user:
        return HttpResponseForbidden
    dproject.delete()
    return HttpResponseRedirect(reverse("helper:dproject_homepage"))


@login_required
def add(request):
    user = request.user

    if request.method == "POST":
        form = ModifyForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            dproject = DProject(user=user, title=title, content=content)
            dproject.save()
            return HttpResponseRedirect(reverse('helper:dproject_page', args=(dproject.id,)))
    else:
        form = ModifyForm()

    return render(request, '../templates/dproject/modify.html', {'form': form})


def hot(request, pg):
    dprojects = DProject.objects.filter(Q(user__dproject__pageview__gte=HOT_BLOG_PAGEVIEW,
                                  modified_time__gte = timezone.now() -
                                                       datetime.timedelta(days=BLOGPAGE_HOT_BLOG_DAY)) |
                                Q(modified_time__gte = timezone.now() -
                                                       datetime.timedelta(days=BLOGPAGE_COMMON_BLOG_DAY))).distinct().order_by('-modified_time')
    page_num = math.ceil(len(dprojects) / BLOGPAGE_BLOG_NUMBER)
    if pg > page_num or pg < 1:
        return HttpResponseNotFound()

    if pg * BLOGPAGE_BLOG_NUMBER > len(dprojects):
        number = len(dprojects)
    else:
        number = pg * BLOGPAGE_BLOG_NUMBER

    dprojects = dprojects[(pg - 1) * BLOGPAGE_BLOG_NUMBER: number]
    return render(request, '../templates/dproject/hot.html',
                  {
                      'dprojects': dprojects,
                      'page_num': page_num,
                      'current_page': pg
                  })


@login_required
def public(request, friend_id):
    user: User = request.user
    friend = Friend.objects.filter(user_id__exact=user.id, friend_id__exact=friend_id)
    if len(friend) == 0 and friend_id != user.id:
        return HttpResponseForbidden()
    dprojects = DProject.objects.filter(user_id__exact=friend_id)
    message = None
    if friend_id == user.id:
        friend_user = user
    else:
        friend_user = friend[0].friend
        if friend[0].authority == 0:
            dprojects = None
            message = "没有权限访问！"

    return render(request, '../templates/dproject/friend.html',
                  {
                      'dprojects': dprojects,
                      'friend': friend_user,
                      'message': message
                  })
