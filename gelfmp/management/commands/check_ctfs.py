import asyncio

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand

from gelfmp.models import Document, Supplier
from gelfmp.models.choices import DocumentType
from gelfmp.services.ibama_ctf import IbamaCTFService


class Command(BaseCommand):
    async def task(self):
        cpf_cnpj_list = await sync_to_async(lambda: list(Supplier.objects.values_list('cpf_cnpj', flat=True)))()
        ctf_service = IbamaCTFService()

        result = await ctf_service.bulk_fetch(cpf_cnpj_list)

        for is_valid, corporate_name, cpf_cnpj in result:
            if not is_valid:
                # Verifica se o fornecedor possui uma
                # dispensa de licenciamento ambiental, o que
                # significa que não tem necessidade de um  CTF.
                excemption = await sync_to_async(
                    lambda: Document.objects.filter(
                        supplier__cpf_cnpj=cpf_cnpj,
                        document_type=DocumentType.EXCEMPTION,
                    ).first()
                )()

                if not excemption:
                    self.stdout.write(f'CTF inválido para o fornecedor {corporate_name} ({cpf_cnpj})')

    def handle(self, *args, **kwargs):
        asyncio.run(self.task())
