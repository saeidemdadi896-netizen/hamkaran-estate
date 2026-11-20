from django import forms
from django.contrib.auth.models import User
from django.utils import timezone
from .models import AgentProfile, Listing, Request, Proposal

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="نام کاربری")
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    full_name = forms.CharField(max_length=150, label="نام و نام خانوادگی")
    phone = forms.CharField(max_length=15, label="شماره تماس")
    city = forms.CharField(max_length=100, label="شهر")

    def clean_username(self):
        v = self.cleaned_data["username"]
        if User.objects.filter(username=v).exists():
            raise forms.ValidationError("این نام کاربری قبلاً ثبت شده است.")
        return v

class OrdinaryUserRegisterForm(forms.ModelForm):
    full_name = forms.CharField(max_length=150, label="نام و نام خانوادگی")
    phone = forms.CharField(max_length=15, label="شماره تماس")
    city = forms.CharField(max_length=100, label="شهر", required=False)
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")

    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': 'نام کاربری (کد ملی یا موبایل)',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class ProfileForm(forms.ModelForm):
    class Meta:
        model = AgentProfile
        exclude = ("user", "status", "created_at")

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ("owner", "moderation", "featured", "featured_start", "featured_end", "created_at")

class RequestForm(forms.ModelForm):
    response_deadline = forms.DateTimeField(
        label="مهلت پاسخ",
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"]
    )
    class Meta:
        model = Request
        exclude = ("owner", "created_at", "status", "resolved_at")

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ("message", "listing")
        widgets = {"message": forms.Textarea(attrs={"rows": 4})}
