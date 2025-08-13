# projects/signals.py
from django.core.mail import mail_admins
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ProjectAccessLog


@receiver(post_save, sender=ProjectAccessLog)
def notify_on_denied(sender, instance, created, **kwargs):
    if created and instance.status == ProjectAccessLog.DENIED:
        mail_admins(
            subject=f"Denied project access: {instance.project}",
            message=f"{instance.ts}: {instance.user} ({instance.ip}) tried {instance.path} [{instance.reason}]"
        )



# This signal handler sends an email to site admins whenever a project access is denied.
# It includes the project name, user details, IP address, and reason for denial.
# This is useful for monitoring access attempts and ensuring that only authorized users can view project details.