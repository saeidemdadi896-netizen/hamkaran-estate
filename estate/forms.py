from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import AgentProfile, Listing, Request, Proposal
class RegisterForm(forms.Form):
    username=forms.CharField(max_length=150,label="نام کاربری")
    password=forms.CharField(widget=forms.PasswordInput,label="گذرواژه")
    full_name=forms.CharField(max_length=120,label="نام و نام خانوادگی")
    phone=forms.CharField(max_length=30,label="تلفن")
    city=forms.CharField(max_length=100,label="شهر")
    def clean_username(self):
        v=self.cleaned_data["username"]
        if User.objects.filter(username=v).exists(): raise forms.ValidationError("این نام کاربری قبلاً ثبت شده است.")
        return v
class ProfileForm(forms.ModelForm):
    class Meta:
        model=AgentProfile; exclude=("user","status","created_at")
class ListingForm(forms.ModelForm):
    class Meta:
        model=Listing; exclude=("owner","moderation","featured","featured_start","featured_end","created_at")
    def clean(self):
        d=super().clean(); mode=d.get("mode")
        if mode in ("mortgage","rent") and not (d.get("deposit") or d.get("monthly_rent")):
            raise forms.ValidationError("برای رهن یا اجاره، مبلغ ودیعه یا اجاره را وارد کنید.")
        return d
class RequestForm(forms.ModelForm):
    response_deadline=forms.DateTimeField(label="مهلت پاسخ (میلادی)",help_text="تاریخ و زمان را به میلادی وارد کنید؛ منطقه زمانی سامانه آسیا/تهران است.",widget=forms.DateTimeInput(attrs={"type":"datetime-local"}),input_formats=["%Y-%m-%dT%H:%M"])
    class Meta:
        model=Request; exclude=("owner","created_at","status","resolved_at")
    def clean(self):
        d=super().clean(); deadline=d.get("response_deadline")
        if deadline and deadline<=timezone.now(): self.add_error("response_deadline","مهلت پاسخ باید در آینده باشد.")
        if d.get("min_area") and d.get("max_area") and d["min_area"]>d["max_area"]: self.add_error("max_area","حداکثر متراژ باید از حداقل کمتر نباشد.")
        return d
class ProposalForm(forms.ModelForm):
    class Meta:
        model=Proposal; fields=("message","listing")
        widgets={"message":forms.Textarea(attrs={"rows":4})}
