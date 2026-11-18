from functools import wraps
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import AgentProfile, Listing, Request, Proposal
from .forms import RegisterForm, ProfileForm, ListingForm, RequestForm, ProposalForm

def approved_required(view):
    @wraps(view)
    @login_required
    def wrapped(request,*args,**kwargs):
        p=getattr(request.user,"profile",None)
        if not p or p.status!="approved": return render(request,"estate/pending.html",status=403)
        return view(request,*args,**kwargs)
    return wrapped

def home(request):
    qs=Listing.objects.filter(moderation="approved").filter(Q(expires_at__isnull=True)|Q(expires_at__gte=timezone.localdate()))
    q=request.GET.get("q",""); city=request.GET.get("city",""); mode=request.GET.get("mode","")
    if q: qs=qs.filter(Q(title__icontains=q)|Q(neighborhood__icontains=q)|Q(description__icontains=q))
    if city: qs=qs.filter(city__icontains=city)
    if mode: qs=qs.filter(mode=mode)
    return render(request,"estate/home.html",{"listings":qs.order_by("-created_at"),"q":q,"city":city,"mode":mode})
def agents(request):
    qs=AgentProfile.objects.filter(status="approved").select_related("user")
    q=request.GET.get("q","")
    if q: qs=qs.filter(Q(full_name__icontains=q)|Q(city__icontains=q)|Q(specialties__icontains=q))
    return render(request,"estate/agents.html",{"agents":qs,"q":q})
def agent_detail(request,pk):
    p=get_object_or_404(AgentProfile,pk=pk,status="approved")
    return render(request,"estate/agent_detail.html",{"agent":p})
def listing_detail(request,pk):
    listing=get_object_or_404(Listing,pk=pk,moderation="approved")
    if listing.expires_at and listing.expires_at<timezone.localdate(): raise Http404
    member=request.user.is_authenticated and getattr(getattr(request.user,"profile",None),"status",None)=="approved"
    return render(request,"estate/listing_detail.html",{"listing":listing,"member":member})
def register(request):
    if request.method=="POST":
        f=RegisterForm(request.POST)
        if f.is_valid():
            u=User.objects.create_user(f.cleaned_data["username"],password=f.cleaned_data["password"])
            AgentProfile.objects.create(user=u,full_name=f.cleaned_data["full_name"],phone=f.cleaned_data["phone"],city=f.cleaned_data["city"])
            messages.success(request,"درخواست عضویت ثبت شد و پس از تأیید مدیر قابل استفاده است."); return redirect("login")
    else: f=RegisterForm()
    return render(request,"estate/form.html",{"form":f,"title":"ثبت‌نام مشاور"})
def logout_view(request):
    if request.method=="POST": logout(request)
    return redirect("home")
@approved_required
def dashboard(request):
    p=request.user.profile
    return render(request,"estate/dashboard.html",{"profile":p,"listings":p.listings.order_by("-created_at"),"requests":p.requests.order_by("-created_at"),"responses":p.proposals.select_related("request")})
@approved_required
def profile_edit(request):
    f=ProfileForm(request.POST or None,instance=request.user.profile)
    if request.method=="POST" and f.is_valid(): f.save(); messages.success(request,"پروفایل ذخیره شد."); return redirect("dashboard")
    return render(request,"estate/form.html",{"form":f,"title":"ویرایش پروفایل"})
@approved_required
def listing_create(request):
    f=ListingForm(request.POST or None)
    if request.method=="POST" and f.is_valid():
        x=f.save(commit=False); x.owner=request.user.profile; x.save(); messages.success(request,"آگهی برای بررسی مدیر ارسال شد."); return redirect("dashboard")
    return render(request,"estate/form.html",{"form":f,"title":"ثبت آگهی"})
@approved_required
def listing_edit(request,pk):
    x=get_object_or_404(Listing,pk=pk,owner=request.user.profile)
    f=ListingForm(request.POST or None,instance=x)
    if request.method=="POST" and f.is_valid():
        obj=f.save(commit=False); obj.moderation="pending"; obj.save(); messages.success(request,"ویرایش برای بررسی مجدد ارسال شد."); return redirect("dashboard")
    return render(request,"estate/form.html",{"form":f,"title":"ویرایش آگهی"})
@approved_required
def requests_board(request):
    qs=Request.objects.select_related("owner").order_by("-created_at")
    cat=request.GET.get("category",""); city=request.GET.get("city","")
    if cat: qs=qs.filter(category=cat)
    if city: qs=qs.filter(city__icontains=city)
    return render(request,"estate/requests.html",{"requests":qs,"category":cat,"city":city})
@approved_required
def request_create(request):
    f=RequestForm(request.POST or None)
    if request.method=="POST" and f.is_valid():
        x=f.save(commit=False); x.owner=request.user.profile; x.save(); messages.success(request,"تقاضا در کارتابل همکاران ثبت شد."); return redirect("request_detail",pk=x.pk)
    return render(request,"estate/form.html",{"form":f,"title":"ثبت تقاضا"})
@approved_required
def request_detail(request,pk):
    x=get_object_or_404(Request,pk=pk)
    owner=x.owner_id==request.user.profile.id
    f=ProposalForm(request.POST or None,user=request.user) if False else ProposalForm(request.POST or None)
    f.fields["listing"].queryset=Listing.objects.filter(owner=request.user.profile,moderation="approved")
    if request.method=="POST":
        if owner: return HttpResponseForbidden("مالک تقاضا نمی‌تواند به تقاضای خود پاسخ دهد.")
        if not x.is_open(): return HttpResponseForbidden("مهلت پاسخ پایان یافته یا تقاضا بسته است.")
        if Proposal.objects.filter(request=x,responder=request.user.profile).exists(): return HttpResponseForbidden("برای هر تقاضا فقط یک پاسخ مجاز است.")
        if f.is_valid():
            pr=f.save(commit=False); pr.request=x; pr.responder=request.user.profile; pr.save(); messages.success(request,"پاسخ ثبت شد."); return redirect("request_detail",pk=x.pk)
    proposals=x.proposals.select_related("responder","listing") if owner or request.user.is_staff else x.proposals.none()
    return render(request,"estate/request_detail.html",{"item":x,"owner":owner,"form":f,"proposals":proposals,"can_answer":not owner and x.is_open() and not Proposal.objects.filter(request=x,responder=request.user.profile).exists()})
