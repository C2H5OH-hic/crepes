from django.core.management.base import BaseCommand
from myapp.utils import enviar_informe_caja_diaria

class Command(BaseCommand):
    help = 'Envía el informe diario de caja por correo'

    def handle(self, *args, **kwargs):
        enviar_informe_caja_diaria()
        self.stdout.write(self.style.SUCCESS("Informe enviado correctamente"))
