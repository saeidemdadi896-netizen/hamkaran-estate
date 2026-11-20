from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class AgentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    STATUS = [("pending", "در انتظار بررسی"), ("approved", "تأیید شده"), ("rejected", "رد شده")]
    status = models.CharField(max_length=12, choices=STATUS, default="pending")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    public_phone = models.BooleanField(default=False, verbose_name="نمایش تلفن در پروفایل عمومی")
    email = models.EmailField(blank=True)
    office_name = models.CharField(max_length=150, blank=True)
    office_address = models.CharField(max_length=250, blank=True)
    license_number = models.CharField(max_length=80, blank=True)
    city = models.CharField(max_length=100)
    areas = models.CharField(max_length=250, blank=True, help_text="محله‌ها را با ویرگول جدا کنید")
    experience_years = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(blank=True)
    specialties = models.CharField(max_length=250, blank=True)
    portrait_url = models.URLField(blank=True)
    logo_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.full_name

class Listing(models.Model):
    MOD = [("pending", "در انتظار بررسی"), ("approved", "تأیید شده"), ("rejected", "رد شده")]
    MODES = [("sale", "فروش"), ("mortgage", "رهن"), ("rent", "اجاره"), ("partnership", "مشارکت")]
    TYPES = [("apartment", "آپارتمان"), ("house", "خانه/ویلا"), ("land", "زمین"), ("commercial", "تجاری"), ("office", "اداری"), ("other", "سایر")]
    owner = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=180)
    mode = models.CharField(max_length=15, choices=MODES)
    property_type = models.CharField(max_length=15, choices=TYPES)
    city = models.CharField(max_length=100); neighborhood = models.CharField(max_length=100)
    address = models.CharField(max_length=300, blank=True)
    area = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    bedrooms = models.PositiveSmallIntegerField(default=0); floor = models.CharField(max_length=30, blank=True)
    age = models.PositiveSmallIntegerField(default=0)
    price = models.PositiveBigIntegerField(default=0)
    deposit = models.PositiveBigIntegerField(default=0)
    monthly_rent = models.PositiveBigIntegerField(default=0)
    description = models.TextField(); image_url = models.URLField(blank=True)
    owner_name = models.CharField(max_length=120, blank=True)
    owner_phone = models.CharField(max_length=30, blank=True)
    public_phone = models.BooleanField(default=False)
    moderation = models.CharField(max_length=12, choices=MOD, default="pending")
    expires_at = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)
    featured_start = models.DateField(null=True, blank=True)
    featured_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def is_featured_now(self):
        d = timezone.localdate(); return self.featured and (not self.featured_start or self.featured_start <= d) and (not self.featured_end or self.featured_end >= d)
    def __str__(self): return self.title

class Request(models.Model):
    CATEGORIES = [("buy", "خرید"), ("sell", "فروش"), ("mortgage", "رهن"), ("rent", "اجاره"), ("partnership", "مشارکت")]
    STATUS = [("open", "باز"), ("closed", "بسته شده")]
    owner = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name="requests")
    category = models.CharField(max_length=15, choices=CATEGORIES)
    property_type = models.CharField(max_length=15, choices=Listing.TYPES)
    title = models.CharField(max_length=180); city = models.CharField(max_length=100); neighborhood = models.CharField(max_length=100, blank=True)
    min_area = models.PositiveIntegerField(null=True, blank=True); max_area = models.PositiveIntegerField(null=True, blank=True)
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    budget = models.PositiveBigIntegerField(null=True, blank=True)
    description = models.TextField()
    client_name = models.CharField(max_length=120, blank=True); client_phone = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    response_deadline = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS, default="open")
    resolved_at = models.DateTimeField(null=True, blank=True)
    def is_expired(self): return self.response_deadline <= timezone.now()
    def is_open(self): return self.status == "open" and not self.is_expired()
    def __str__(self): return self.title

class Proposal(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE, related_name="proposals")
    responder = models.ForeignKey(AgentProfile, on_delete=models.CASCADE, related_name="proposals")
    message = models.TextField()
    listing = models.ForeignKey(Listing, null=True, blank=True, on_delete=models.SET_NULL, limit_choices_to={"moderation": "approved"})
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: constraints = [models.UniqueConstraint(fields=["request", "responder"], name="one_proposal_per_agent_request")]
    def __str__(self): return f"{self.responder} → {self.request}"

class OrdinaryUserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ordinary_profile")
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    city = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.full_name or self.user.username
