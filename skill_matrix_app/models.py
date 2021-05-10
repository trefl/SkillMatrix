from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
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

class Divisions(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    objects = models.Manager()


class Groups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    objects = models.Manager()


class Subgroups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    group_id = models.ForeignKey(Groups, on_delete=models.CASCADE)
    objects = models.Manager()


class Positions(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    objects = models.Manager()

class Workers(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    birthday = models.DateField()
    profile_pic = models.ImageField(default='/media/default/avatar.png')
    archival = models.BooleanField(default=False)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    position_id = models.ForeignKey(Positions, on_delete=models.DO_NOTHING, blank=True, null=True)
    group_id = models.ForeignKey(Groups, on_delete=models.DO_NOTHING, blank=True, null=True)
    subgroup_id = models.ForeignKey(Subgroups, on_delete=models.DO_NOTHING, blank=True, null=True)
    division_id = models.ForeignKey(Divisions, on_delete=models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()


class Skills(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    company_id = models.ForeignKey(Companies, on_delete=models.CASCADE)
    subgroup_id = models.ForeignKey(Subgroups, on_delete=models.DO_NOTHING, blank=True, null=True)
    objects = models.Manager()

class Ratings(models.Model):
    id = models.AutoField(primary_key=True)
    worker_id = models.ForeignKey(Workers, on_delete=models.CASCADE)
    skill_id = models.ForeignKey(Skills, on_delete=models.CASCADE)
    rate = models.IntegerField(default=0, validators=[MaxValueValidator(4), MinValueValidator(0)])
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

