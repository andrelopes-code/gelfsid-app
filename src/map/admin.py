from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models import City, Document, State, Supplier

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(State)
class EstadoAdmin(ModelAdmin):
    list_display = ('abbr', 'name')
    search_fields = ('name', 'abbr')


@admin.register(City)
class CidadeAdmin(ModelAdmin):
    list_display = ('name', 'state')
    list_filter = ('state',)
    search_fields = ('name',)


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ('document', 'type', 'validity', 'status', 'supplier')
    list_filter = ('status', 'type', 'supplier')


@admin.register(Supplier)
class SupplierAdmin(ModelAdmin):
    list_display = (
        'corporate_name',
        'material_type',
        'cpf_cnpj',
        'city',
        'colorful_rating',
    )

    list_filter = (
        'material_type',
        'state',
    )

    search_fields = (
        'corporate_name',
        'cpf_cnpj',
    )

    fieldsets = (
        (
            'Informações Básicas',
            {
                'fields': (
                    'corporate_name',
                    'cpf_cnpj',
                    'material_type',
                )
            },
        ),
        (
            'Avaliação',
            {'fields': ('rating',)},
        ),
        (
            'Localização',
            {
                'fields': (
                    'state',
                    'city',
                )
            },
        ),
    )

    def colorful_rating(self, supplier, good_rating=80):
        if supplier.rating is None:
            return 'N/A'

        if supplier.rating >= good_rating:
            cor = 'var(--green-highlight)'
        else:
            cor = 'var(--highlight)'

        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, f'{supplier.rating}')

    colorful_rating.short_description = 'Nota'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            if request.POST.get('state'):
                kwargs['queryset'] = City.objects.filter(state_id=request.POST.get('state'))
            elif request.GET.get('state'):
                kwargs['queryset'] = City.objects.filter(state_id=request.GET.get('state'))
            else:
                kwargs['queryset'] = City.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/city_state_dependency.js',)
