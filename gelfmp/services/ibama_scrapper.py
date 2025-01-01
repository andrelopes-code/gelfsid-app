import asyncio

import httpx
import rich
from django.templatetags.static import static
from parsel import Selector
from weasyprint import CSS, HTML

URL = 'https://servicos.ibama.gov.br/ctf/publico/certificado_regularidade_consulta.php'
CONTENT_TYPE = 'application/x-www-form-urlencoded'


class IbamaCTFService:
    """Classe para buscar informações sobre o CTF de um CPF/CNPJ."""

    async def fetch(self, cpf_cnpj):
        data = {
            'num_cpf_cnpj': cpf_cnpj,
            'formDinAcao': 'Consultar',
        }

        async with httpx.AsyncClient(headers={'Content-Type': CONTENT_TYPE}) as client:
            response = await client.post(URL, data=data)

            # Caso a requisição falhe, aborta o processo.
            if response.status_code != 200:
                raise Exception(f'[{response.status_code}] Falha ao buscar o CTF de {cpf_cnpj}')

            selector = Selector(response.text)

            issue_date = selector.css('#dat_emissao::attr(value)').get()
            corporate_name = selector.css('#nom_pessoa::attr(value)').get()

            if not issue_date:
                return (False, corporate_name, cpf_cnpj)

            validity_date = selector.css('#dat_validade::attr(value)').get()
            registration_number = selector.css('#num_registro::attr(value)').get()

            rich.print(
                f'Razão Social: {corporate_name}\n'
                f'Registro: {registration_number}\n'
                f'Emissão: {issue_date}\n'
                f'Validade: {validity_date}\n'
            )

            return (True, corporate_name, cpf_cnpj)

    async def bulk_fetch(self, cpf_cnpj_list) -> tuple[bool, str, str]:
        return await asyncio.gather(*[self.fetch(cpf_cnpj) for cpf_cnpj in cpf_cnpj_list])

    def save_pdf(self, content, registration_number):
        HTML(string=content).write_pdf(
            f'{registration_number}.pdf',
            stylesheets=[
                CSS(static('css/ibama_ctf.css')),
            ],
        )
