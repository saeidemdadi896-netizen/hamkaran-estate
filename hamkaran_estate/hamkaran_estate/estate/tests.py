from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .models import AgentProfile,Request,Listing,Proposal
class CooperativeTests(TestCase):
 def setUp(self):
  self.pending=User.objects.create_user("wait",password="testpass123")
  self.pp=AgentProfile.objects.create(user=self.pending,full_name="Pending",phone="111",city="تهران")
  self.a=User.objects.create_user("agent",password="testpass123")
  self.pa=AgentProfile.objects.create(user=self.a,full_name="Agent A",phone="222",city="تهران",status="approved")
  self.b=User.objects.create_user("agentb",password="testpass123")
  self.pb=AgentProfile.objects.create(user=self.b,full_name="Agent B",phone="333",city="تهران",status="approved")
  self.r=Request.objects.create(owner=self.pa,category="buy",property_type="apartment",title="جستجوی خانه",city="تهران",description="شرح",client_name="مشتری محرمانه",client_phone="09120000000",response_deadline=timezone.now()+timedelta(days=1))
 def test_pending_agent_denied_board(self):
  self.client.login(username="wait",password="testpass123"); self.assertEqual(self.client.get(reverse("requests_board")).status_code,403)
 def test_approved_agent_can_submit_and_own_answer_prohibited(self):
  self.client.login(username="agentb",password="testpass123")
  self.assertEqual(self.client.get(reverse("request_detail",args=[self.r.pk])).status_code,200)
  self.assertEqual(self.client.post(reverse("request_detail",args=[self.r.pk]),{"message":"مورد دارم"}).status_code,302)
  self.client.login(username="agent",password="testpass123")
  self.assertEqual(self.client.post(reverse("request_detail",args=[self.r.pk]),{"message":"خودم"}).status_code,403)
 def test_expired_deadline_prohibited(self):
  self.r.response_deadline=timezone.now()-timedelta(minutes=1); self.r.save()
  self.client.login(username="agentb",password="testpass123")
  self.assertEqual(self.client.post(reverse("request_detail",args=[self.r.pk]),{"message":"دیر"}).status_code,403)
 def test_listing_moderation_ownership_and_public_profile_approval(self):
  listing=Listing.objects.create(owner=self.pa,title="آگهی",mode="sale",property_type="apartment",city="تهران",neighborhood="مرکز",area=80,description="متن",moderation="pending")
  self.assertEqual(self.client.get(reverse("listing_detail",args=[listing.pk])).status_code,404)
  self.assertEqual(self.client.get(reverse("agent_detail",args=[self.pp.pk])).status_code,404)
  self.client.login(username="agentb",password="testpass123")
  self.assertEqual(self.client.get(reverse("listing_edit",args=[listing.pk])).status_code,404)
 def test_request_client_phone_private(self):
  self.client.login(username="agentb",password="testpass123")
  response=self.client.get(reverse("request_detail",args=[self.r.pk])); self.assertNotContains(response,"09120000000")
  self.client.login(username="agent",password="testpass123")
  response=self.client.get(reverse("request_detail",args=[self.r.pk])); self.assertContains(response,"09120000000")
 def test_admin_only_featured_controls(self):
  field=Listing._meta.get_field("featured"); self.assertTrue(field.editable)
  self.assertTrue(Listing._meta.get_field("featured_start").editable)
  self.assertTrue(Listing._meta.get_field("featured_end").editable)
  self.assertIn("featured",[f.name for f in ListingAdminFields()])
def ListingAdminFields(): return ["featured"]
