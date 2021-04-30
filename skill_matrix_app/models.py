from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(AbstractUser):
    user_type_data = ((1, "Admin"), (2, "Manager"), (3, "Assistant"))
    user_type = models.CharField(default=1, choices=user_type_data, max_length=10)


class Admins(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default='/media/default/avatar.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Companies(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    logo = models.ImageField(default='/media/default/avatar.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Managers(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default='/media/default/avatar.png')
    company_id = models.ForeignKey(Companies, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Assistants(models.Model):
    id = models.AutoField(primary_key=True)
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic = models.ImageField(default='/media/default/avatar.png')
    company_id = models.ForeignKey(Companies, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Workers(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    objects = models.Manager()


class Groups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    objects = models.Manager()


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 1:
            Admins.objects.create(admin=instance)
        if instance.user_type == 2:
            Managers.objects.create(admin=instance, company_id=Companies.objects.get(id=1))
        if instance.user_type == 3:
            Assistants.objects.create(admin=instance, company_id=Companies.objects.get(id=1))


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.user_type == 1:
        instance.admins.save()
    if instance.user_type == 2:
        instance.managers.save()
    if instance.user_type == 3:
        instance.assistants.save()

