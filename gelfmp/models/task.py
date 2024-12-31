from django.contrib.auth.models import User
from django.db import models
from django.forms import ValidationError

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
        related_name='tasks_assigned_to',
        verbose_name='Atribuído a',
    )

    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_assigned_by',
        verbose_name='Atribuído por',
    )

    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks_completed_by',
        verbose_name='Concluído por',
    )

    def clean(self):
        if self.due_date and self.due_date < self.created_at:
            raise ValidationError('A data de vencimento não pode ser anterior à criação da tarefa.')

        if self.status == TaskStatus.COMPLETED and not self.completed_by:
            raise ValidationError('O campo "Concluído por" deve ser preenchido para tarefas concluídas.')

        return super().clean()

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

    def __str__(self):
        return self.description
