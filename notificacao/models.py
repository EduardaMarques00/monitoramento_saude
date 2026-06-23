from django.db import models

class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('alerta', 'Alerta'),
        ('lembrete', 'Lembrete'),
        ('resultado', 'Resultado'),
        ('outro', 'Outro'),
    ]
    paciente = models.ForeignKey('paciente.Paciente', on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='lembrete')
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-criado_em']

    def __str__(self):
        return f'[{self.tipo}] {self.titulo} - {self.paciente}'
