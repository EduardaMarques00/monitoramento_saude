from django.contrib import admin
from .models import Prescricao

@admin.register(Prescricao)
class PrescricaoAdmin(admin.ModelAdmin):
    list_display = ('medicamento', 'paciente', 'medico', 'dosagem', 'data_inicio', 'data_fim')
    search_fields = ('medicamento', 'paciente__nome', 'medico__nome')
    list_filter = ('data_inicio',)
