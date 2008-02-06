#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2007 Ahmet AYGÜN
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from datetime import datetime

from django.http import HttpResponseRedirect, HttpResponseServerError, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from oi.forum.settings import *
from oi.forum.forms import *

from oi.st.wrappers import render_response
from oi.forum.models import Category, Forum, Topic, Post, AbuseReport, WatchList

from django.core.urlresolvers import reverse
from oi.st.models import Tag

def main(request):
    categories = Category.objects.order_by('order')

    return render_response(request, 'forum/forum_list.html', locals())

def forum(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topics = forum.topic_set.all().order_by('-sticky', '-topic_latest_post')

    return object_list(request, topics, template_name='forum/forum_detail.html', template_object_name='topic', extra_context={'forum': forum}, paginate_by=TOPICS_PER_PAGE, allow_empty=True)

def topic(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    posts = topic.post_set.all().order_by('created')

    session_key = 'visited_'+topic_id

    if request.user.is_authenticated() and not session_key in request.session:
        topic.views += 1
        request.session[session_key] = True
        topic.save()

    return render_response(request, 'forum/topic.html', locals())

@login_required
def reply(request, forum_slug, topic_id, post_id=False):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)

    posts = topic.post_set.all().order_by('-created')

    if forum.locked or topic.locked:
        raise HttpResponseServerError #FIXME: Give an error message

    if request.method == 'POST':
        form = PostForm(request.POST.copy())

        flood,timeout = flood_control(request)

        if form.is_valid() and not flood:
            post = Post(topic=topic,
                        author=request.user,
                        text=form.clean_data['text']
                       )
            post.save()

            return HttpResponseRedirect(post.get_absolute_url())
    else:
        if post_id:
            post = get_object_or_404(Post, pk=post_id)

            if post in topic.post_set.all():
                form = PostForm(auto_id=True, initial={'text': '[quote|'+post_id+']'+post.text+'[/quote]'})
        else:
            form = PostForm(auto_id=True)

    return render_response(request, 'forum/reply.html', locals())

@login_required
def edit_post(request, forum_slug, topic_id, post_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    post = get_object_or_404(Post, pk=post_id)

    if forum.locked or topic.locked:
        raise HttpResponseServerError #FIXME: Give an error message

    if request.method == 'POST':
        form = PostForm(request.POST.copy())

        flood,timeout = flood_control(request)

        if form.is_valid() and not flood:
            post.text = form.clean_data['text']
            post.edit_count += 1
            post.edited = datetime.now()
            post.last_edited_by = request.user
            post.save()

            return HttpResponseRedirect(post.get_absolute_url())
    else:
        if post in topic.post_set.all():
            form = PostForm(auto_id=True, initial={'text': post.text})

    return render_response(request, 'forum/reply.html', locals())

@login_required
def new_topic(request, forum_slug):
    forum = get_object_or_404(Forum, slug=forum_slug)

    if forum.locked:
        raise HttpResponseServerError #FIXME: Give an error message

    if request.method == 'POST':
        form = TopicForm(request.POST.copy())
        flood,timeout = flood_control(request)

        if form.is_valid() and not flood:
            topic = Topic(forum=forum,
                          title=form.clean_data['title'])

        #tags
            topic.save()

            for tag in form.clean_data['tags']:
                t=Tag.objects.get(name=tag)
                topic.tags.add(t)

            post = Post(topic=topic,
                        author=request.user,
                        text=form.clean_data['text'])

            post.save()

            return HttpResponseRedirect(post.get_absolute_url())
    else:
        form = TopicForm(auto_id=True)

    return render_response(request, 'forum/new_topic.html', locals())

@login_required
def edit_topic(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)
    first_post = topic.post_set.order_by('created')[0]

    if forum.locked or topic.locked:
        raise HttpResponseServerError #FIXME: Give an error message

    if request.method == 'POST':
        form = TopicForm(request.POST.copy())
        flood,timeout = flood_control(request)

        if form.is_valid() and not flood:
            topic.title = form.clean_data['title']
            topic.topic_latest_post = first_post
            topic.save()

            first_post.edit_count += 1
            first_post.edited = datetime.now()
            first_post.last_edited_by = request.user
            first_post.save()

            return HttpResponseRedirect(topic.get_absolute_url())
    else:
        form = TopicForm(auto_id=True, initial={'title': topic.title, 'text': first_post.text})

    return render_response(request, 'forum/new_topic.html', locals())

@login_required
def merge(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)

    if forum.locked or topic.locked:
        hata="Kilitli konularda bu tür işlemler yapılamaz!"
        return render_response(request, 'forum/merge.html', locals())
        
    if request.method == 'POST' and request.user.has_perm('forum.can_merge_topic'):
        form = MergeForm(request.POST.copy())
        flood,timeout = flood_control(request)

        if form.is_valid() and not flood:
            topic2 = form.clean_data['topic2']

            if int(topic2)==topic.id:
                hata="Aynı konuyu mu merge edeceksiniz !"
                return render_response(request, 'forum/merge.html', locals())


            topic2_object=get_object_or_404(Topic, pk=int(topic2))

            posts_tomove=Post.objects.filter(topic=topic.id)
            for post in posts_tomove:
                post.topic = topic2_object
                post.save()

            #bir de simdi ileti sayisini arttirmak gerekir.
            topic2_object.posts += posts_tomove.count()
            topic2_object.save()

            topic.delete()

            return HttpResponseRedirect(forum.get_absolute_url())

        else:
            hata="Forum valid degil veya floood yapıyorsun!"
            return render_response(request, 'forum/merge.html', locals())

    else:
        form = MergeForm(auto_id=True)

    return render_response(request, 'forum/merge.html', locals())

@login_required
def hide(request, forum_slug, topic_id, post_id=False):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.user.has_perm('forum.can_hide_post') and post_id:
        post = get_object_or_404(Post, pk=post_id)

        if post.hidden:
            post.hidden = 0
        else:
            post.hidden = 1

        post.save()

        return HttpResponseRedirect(topic.get_absolute_url())
    elif request.user.has_perm('forum.can_hide_topic') and not post_id:
        if topic.hidden:
            topic.hidden = 0
        else:
            topic.hidden = 1

        topic.save()

        return HttpResponseRedirect(forum.get_absolute_url())
    else:
        return HttpResponseServerError # FIXME: Given an error message

@login_required
def stick(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.user.has_perm('forum.can_stick_stopic') and not topic.sticky:
        topic.sticky = 1
        topic.save()

        return HttpResponseRedirect(forum.get_absolute_url())
    elif request.user.has_perm('forum.can_stick_topic') and topic.sticky:
        topic.sticky = 0
        topic.save()

        return HttpResponseRedirect(forum.get_absolute_url())
    else:
        return HttpResponseServerError # FIXME: Give an error message

@login_required
def lock(request, forum_slug, topic_id):
    forum = get_object_or_404(Forum, slug=forum_slug)
    topic = get_object_or_404(Topic, pk=topic_id)

    if request.user.has_perm('forum.can_lock_topic') and not topic.locked:
        topic.locked = 1
        topic.save()

        return HttpResponseRedirect(forum.get_absolute_url())
    elif request.user.has_perm('forum.can_lock_topic') and topic.locked:
        topic.locked = 0
        topic.save()

        return HttpResponseRedirect(forum.get_absolute_url())
    else:
        return HttpResponseServerError # FIXME: Give an error message

def flood_control(request):
    if 'flood_control' in request.session and ((datetime.now() - request.session['flood_control']).seconds < FLOOD_TIMEOUT):
        flood = True
        timeout = (FLOOD_TIMEOUT - (datetime.now() - request.session['flood_control']).seconds)
    else:
        flood = timeout = False
        request.session['flood_control'] = datetime.now()

    return flood,timeout
