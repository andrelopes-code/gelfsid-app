from django.forms import model_to_dict
from django.http import JsonResponse
from ..models import Cidade, FornecedorMateriaPrima
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def get_cidades(request):
    estado_id = request.GET.get('estado')

    if estado_id:
        cidades = Cidade.objects.filter(estado_id=estado_id).values('id', 'nome')
        return JsonResponse(list(cidades), safe=False)

    return JsonResponse([], safe=False)


@staff_member_required
def get_fornecedor(request):
    fornecedor_id = request.GET.get('id')

    if fornecedor_id:
        fornecedor = FornecedorMateriaPrima.objects.filter(id=fornecedor_id).first()

        if fornecedor:
            fornecedor_data = model_to_dict(fornecedor)

            if fornecedor.cidade:
                fornecedor_data['cidade'] = {
                    'id': fornecedor.cidade.id,
                    'nome': fornecedor.cidade.nome,
                }

            return JsonResponse(fornecedor_data)
        else:
            return JsonResponse({'error': 'Fornecedor not found'}, status=404)
    else:
        return JsonResponse({'error': 'Fornecedor ID is required'}, status=400)
