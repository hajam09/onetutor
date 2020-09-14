from django.contrib import admin

from chat.forms import ThreadForm
from chat.models import ChatMessage
from chat.models import Thread


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessageInline]
    form = ThreadForm

    class Meta:
        model = Thread


admin.site.register(ChatMessage)
admin.site.register(Thread, ThreadAdmin)
