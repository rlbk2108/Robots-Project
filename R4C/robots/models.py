from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


class Robot(models.Model):
    serial = models.CharField(max_length=5, blank=False, null=False, auto_created=True)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)

    class Meta:
        unique_together = ('model', 'version')


@receiver(pre_save, sender=Robot)
def validate_model_exists(sender, instance, **kwargs):
    if not Robot.objects.filter(model=instance.model).exists():
        raise ValidationError(f"Model '{instance.model}' does not exist in the system.")


@receiver(pre_save, sender=Robot)
def update_serial(sender, instance, **kwargs):
    instance.serial = f'{instance.model}-{instance.version}'
