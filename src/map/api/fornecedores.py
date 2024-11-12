from django.http import JsonResponse
from map.models import FornecedorMateriaPrima
from map.utils.distance_calculator import DistanceCalculator

HOST_CITY = 'Sete Lagoas, MG'


def get_fornecedores(request):
    fornecedores = FornecedorMateriaPrima.objects.select_related('cidade', 'estado').all()

    data = []
    for fornecedor in fornecedores:
        distance = DistanceCalculator.get_distance(f'{fornecedor.cidade.nome}, {fornecedor.cidade.estado}', HOST_CITY)
        data.append({
            'id': fornecedor.id,
            'razao_social': fornecedor.razao_social,
            'cpf_cnpj': fornecedor.cpf_cnpj,
            'tipo_material': fornecedor.get_tipo_material_display(),
            'licenca_ambiental': fornecedor.licenca_ambiental,
            'cadastro_tecnico_federal': fornecedor.cadastro_tecnico_federal,
            'registro_ief': fornecedor.registro_ief,
            'avaliacao': fornecedor.avaliacao,
            'estado': {
                'sigla': fornecedor.estado.sigla,
                'nome': fornecedor.estado.nome,
            },
            'cidade': {
                'id': fornecedor.cidade.id,
                'nome': fornecedor.cidade.nome,
            },
            'distancia_em_metros': distance.distance_in_meters,
        })

    return JsonResponse(data, safe=False)
