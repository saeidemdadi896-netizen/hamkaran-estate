from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .models import AgentProfile, OrdinaryUserProfile, Listing, Request, Proposal
from .forms import (
    RegisterForm,
    OrdinaryUserRegisterForm,
    ProfileForm,
    ListingForm,
    RequestForm,
    ProposalForm,
)

def home(request):
    listings = Listing.objects.filter(moderation="approved").order_by("-created_at")[:6]
    return render(request, "estate/home.html", {"listings": listings})

def agents(request):
    agents = AgentProfile.objects.filter(status="approved")
    return render(request, "estate/agents.html", {"agents": agents})

def agent_detail(request, pk):
    agent = get_object_or_404(AgentProfile, pk=pk, status="approved")
    listings = agent.listings.filter(moderation="approved")
    return render(request, "estate/agent_detail.html", {"agent": agent, "listings": listings})

def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk, moderation="approved")
    return render(request, "estate/listing_detail.html", {"listing": listing})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            messages.success(request, "درخواست عضویت شما با موفقیت ثبت شد و پس از تأیید فعال خواهد شد.")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "estate/form.html", {"form": form, "title": "ثبت‌نام مشاور / همکار"})

def ordinary_signup(request):
    if request.user.is_authenticated:
        messages.info(request, "شما قبلاً وارد حساب کاربری شده‌اید.")
        return redirect("home")

    if request.method == "POST":
        form = OrdinaryUserRegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                full_name = form.cleaned_data["full_name"].strip()
                OrdinaryUserProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    phone=form.cleaned_data["phone"].strip(),
                    city=form.cleaned_data.get("city", "").strip(),
                )
            messages.success(request, "حساب کاربری شما با موفقیت ساخته شد. اکنون می‌توانید وارد شوید.")
            return redirect("login")
    else:
        form = OrdinaryUserRegisterForm()
    return render(request, "estate/form.html", {"form": form, "title": "ثبت‌نام کاربر عادی"})

def logout_view(request):
    logout(request)
    messages.info(request, "از حساب کاربری خارج شدید.")
    return redirect("home")

@login_required
def dashboard(request):
    return render(request, "estate/dashboard.html")

@login_required
def profile_edit(request):
    return render(request, "estate/form.html", {"title": "ویرایش پروفایل"})

@login_required
def listing_create(request):
    return render(request, "estate/form.html", {"title": "ثبت ملک جدید"})

@login_required
def listing_edit(request, pk):
    return render(request, "estate/form.html", {"title": "ویرایش ملک"})

def requests_board(request):
    requests_list = Request.objects.all()
    return render(request, "estate/requests.html", {"requests": requests_list})

@login_required
def request_create(request):
    return render(request, "estate/form.html", {"title": "ثبت درخواست خرید/اجاره"})

def request_detail(request, pk):
    req = get_object_or_404(Request, pk=pk)
    return render(request, "estate/requests.html", {"request_item": req})
