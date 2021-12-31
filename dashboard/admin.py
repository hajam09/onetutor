from django.contrib import admin

from dashboard.models import UserLogin
from dashboard.models import UserSession

admin.site.register(UserLogin)
admin.site.register(UserSession)
