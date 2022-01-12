from django.contrib import admin

from chat.forms import ThreadForm
from chat.models import ChatMessage
from chat.models import Thread

admin.site.register(ChatMessage)


class ChatMessage(admin.TabularInline):
    model = ChatMessage


class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    form = ThreadForm

    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)
