#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2009 TÜBİTAK UEKAE
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

import random, sha

from django.db import models

from oi.settings import CITY_LIST
from oi.middleware import threadlocals

class CdClient(models.Model):
    first_name = models.CharField("Ad", max_length=30)
    last_name = models.CharField("Soyad", max_length=30)
    email = models.EmailField("E-Posta")
    address = models.TextField("Adres")
    postcode = models.CharField("Posta Kodu", blank=True, max_length=5)
    town = models.CharField("İlçe", max_length=40)
    city = models.CharField("Şehir", choices=CITY_LIST, max_length=40)
    phone_area = models.CharField("Alan Kodu", max_length=3)
    phone_number = models.CharField("Telefon Numarası", max_length=7)
    ip = models.IPAddressField(blank=True, verbose_name='IP adresi')
    date = models.DateTimeField(auto_now_add=True)

    confirmed = models.BooleanField("Onaylandı")
    sent = models.BooleanField("Gönderildi")
    taken = models.BooleanField("Alındı")
    hash = models.CharField("Etkinleştirme Anahtarı", max_length=40)

    def get_full_name(self):
        return u"%s %s" % (self.first_name, self.last_name)

    def get_full_phone(self):
        return u"%s %s" % (self.phone_area, self.phone_number)

    def __unicode__(self):
        return self.get_full_name()

    def save(self):
        if not self.hash:
            random.seed()
            salt = sha.new(str(random.random())).hexdigest()
            self.hash = sha.new(salt).hexdigest()
        if not self.ip:
            self.ip = threadlocals.get_current_ip()
        super(CdClient, self).save()
