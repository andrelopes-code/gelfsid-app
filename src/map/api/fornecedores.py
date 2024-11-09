from django.http import JsonResponse
from map.models import FornecedorMateriaPrima


def get_fornecedores(request):
    fornecedores = FornecedorMateriaPrima.objects.select_related('cidade', 'estado').all()

    data = [
        {
            'id': fornecedor.id,
            'razao_social': fornecedor.razao_social,
            'cnpj': fornecedor.cnpj,
            'tipo_material': fornecedor.get_tipo_material_display(),
            'certificacao_ambiental': fornecedor.certificacao_ambiental,
            'licenca_operacao': fornecedor.licenca_operacao,
            'registroidade': fornecedor.nota_qualidade,
            'estado': {
                'sigla': fornecedor.estado.sigla,
                'nome': fornecedor.cidade.estado.nome,
            },
            'cidade': {
                'id': fornecedor.cidade.id,
                'nome': fornecedor.cidade.nome,
            },
        }
        for fornecedor in fornecedores
    ]

    return JsonResponse(data, safe=False)
