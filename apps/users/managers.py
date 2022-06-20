from django.contrib.auth.models import UserManager
from django.contrib.auth.hashers import make_password
from django.db import models

from statistics import mean


class UserManager(UserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.username = email
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        return super().create_superuser(email, password, **extra_fields)

    def with_roi_level_and_profit(self):
        return self.annotate(roi_level=models.Value('0'), profit=models.Value('0'))


class TraderQuerySet(models.QuerySet):
    def with_statistic(self):
        return self.annotate(roi_statistic=models.Value(0),
                             profit=models.Value(0),
                             people_in_groups=models.Count('groups__memberships', distinct=True),
                             people_copying=models.Value(0),
                             income_of_groups=models.Value(0),
                             addmission_to_groups=models.Value(0),
                             )

