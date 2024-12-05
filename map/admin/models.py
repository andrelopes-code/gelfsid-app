from django.contrib import admin

from map import models

from .bases import BaseModelAdmin
from .inlines import ContactInline, DocumentInline


@admin.register(models.Contact)
class ContactAdmin(BaseModelAdmin):
    list_display = ('contact_type', 'name', 'email')
    search_fields = ('name', 'email')
    list_filter = ('contact_type',)


@admin.register(models.BankDetails)
class BankDetailsAdmin(BaseModelAdmin):
    list_display = ('bank_name', 'agency', 'account_number')


@admin.register(models.Document)
class DocumentAdmin(BaseModelAdmin):
    list_display = ('name', 'type', 'validity', 'status', 'supplier')
    list_filter = ('status', 'type', 'supplier')


@admin.register(models.CharcoalEntry)
class CharcoalEntryAdmin(BaseModelAdmin):
    list_display = ('supplier', 'entry_volume', 'moisture', 'density', 'fines', 'entry_date')
    search_fields = ('supplier__corporate_name',)


@admin.register(models.Supplier)
class SupplierAdmin(BaseModelAdmin):
    list_display = (
        'corporate_name',
        'material_type',
        'cpf_cnpj',
        'city',
    )

    list_filter = ('material_type', 'state')
    search_fields = ('corporate_name', 'cpf_cnpj')

    fieldsets = (
        (
            'Informações Básicas',
            {
                'fields': [
                    'corporate_name',
                    'cpf_cnpj',
                    'material_type',
                    ('state_registration', 'municipal_registration'),
                    'xml_email',
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
                'classes': ('grp-collapse grp-closed',),
                'fields': ['observations'],
            },
        ),
    )

    inlines = [DocumentInline, ContactInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'city':
            if request.POST.get('state'):
                kwargs['queryset'] = models.City.objects.filter(state_id=request.POST.get('state'))
            elif request.GET.get('state'):
                kwargs['queryset'] = models.City.objects.filter(state_id=request.GET.get('state'))
            else:
                kwargs['queryset'] = models.City.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/city_state_dependency.js',)
