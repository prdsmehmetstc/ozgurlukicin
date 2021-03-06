#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2009 TÜBİTAK UEKAE
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from django.shortcuts import get_object_or_404, redirect
from django.core.mail import EmailMessage
from django.template import Context, loader
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.db.models import Q

from oi.shipit.forms import *
from oi.shipit.models import *
from oi.shipit.settings import *
from oi.st.wrappers import render_response
from oi.settings import DEFAULT_FROM_EMAIL
from oi.forum.views import flood_control
from oi.settings import WEB_URL, CITY_LIST


def create_cdclient(request):
    if request.method == "POST":
        form = CdClientForm(request.POST.copy())
        flood, timeout = flood_control(request)
        if form.is_valid() and not flood:
            cdClient = form.save()
            message = loader.get_template("shipit/confirm_email.html").render(Context({"cdClient":cdClient}))
            mail = EmailMessage("Pardus DVD isteğiniz", message, "Özgürlükiçin <%s>" % DEFAULT_FROM_EMAIL, ["%s <%s>" % (cdClient.get_full_name(), cdClient.email)])
            mail.content_subtype = "html"
            mail.send(fail_silently=True)
            return render_response(request, "shipit/sent.html", locals())
    else:
        initial = {}
        if request.user.is_authenticated():
            initial["first_name"] = request.user.first_name
            initial["last_name"] = request.user.last_name
            initial["email"] = request.user.email
            initial["city"] = request.user.get_profile().city
        form = CdClientForm(initial=initial)
    return render_response(request, "shipit/create_cdclient.html", locals())

def confirm_cdclient(request, id, hash):
    cdClient = get_object_or_404(CdClient, id=id, hash=hash, confirmed=False)
    if CdClient.objects.filter(tcidentity=cdClient.tcidentity, confirmed=True).count()>0:
        return HttpResponse("Bu TC kimlik numarası daha önce kullanılmış!")
    cdClient.confirmed = True
    cdClient.save()
    #send mail to lists
    message = loader.get_template("shipit/confirmed_email.html").render(Context({"cdClient":cdClient,"WEB_URL":WEB_URL}))
    mail = EmailMessage(
        "Pardus DVD isteği",
        message,
        "Özgürlükiçin <%s>" % DEFAULT_FROM_EMAIL,
        [DVD_MAIL_LIST],
        headers={"Message-ID":"%s-%s" % (cdClient.id, cdClient.hash)}
    )
    mail.content_subtype = "html"
    mail.send(fail_silently=True)

    return render_response(request, "shipit/confirmed.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_list(request):
    if request.method == "POST":
        form = SearchForm(request.POST.copy())
        if form.is_valid():
            term = form.cleaned_data["term"]
            cdClient_list = CdClient.objects.filter(Q(first_name__icontains=term)|Q(last_name__icontains=term)|Q(address__icontains=term)|Q(phone_number__icontains=term)).filter(sent=False, confirmed=True)
    else:
        form = SearchForm()

    return render_response(request, "shipit/cdclient_list.html", locals())

@permission_required("shipit.change_cdclient")
def change_cdclient(request, id):
    cdClient = get_object_or_404(CdClient, id=id)
    if request.method == "POST":
        form = CdClientChangeForm(request.POST, instance=cdClient)
        if form.is_valid():
            form.save()
    else:
        form = CdClientChangeForm(instance=cdClient)
    return render_response(request, "shipit/change_cdclient.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_detail(request, id):
    cdClient = get_object_or_404(CdClient, id=id)
    cargo = Cargo.objects.filter(cdclient=cdClient)
    return render_response(request, "shipit/cdclient_detail.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_cargo(request, id):
    cdClient = get_object_or_404(CdClient, id=id)
    if request.method == "POST":
        form = CargoForm(request.POST.copy())
        if form.is_valid():
            cargo = form.save(commit=False)
            cargo.cdclient = cdClient
            cargo.save()
            message = loader.get_template("shipit/sent_email.html").render(Context({"cdClient":cdClient,"cargo":cargo}))
            mail = EmailMessage(
                "Pardus DVD isteğiniz",
                message,
                "Özgürlükiçin <%s>" % DEFAULT_FROM_EMAIL,
                [DVD_MAIL_LIST, cdClient.email],
                headers={"Message-ID":"%s-%s" % (cdClient.id, cdClient.hash)}
            )
            mail.content_subtype = "html"
            mail.send(fail_silently=True)
            cdClient.sent = True
            cdClient.save()

            return HttpResponseRedirect(cdClient.get_absoulte_url())
    else:
        form = CargoForm()
    return render_response(request, "shipit/cargo.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_list_to_send(request, version_slug=None):
    if version_slug != None:
        version = get_object_or_404(PardusVersion, slug=version_slug)
        cdclient_list = CdClient.objects.filter(confirmed=True, sent=False, version=version)
    else:
        cdclient_list = CdClient.objects.filter(confirmed=True, sent=False)
    show_date = request.GET.has_key("date")
    return render_response(request, "shipit/clients_to_send.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_list_sent(request, version_slug=None):
    if version_slug != None:
        version = get_object_or_404(PardusVersion, slug=version_slug)
        cdclient_list = CdClient.objects.filter(confirmed=True, sent=True, version=version)
    else:
        cdclient_list = CdClient.objects.filter(confirmed=True, sent=True)
    show_date = request.GET.has_key("date")
    return render_response(request, "shipit/clients_to_send.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_list_delivered(request):
    cargo_list = Cargo.objects.all()
    show_date = request.GET.has_key("date")
    return render_response(request, "shipit/clients_delivered.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_list_not_sent(request, version_slug=None):
    if version_slug != None:
        version = get_object_or_404(PardusVersion, slug=version_slug)
        cdclient_list = CdClient.objects.filter(confirmed=True, sent=False, version=version).order_by('-date')
    else:
        cdclient_list = CdClient.objects.filter(confirmed=True, sent=False).order_by('-date')
    count = 0
    for client in cdclient_list:
        if not client.sent:
            count += 1
    show_date = request.GET.has_key("date")
    return render_response(request, "shipit/clients_not_sent.html", locals())

@permission_required("shipit.change_cdclient")
def cdclient_list_cities(request):
    city_list = []
    for city in CITY_LIST:
        city_list.append((CdClient.objects.filter(sent=True, city=city[0]).count(), city[1]))
    city_list.sort()
    city_list.reverse()
    total = CdClient.objects.filter(sent=True).count()
    return render_response(request, "shipit/city_list.html", locals())

def redirect_to_new_url(request):
    return redirect('/dvdgonder/')
