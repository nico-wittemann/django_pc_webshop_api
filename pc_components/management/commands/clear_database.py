from pc_components.models import Component, Pc, Pc_Components
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Deletes all data from the database'

    def handle(self, *args, **options):
        # Delete all PC-component relationships
        Pc_Components.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All PC-component relationships deleted'))

        # Delete all PCs
        Pc.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All PCs deleted'))

        # Delete all components
        Component.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('All components deleted'))

        self.stdout.write(self.style.SUCCESS('Database successfully cleared'))