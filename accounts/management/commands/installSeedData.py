from django.core.management import BaseCommand

from onetutor.operations import seedDataOperations

BOOLEAN = [True, False]


class Command(BaseCommand):
    help = "Install seed data"

    def handle(self, *args, **kwargs):
        seedDataOperations.runSeedDataInstaller()
