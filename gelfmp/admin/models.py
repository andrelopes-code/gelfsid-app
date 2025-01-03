from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html

from gelfmp import models
from gelfmp.admin.exporters import ExportCSV
from gelfmp.models.choices import TaskStatus

from .base import BaseModelAdmin, ROBaseModelAdmin
from .filters import DocumentValidityFilter, MonthFilter, SupplierWithEntriesFilter
from .inlines import AliasInline, BankDetailsInline, ContactInline, DocumentInline


class LogEntryAdmin(ROBaseModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_repr', 'action_flag')
    search_fields = ('object_repr', 'user__username')
    list_filter = ('action_flag', 'content_type')


class ContactAdmin(BaseModelAdmin):
    list_display = ('contact_type', 'name', 'email')
    search_fields = ('name', 'email')
    list_filter = ('contact_type',)
    autocomplete_fields = ('supplier',)

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
            {'fields': []},
        ),
    )


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
                    'account_cnpj',
                )
            },
        ),
        (
            '',
            {'fields': []},
        ),
    )


class DocumentAdmin(BaseModelAdmin):
    list_display = ('document_type', 'name', 'validity', 'supplier')
    list_filter = ('document_type', 'supplier', DocumentValidityFilter)
    search_fields = ('name', 'supplier__corporate_name')
    autocomplete_fields = ('supplier',)

    actions = ['delete_files']

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


class CharcoalEntryAdmin(ROBaseModelAdmin, ExportCSV):
    change_list_template = 'admin/charcoalentry/change_list.html'

    list_display = ('supplier', 'entry_volume', 'moisture', 'density', 'fines', 'entry_date')
    search_fields = ('supplier__corporate_name', 'dcf__process_number')
    list_filter = (SupplierWithEntriesFilter, MonthFilter, 'supplier__supplier_type')
    autocomplete_fields = ('supplier', 'dcf')

    actions = ['export_to_csv']

    csv_fields = (
        'supplier',
        'entry_date',
        'dcf',
        'entry_volume',
        'moisture',
        'density',
        'fines',
    )

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
            {'fields': []},
        ),
    )


class CharcoalMonthlyPlanAdmin(BaseModelAdmin):
    change_form_template = 'admin/charcoalmonthlyplan/change_form.html'

    list_display = ('supplier', 'planned_volume', 'month', 'year')
    list_filter = ('month', 'year')
    search_fields = ('supplier__corporate_name',)
    autocomplete_fields = ('supplier',)

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
            # Adciona apenas fornecedores de carvão ao seletor de fornecedores.
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


class CharcoalIQFAdmin(ROBaseModelAdmin):
    change_list_template = 'admin/charcoaliqf/change_list.html'

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


