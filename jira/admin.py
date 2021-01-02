from django.contrib import admin
from .models import Sprint, Ticket, TicketImage

admin.site.register(Sprint)
admin.site.register(Ticket)
admin.site.register(TicketImage)