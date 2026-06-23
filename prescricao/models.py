from django.db import models

class Prescricao(models.Model):
    paciente = models.ForeignKey('paciente.Paciente', on_delete=models.CASCADE, related_name='prescricoes')
    medico = models.ForeignKey('medico.Medico', on_delete=models.CASCADE, related_name='prescricoes')
    medicamento = models.CharField(max_length=200)
    dosagem = models.CharField(max_length=100)
    frequencia = models.CharField(max_length=100)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    observacoes = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Prescrição'
        verbose_name_plural = 'Prescrições'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.medicamento} - {self.paciente} ({self.data_inicio})'
