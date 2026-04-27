from django.apps import AppConfig


class ClientsConfig(AppConfig):
    name = 'clients'

    def ready(self):
        # Import des signaux
        import clients.signals
