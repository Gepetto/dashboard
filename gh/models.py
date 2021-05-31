from django.db import models

# from ..rainboard import models as rb_models


class GithubCheckSuite(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
