#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2010 TÜBİTAK UEKAE
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from oi.forum.models import Topic
# Create your models here.


voteChoices = (
            ( 'U', '+1'),
            ( 'D', '-1'),
            ( 'N', ' 0'),
)


class Idea(models.Model):
    title = models.CharField(max_length = 128)
    description = models.TextField()
    dateSubmitted = models.DateTimeField("date submitted",default=datetime.now())
    submitter = models.ForeignKey(User, related_name="idea_submitter")
    status = models.ForeignKey("Status", blank=True, null=True)
    category = models.ForeignKey("Category", blank=True, null=True)
    duplicate = models.ForeignKey("self", blank=True, null=True)
    is_duplicate = models.BooleanField("Idea Duplicate", default=False)
    is_hidden = models.BooleanField("Hiddden", default=False)
    topic = models.ForeignKey(Topic, related_name="Idea_topic")
    vote_count = models.IntegerField(default=0)
    vote_value = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

class Status(models.Model):
    name = models.CharField(max_length = 128)
    
    def __unicode__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length = 128)
    
    def __unicode__(self):
        return self.name

class Vote(models.Model):
    idea = models.ForeignKey("Idea")
    voter = models.ForeignKey(User, related_name = "voter_user")
    vote = models.CharField(max_length = 1, choices = voteChoices)
    
    def __unicode__(self):
        return self.vote

class ScreenShot(models.Model):
    idea = models.ForeignKey("Idea")
    image = models.ImageField(upload_to = "beyin2/")
    
    def __unicode__(self):
        return self.image.file.name



