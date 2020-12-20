import os

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = """
    Sets the environment variable to production or development
    based on the args
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "config", type=str,
            help="dev or prod (dev by default)",
            default="dev"
        )

    def handle(self, *args, **kwargs):
        conf = kwargs["config"]
        if conf == "dev":
            os.environ["DJANGO_SETTINGS_MODULE"] = "main.settings.development"
            self.stdout.write("The environment is set to development")
        elif conf == "prod":
            os.environ["DJANGO_SETTINGS_MODULE"] = "main.settings.production"
            self.stdout.write("The environment is set to production")
        else:
            raise CommandError("Invalid arguments passed")