class SupplierAdmin(BaseModelAdmin):
    change_form_template = 'admin/supplier/change_form.html'

    list_display = ('corporate_name', 'material_type', 'cpf_cnpj', 'city', 'active')
    list_filter = ('material_type', 'state', 'active')
    search_fields = ('corporate_name', 'cpf_cnpj')

    inlines = [DocumentInline, ContactInline, BankDetailsInline, AliasInline]

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
            'Extra',
            {
                'fields': ['observations'],
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        # Remove a correção ortográfica no campo de observações.
        if db_field.name == 'observations':
            formfield.widget.attrs.update({'spellcheck': 'false'})

        # Remove a correção ortográfica no campo de nome da corporação
        # e força o uso de letras maiúsculas no campo.
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


class CharcoalContractAdmin(BaseModelAdmin):
    change_form_template = 'admin/charcoalcontract/change_form.html'

    list_display = (
        'supplier',
        'dcf',
        'legal_department_signed',
        'supplier_signed',
        'gelf_signed',
        'remaining_volume',
        'status',
    )

    search_fields = ('supplier__corporate_name', 'dcf__process_number')
    autocomplete_fields = ('dcf', 'supplier')

    fieldsets = (
        (
            'Informações do Contrato',
            {
                'fields': [
                    'supplier',
                    'dcf',
                    'price',
                    ('entry_date', 'contract_volume'),
                    'file',
                ]
            },
        ),
        (
            'Assinaturas',
            {
                'fields': (
                    (
                        'legal_department_signed',
                        'supplier_signed',
                        'gelf_signed',
                    ),
                )
            },
        ),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'supplier':
            # Adciona apenas fornecedores de carvão ao seletor de fornecedores.
            kwargs['queryset'] = models.Supplier.objects.filter(material_type=models.MaterialType.CHARCOAL)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def status(self, obj):
        if not obj.legal_department_signed or not obj.supplier_signed or not obj.gelf_signed:
            return 'Pendente'

        return 'Vigente' if obj.active else 'Encerrado'

    def remaining_volume(self, obj):
        delivered_volume = obj.delivered_volume
        return round(obj.contract_volume - delivered_volume, 2)

    status.short_description = 'Status'
    remaining_volume.short_description = 'Volume Restante'


class DCFAdmin(BaseModelAdmin):
    list_display = ('process_number', 'supplier', 'available_volume', 'validity_date')
    search_fields = ('process_number', 'supplier__corporate_name')

    autocomplete_fields = ('supplier',)

    fieldsets = (
        (
            'Informações da DCF',
            {
                'fields': [
                    'process_number',
                    'supplier',
                    (
                        'declared_volume',
                        'available_volume',
                        'issue_date',
                    ),
                    'file',
                ]
            },
        ),
        ('', {'fields': []}),
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'supplier':
            # Adciona apenas fornecedores de carvão ao seletor de fornecedores.
            kwargs['queryset'] = models.Supplier.objects.filter(material_type=models.MaterialType.CHARCOAL)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class TaskAdmin(BaseModelAdmin):
    list_display = ('description', 'assigned_by', 'assigned_to', 'due_date', 'status_color')
    readonly_fields = ('assigned_by', 'completed_by')
    search_fields = (
        'description',
        'assigned_to__first_name',
        'assigned_to__last_name',
        'assigned_by__first_name',
        'assigned_by__last_name',
    )

    fieldsets = (
        (
            'Informações da Tarefa',
            {
                'fields': [
                    'description',
                    'status',
                    'due_date',
                    ('assigned_to', 'assigned_by', 'completed_by'),
                ]
            },
        ),
        ('', {'fields': []}),
    )

    def status_color(self, obj):
        status_display = obj.get_status_display()

        if obj.status == TaskStatus.COMPLETED:
            return format_html('<span style="color:#88f38c;">{}</span>', f'{status_display} ({obj.completed_by})')
        elif obj.status == TaskStatus.IN_PROGRESS:
            return format_html('<span style="color:#f3e887;">{}</span>', status_display)
        elif obj.status == TaskStatus.PENDING:
            return format_html('<span style="color:#f0b763;">{}</span>', status_display)

        return status_display

    def has_change_permission(self, request, obj=None):
        if obj and obj.assigned_by == request.user or request.user.is_superuser:
            return True

        return False

    def has_delete_permission(self, request, obj=None):
        if obj and obj.assigned_by == request.user or request.user.is_superuser:
            return True

        return False

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.assigned_by = request.user

        if obj.status == TaskStatus.COMPLETED and not obj.completed_by:
            obj.completed_by = request.user

        super().save_model(request, obj, form, change)

    status_color.short_description = 'Status'
    status_color.admin_order_field = 'status'


def register(admin_site):
    admin_site.register(models.Supplier, SupplierAdmin)
    admin_site.register(models.Document, DocumentAdmin)
    admin_site.register(models.CharcoalMonthlyPlan, CharcoalMonthlyPlanAdmin)
    admin_site.register(models.CharcoalIQF, CharcoalIQFAdmin)
    admin_site.register(models.CharcoalEntry, CharcoalEntryAdmin)
    admin_site.register(models.Contact, ContactAdmin)
    admin_site.register(models.BankDetails, BankDetailsAdmin)
    admin_site.register(models.CharcoalContract, CharcoalContractAdmin)
    admin_site.register(models.DCF, DCFAdmin)
    admin_site.register(models.Task, TaskAdmin)

    # Modelos admin padrão do Django
    admin_site.register(Group, GroupAdmin)
    admin_site.register(User, UserAdmin)
    admin_site.register(LogEntry, LogEntryAdmin)
