from django.contrib import admin
from .models import AgentProfile, Listing, Request, Proposal
@admin.register(AgentProfile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=("full_name","city","phone","status","created_at"); list_filter=("status","city"); search_fields=("full_name","phone","user__username")
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display=("title","owner","mode","city","moderation","featured","featured_start","featured_end"); list_filter=("moderation","mode","city","featured"); search_fields=("title","owner__full_name");
    def get_readonly_fields(self,request,obj=None): return ()
@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display=("title","owner","category","response_deadline","status"); list_filter=("category","status")
@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin): list_display=("request","responder","created_at")
admin.site.site_header="مدیریت تعاونی مشاوران املاک"
