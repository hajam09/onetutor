from django.contrib import admin
from .models import Ticket, TicketImage

admin.site.register(Ticket)
admin.site.register(TicketImage)