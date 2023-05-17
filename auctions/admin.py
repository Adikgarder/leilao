from django.contrib import admin
from .models import *
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from twilio.rest import Client
from .models import Profile
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from django.http import HttpResponse
import csv

admin.site.register(User, UserAdmin)


from .models import SMSUser

class auction(admin.ModelAdmin):
    list_display = ("id", "user", "active_bool", "title", "desc", "starting_bid", "image_url", "category", "time_left")

    def time_left(self, obj):
        time_left = obj.end_date - timezone.now()

        if time_left < timedelta():
            return "Leilão encerrado"
        else:
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{days}d {hours}h {minutes}m {seconds}s"
        
        
class watchl(admin.ModelAdmin):
    list_display = ("id", "watch_list" , "user")

class bds(admin.ModelAdmin):
    list_display = ("id","user","listingid","bid")

class comme(admin.ModelAdmin):
    list_display = ("id","user", "comment", "listingid")

class win(admin.ModelAdmin):
    list_display = ("id","user", "bid_win_list")

class SendEmail(admin.ModelAdmin):
   list_display = ('user', 'subject', 'sent_at')

def send_email(self, request, queryset):
        for obj in queryset:
            subject = obj.subject
            message = render_to_string('email_template.html', {'obj': obj})
            plain_message = strip_tags(message)
            from_email = 'your_email@example.com'
            recipient_list = [obj.user.email]
            send_mail(subject, plain_message, from_email, recipient_list, html_message=message)
            obj.sent_at = timezone.now()
            obj.save()

send_email.short_description = 'Send email to selected users'

actions = [send_email]

class SMSUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'sent_at')
    actions = ['send_sms']

    def send_sms(self, request, queryset):
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        twilio_number = settings.TWILIO_PHONE_NUMBER

        for sms_user in queryset:
            message = sms_user.message
            recipient_number = sms_user.user.profile.phone_number

            client = Client(account_sid, auth_token)

            message = client.messages.create(
                body=message,
                from_=twilio_number,
                to=recipient_number
            )

            sms_user.sent_at = timezone.now()
            sms_user.save()

    send_sms.short_description = 'Send SMS to selected users'

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'profile'
    
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'Profile.is_staff', 'Profile.is_superuser', 'Profile.is_active')
    list_filter = ('Profile.is_staff', 'Profile.is_superuser', 'Profile.is_active', 'user__groups__name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number', 'address', 'postal_code')}),
        (_('Permissions'), {'fields': ('is_active',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

class Profileuser(admin.ModelAdmin):
    list_display = ("id" , "user","phone_number","address","postal_code","city","is_staff","is_superuser","is_active")
# Register your models here.
admin.site.register(auctionlist, auction)
admin.site.register(bids, bds)
admin.site.register(comments, comme)
admin.site.register(watchlist, watchl)
admin.site.register(winner, win)
admin.site.register(EmailUser,SendEmail) 
admin.site.register(SMSUser, SMSUserAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile,Profileuser)


