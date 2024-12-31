import httpx
from django.core.cache import cache


class CNPJInfoService:
    """Classe para buscar informações de um CNPJ."""

    URL = 'https://open.cnpja.com/office/{cnpj}'
    CACHE_TIMEOUT = 60 * 60 * 12  # 12 horas

    def fetch(self, cnpj):
        cache_key = f'cnpj_info_{cnpj}'

        if cached := cache.get(cache_key):
            return cached

        response = httpx.get(self.URL.format(cnpj=cnpj))

        if response.status_code != 200:
            raise ValueError(f'Failed to fetch CNPJ info for {cnpj}')

        data = response.json()

        cache.set(cache_key, data, self.CACHE_TIMEOUT)

        return data
