from django.contrib import admin
from .models import Sprint, Ticket, TicketComment, TicketImage

admin.site.register(Sprint)
admin.site.register(Ticket)
admin.site.register(TicketComment)
admin.site.register(TicketImage)