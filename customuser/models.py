from django.db import models
from django.contrib.auth.models import User


class CustomUser(User):
    organization        = models.ForeignKey('organization.Organization',on_delete=models.CASCADE,related_name='user_organization')

    def __str__(self):
        return f"{self.id} ---  {self.username} --- For - {self.organization.name}"
