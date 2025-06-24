from enum import unique
from django.db import models
from psycopg2 import DATETIME
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    created_at = models.DateTimeField(auto_now_add=True)
    pcs = models.ManyToManyField('pc_components.Pc', through='User_Pc')
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class User_Pc(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pc = models.ForeignKey('pc_components.Pc', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.pc.id}"









