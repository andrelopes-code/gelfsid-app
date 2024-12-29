from django.contrib import admin
from django.urls import path

from gelfmp.admin import models
from gelfmp.models.app_error import AppError


class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path('', self.index, name='index'),
        ]

        return custom_urls + urls

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}

        recent_errors = AppError.objects.all()[:30]

        extra_context.update({
            'recent_errors': recent_errors,
        })

        return super().index(request, extra_context)


admin_site = CustomAdminSite()
models.register(admin_site)
