from time import sleep

from django.core.management.base import BaseCommand

from gh.models import PushQueue


class Command(BaseCommand):
    help = "push something every minute"

    def handle(self, *args, **options):
        while True:
            sleep(60)
            if i := PushQueue.objects.order_by("?").first():
                try:
                    i.push()
                    i.delete()
                except Exception as e:
                    err = f"can't push {i} ({i.retry}): {e}"
                    self.stderr.write(err)
                    if i.retry < 10:
                        i.retry += 1
                        i.save()
                    else:
                        i.delete()
