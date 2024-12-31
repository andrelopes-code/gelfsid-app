from django.contrib import admin, messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import path

from gelfmp.admin import models
from gelfmp.models import Task
from gelfmp.models.choices import TaskStatus


class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        custom_urls = [
            path('', self.index, name='index'),
            path('task/<int:id>/complete', self.complete_task, name='complete_task'),
        ]

        return custom_urls + super().get_urls()

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        extra_context['pending_tasks'] = (
            Task.objects.filter(Q(status=TaskStatus.PENDING) | Q(status=TaskStatus.IN_PROGRESS))
            .filter(Q(assigned_to__isnull=True) | Q(assigned_to=request.user))
            .all()
        )

        return super().index(request, extra_context)

    def complete_task(self, request, id):
        task = get_object_or_404(Task, id=id)

        if task.assigned_to and task.assigned_to != request.user:
            messages.error(request, 'Essa tarefa pertence a outro usuário.')
            return redirect('admin:index')

        task.completed_by = request.user
        task.status = TaskStatus.COMPLETED
        task.save()

        messages.success(request, f'A tarefa "{task.description}" foi marcada como concluída.')

        return redirect('admin:index')


admin_site = CustomAdminSite()

# Registra os modelos Admin
# usando o site admin personalizado.
models.register(admin_site)
