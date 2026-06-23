from django.contrib import admin
from .models import Notificacao

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'paciente', 'tipo', 'lida', 'criado_em')
    search_fields = ('titulo', 'paciente__nome', 'mensagem')
    list_filter = ('tipo', 'lida')
