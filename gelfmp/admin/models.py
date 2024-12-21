from django.contrib import admin

from gelfmp import models

from .base import BaseModelAdmin
from .filters import MonthFilter, SupplierWithEntriesFilter
from .inlines import ContactInline, DocumentInline


@admin.register(models.Contact)
class ContactAdmin(BaseModelAdmin):
    list_display = ('contact_type', 'name', 'email')
    search_fields = ('name', 'email')
    list_filter = ('contact_type',)
    fieldsets = (
        (
            'Contato',
            {
                'fields': (
                    'supplier',
                    'contact_type',
                    'name',
                    'email',
                    'primary_phone',
                    'secondary_phone',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )


@admin.register(models.BankDetails)
class BankDetailsAdmin(BaseModelAdmin):
    list_display = ('bank_name', 'account_number', 'agency')
    fieldsets = (
        (
            'Detalhes Bancários',
            {
                'fields': (
                    'bank_name',
                    'bank_code',
                    'account_number',
                    'agency',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )


@admin.register(models.Document)
class DocumentAdmin(BaseModelAdmin):
    list_display = ('document_type', 'name', 'validity', 'supplier')
    list_filter = ('document_type', 'supplier')
    search_fields = ['name', 'supplier__corporate_name']
    actions = ['delete_files']

    def get_actions(self, request):
        actions = super().get_actions(request)

        # Remove a opção padrão de exclusão de documentos
        # pois estava causando inconsistências não deletando
        # o arquivo no sistema de arquivos.
        if 'delete_selected' in actions:
            del actions['delete_selected']

        return actions

    def delete_files(self, request, queryset):
        # Action personalizada para deletar
        # os documentos selecionados.
        for obj in queryset:
            obj.delete()

        self.message_user(request, 'Documentos excluídos com sucesso!')

    delete_files.short_description = 'Excluir Documentos selecionados'

    fieldsets = (
        (
            'Documento',
            {
                'fields': (
                    'supplier',
                    'document_type',
                    'visible',
                    'name',
                    'validity',
                    'file',
                )
            },
        ),
        (
            '',
            {'fields': ('geojson',)},
        ),
    )


@admin.register(models.CharcoalEntry)
class CharcoalEntryAdmin(BaseModelAdmin):
    list_display = ('supplier', 'entry_volume', 'moisture', 'density', 'fines', 'entry_date')
    search_fields = ('supplier__corporate_name', 'dcf')
    list_filter = (SupplierWithEntriesFilter, MonthFilter)

    fieldsets = (
        (
            'Entrada de Carvão',
            {
                'fields': (
                    'supplier',
                    'entry_date',
                    'entry_volume',
                    'moisture',
                    'density',
                    'fines',
                    'dcf',
                )
            },
        ),
        (
            '',
            {'fields': tuple()},
        ),
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False


@admin.register(models.CharcoalMonthlyPlan)
class CharcoalMonthlyPlanAdmin(BaseModelAdmin):
    change_form_template = 'admin/charcoalmonthlyplan/change_form.html'

    list_display = ('supplier', 'planned_volume', 'month', 'year')
    list_filter = ('month', 'year')
    search_fields = ('supplier__corporate_name',)

    fieldsets = (
        (
            'Programação de Carvão',
            {
                'fields': (
                    'supplier',
                    'planned_volume',
                    'month',
                    'year',
                )
            },
        ),
        (
            'GELF',
            {'fields': ('price',)},
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'supplier':
            # Adciona apenas fornecedores de carvão ao seletor de fornecedores
            kwargs['queryset'] = models.Supplier.objects.filter(material_type=models.MaterialType.CHARCOAL)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        return {
            'month': request.session.get('charcoalmonthlyplan_last_month'),
            'year': request.session.get('charcoalmonthlyplan_last_year'),
        }

    def response_add(self, request, obj, post_url_continue=None):
        request.session['charcoalmonthlyplan_last_month'] = obj.month
        request.session['charcoalmonthlyplan_last_year'] = obj.year

        return super().response_add(request, obj, post_url_continue)


@admin.register(models.CharcoalIQF)
class CharcoalIQFAdmin(BaseModelAdmin):
    change_list_template = 'admin/charcoaliqf/change_form.html'

    list_display = (
        'supplier',
        'iqf',
        'planned_percentage',
        'fines_percentage',
        'moisture_percentage',
        'density_percentage',
        'month',
        'year',
    )
    list_filter = ('month', 'year')
    search_fields = ('supplier__corporate_name',)

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(models.Supplier)
class SupplierAdmin(BaseModelAdmin):
    list_display = (
        'corporate_name',
        'material_type',
        'cpf_cnpj',
        'city',
        'active',
    )

    list_filter = ('material_type', 'state', 'active')
    search_fields = ('corporate_name', 'cpf_cnpj')

    fieldsets = (
        (
            'Informações Básicas',
            {
                'fields': [
                    'corporate_name',
                    'cpf_cnpj',
                    ('supplier_type', 'material_type'),
                    ('state_registration', 'municipal_registration'),
                    ('xml_email', 'rm_code'),
                    'active',
                ]
            },
        ),
        (
            'Localização',
            {
                'fields': [
                    (
                        'address',
                        'latitude',
                        'longitude',
                    ),
                    (
                        'cep',
                        'state',
                        'city',
                    ),
                ]
            },
        ),
        (
            'Pagamento',
            {
                'fields': [
                    ('bank_details',),
                ]
            },
        ),
        (
            'Extra',
            {
                'fields': ['observations'],
            },
        ),
    )

    inlines = [DocumentInline, ContactInline]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name == 'observations':
            formfield.widget.attrs.update({'spellcheck': 'false'})

        if db_field.name == 'corporate_name':
            formfield.widget.attrs.update({'spellcheck': 'false', 'style': 'text-transform: uppercase;'})

        return formfield

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            state = request.POST.get('state') or request.GET.get('state')
            if state:
                kwargs['queryset'] = models.City.objects.filter(state_id=state)
            else:
                kwargs['queryset'] = models.City.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/city_state_dependency.js',)
