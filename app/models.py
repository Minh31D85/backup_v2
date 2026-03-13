from django.db import models
from django.conf import settings


class Application(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    name = models.CharField(max_length=120)
    identifier = models.CharField(max_length=120)
    schema_version = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "identifier")

    def __str__(self):
        return self.name
    

class Group(models.Model):
    application =  models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="groups",
        db_index=True
    )
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("application", "name")

    def __str__(self):
        return self.name


class PasswordItem(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name="passwords"
    )
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, blank=True, null=True)
    email =  models.EmailField(blank=True, null=True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
