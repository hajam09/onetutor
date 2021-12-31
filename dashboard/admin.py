from django.contrib import admin

from dashboard.models import UserLogin
from dashboard.models import UserSession

class UserLoginAdmin(admin.ModelAdmin):
    readonly_fields = ('loginTime', 'logoutTime')

class UserSessionAdmin(admin.ModelAdmin):
    readonly_fields = ('dateTime',)

admin.site.register(UserLogin, UserLoginAdmin)
admin.site.register(UserSession, UserSessionAdmin)
