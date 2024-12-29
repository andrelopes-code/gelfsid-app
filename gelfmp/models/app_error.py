from django.db import models

from .base_model import BaseModel


class AppError(BaseModel):
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    error_origin = models.CharField(max_length=100, verbose_name='Origem do Erro')
    error_message = models.TextField(verbose_name='Mensagem de Erro')

    def __str__(self):
        return self.error_message

    class Meta:
        verbose_name = 'Erro'
        verbose_name_plural = 'Erros'
        ordering = ['-timestamp']
