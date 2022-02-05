from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(Sprint)
admin.site.register(Project)
admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Label)
admin.site.register(Ticket)
admin.site.register(TicketAttachment)
admin.site.register(TicketComment)
admin.site.register(Team)
