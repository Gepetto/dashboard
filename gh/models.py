from django.db import models

# from ..rainboard import models as rb_models


class GithubCheckSuite(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)  # noqa: A003

    def __str__(self):
        return f"{self.id}"
