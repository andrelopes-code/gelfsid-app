from django.http import JsonResponse
from map.models import FornecedorMateriaPrima
from django.conf import settings

HOST_CITY = getattr(settings, 'HOST_CITY', 'Sete Lagoas, MG')


def get_fornecedores(request):
    fornecedores = FornecedorMateriaPrima.objects.select_related(
        'cidade', 'estado', 'licenca_ambiental', 'cadastro_tecnico_federal', 'registro_ief'
    ).all()

    def serialize_document(document):
        return (
            {
                'documento': document.documento,
                'validade': document.validade,
                'status': document.status,
                'hyperlink': document.hyperlink,
            }
            if document
            else None
        )

    data = []
    for fornecedor in fornecedores:
        data.append({
            'id': fornecedor.id,
            'razao_social': fornecedor.razao_social,
            'cpf_cnpj': fornecedor.cpf_cnpj,
            'tipo_material': fornecedor.get_tipo_material_display(),
            'licenca_ambiental': serialize_document(fornecedor.licenca_ambiental),
            'cadastro_tecnico_federal': serialize_document(fornecedor.cadastro_tecnico_federal),
            'registro_ief': serialize_document(fornecedor.registro_ief),
            'avaliacao': fornecedor.avaliacao,
            'estado': {
                'sigla': fornecedor.estado.sigla,
                'nome': fornecedor.estado.nome,
            },
            'cidade': {
                'id': fornecedor.cidade.id,
                'nome': fornecedor.cidade.nome,
            },
            'distancia_em_metros': fornecedor.distancia_em_metros,
        })
        print(fornecedor.distancia_em_metros)

    return JsonResponse(data, safe=False)
