#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Uğur Çetin
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django.db import models
from django.contrib.auth.models import User

class PollVote(models.Model):
    option = models.ForeignKey("PollOption", verbose_name="Seçenek")
    voter = models.ForeignKey(User)
    voter_ip = models.IPAddressField(blank=True, verbose_name="IP Adresi")

    def __unicode__(self):
        return option

    class Admin:
        list_display = ("option", "voter", "voter_ip")
        ordering = ["option"]
        search_fields = ["voter_ip"]

    class Meta:
        verbose_name = "Anket Oyu"
        verbose_name_plural = "Anket Oyları"

class PollOption(models.Model):
    poll = models.ForeignKey("Poll", verbose_name="Anket")
    text = models.CharField("Yazı", max_length=128)
    vote_count = models.IntegerField(default=0, verbose_name="Oy sayısı")

    def __unicode__(self):
        if len(self.text) > 32:
            return "%s..." % self.question[:30]
        else:
            return self.text

    class Admin:
        list_display = ("poll", "text", "vote_count")
        ordering = ["poll"]
        search_fields = ["text"]

    class Meta:
        verbose_name = "Anket Seçeneği"
        verbose_name_plural = "Anket Seçenekleri"

class Poll(models.Model):
    question = models.CharField("Soru", max_length=128)
    allow_revoting = models.BooleanField("Oy Değiştirme")
    start_date = models.DateTimeField("Başlangıç Tarihi", auto_now_add=True)
    end_date = models.DateTimeField("Bitiş Tarihi")

    def __unicode__(self):
        if len(self.question) > 32:
            return "%s..." % self.question[:30]
        else:
            return self.question

    class Admin:
        list_display = ("question", "allow_revoting", "start_date", "end_date")
        ordering = ["-start_date"]
        search_fields = ["question"]

    class Meta:
        verbose_name = "Anket"
        verbose_name_plural = "Anketler"