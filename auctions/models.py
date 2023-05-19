from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from twilio.rest import Client
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from twilio.base.exceptions import TwilioException



def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

class User(AbstractUser):
    pass
    phone = models.CharField(max_length=20, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

class auctionlist(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    desc = models.TextField()
    starting_bid = models.IntegerField()
    image_url = models.CharField(max_length=228, default=None, blank=True, null=True)    
    category = models.CharField(max_length=64)
    active_bool = models.BooleanField(default=True)                       
    end_date = models.DateTimeField()


    def time_left(self):
        time_left = self.end_date - timezone.now()
        if time_left.days < 0:
            return "Leilão encerrado"
        else:
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m {seconds}s"

        
class bids(models.Model):
    user = models.CharField(max_length=30)
    listingid = models.IntegerField()
    bid = models.IntegerField()
    

class comments(models.Model):
    user = models.CharField(max_length=64)
    comment = models.TextField()
    listingid = models.IntegerField()
    

class watchlist(models.Model):
    watch_list = models.ForeignKey(auctionlist, on_delete=models.CASCADE)
    user = models.CharField(max_length=64)

class winner(models.Model):
    bid_win_list = models.ForeignKey(auctionlist, on_delete = models.CASCADE)
    user = models.CharField(max_length=64, default = None)

class EmailUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        subject = self.subject
        message = self.message
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [self.user.email]

        html_message = render_to_string('email_template.html', {'message': message})
        plain_message = strip_tags(html_message)

        send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)
        super(EmailUser, self).save(*args, **kwargs)
from django.conf import settings
from twilio.rest import Client

class SMSUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        message = self.message
        try:
            recipient_number = self.user.profile.phone_number
        except Profile.DoesNotExist:
            # handle case where user doesn't have a profile
            recipient_number = None

        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_number = settings.TWILIO_PHONE_NUMBER

        client = Client(account_sid, auth_token)

        try:
            message = client.messages.create(
                body=message,
                from_=twilio_number,
                to=recipient_number
            )
            super().save(*args, **kwargs)
        except TwilioException as e:
            # handle Twilio errors
            print(f"Failed to send SMS message: {str(e)}")

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email

        




