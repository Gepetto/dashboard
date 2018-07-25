from rainboard.models import Robotpkg

logger = logging.getLogger('rainboard.images')


class Command(BaseCommand):
    help = 'Populate database with Docker images data'

    def handle(self, *args, **options):
        for rpkg in Robotpkg.objects.all():
            rpkg.update_images()
