from django.contrib.auth.models import User
from django.db import models

from .base_model import BaseModel
from .choices import TaskStatus


class Task(BaseModel):
    description = models.TextField(max_length=255, verbose_name='Descrição')
    due_date = models.DateField(null=True, blank=True, verbose_name='Data de Vencimento')

    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        verbose_name='Status',
    )

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Responsável',
    )

    def __str__(self):
        return self.description

    class Meta:
        indexes = [
            models.Index(fields=['assigned_to']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

        ordering = ['-created_at']
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
