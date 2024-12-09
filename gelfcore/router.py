from django.urls import path as djpath


class Router:
    """
    Classe para servir de decorator para registrar rotas.

    route = Router(prefix='api/')

    @route('example/')
    def example_view(): ...
    """

    def __init__(self, prefix=None):
        # Prefixo opcional para todas as rotas
        self.prefix = prefix.rstrip('/') + '/' if prefix else ''

        # Dicionário para armazenar rotas
        # e suas views relacionadas
        self.map = {}

    def __call__(self, path='', /, name=None):
        def decorator(view):
            full_path = f'{self.prefix}{path.lstrip("/")}'
            assert full_path not in self.map, f'Rota duplicada: {full_path}'
            self.map[full_path] = view, name
            return view

        return decorator

    @property
    def urls(self):
        """
        Gera os objetos de rota Django usando o prefixo.
        """

        for path, (view, name) in self.map.items():
            if isinstance(view, type):
                view = view.as_view()

            yield djpath(path, view, name=name)
