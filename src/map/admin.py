from django.contrib import admin
from .models import FornecedorMateriaPrima, Estado, Cidade
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Estado)
class EstadoAdmin(ModelAdmin):
    list_display = ('sigla', 'nome')
    search_fields = ('nome', 'sigla')


@admin.register(Cidade)
class CidadeAdmin(ModelAdmin):
    list_display = ('nome', 'estado')
    list_filter = ('estado',)
    search_fields = ('nome',)


@admin.register(FornecedorMateriaPrima)
class FornecedorMateriaPrimaAdmin(ModelAdmin):
    list_display = (
        'razao_social',
        'tipo_material',
        'cnpj',
        'cidade',
        'certificacao_status',
        'nota_qualidade_colorida',
    )

    list_filter = (
        'tipo_material',
        'estado',
        'certificacao_ambiental',
    )

    search_fields = (
        'razao_social',
        'cnpj',
    )

    fieldsets = (
        (
            'Informações Básicas',
            {
                'fields': (
                    'razao_social',
                    'cnpj',
                    'tipo_material',
                )
            },
        ),
        (
            'Certificações',
            {
                'fields': (
                    'certificacao_ambiental',
                    'licenca_operacao',
                    'registro_ibama',
                )
            },
        ),
        (
            'Avaliação',
            {'fields': ('nota_qualidade',)},
        ),
        (
            'Localização',
            {
                'fields': (
                    'estado',
                    'cidade',
                    'coordenadas_gps',
                )
            },
        ),
    )

    def certificacao_status(self, obj):
        if obj.certificacao_ambiental:
            return 'Certificado'
        return 'Não Certificado'

    certificacao_status.short_description = 'Certificação'

    def nota_qualidade_colorida(self, obj):
        if obj.nota_qualidade is None:
            return 'N/A'

        if obj.nota_qualidade >= 80:
            cor = 'var(--green-highlight)'
        else:
            cor = 'var(--highlight)'

        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', cor, f'{obj.nota_qualidade}')

    nota_qualidade_colorida.short_description = 'Nota'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'cidade':
            if request.POST.get('estado'):
                kwargs['queryset'] = Cidade.objects.filter(estado_id=request.POST.get('estado'))
            elif request.GET.get('estado'):
                kwargs['queryset'] = Cidade.objects.filter(estado_id=request.GET.get('estado'))
            else:
                kwargs['queryset'] = Cidade.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        js = ('admin/js/cidade_estado_dependencia.js',)
