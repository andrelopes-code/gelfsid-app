from django.http import JsonResponse
from map.models import FornecedorMateriaPrima
from map.utils.distance_calculator import DistanceCalculator


def get_fornecedores(request):
    fornecedores = FornecedorMateriaPrima.objects.select_related('cidade', 'estado').all()

    data = []
    for fornecedor in fornecedores:
        distance = DistanceCalculator.get_distance(
            f'{fornecedor.cidade.nome}, {fornecedor.cidade.estado}', 'Sete Lagoas, MG'
        )
        data.append({
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
            'distancia_em_metros': distance.distance_in_meters,
        })

    return JsonResponse(data, safe=False)
