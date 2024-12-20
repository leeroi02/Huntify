from django.db import models
from django.contrib.humanize.templatetags.humanize import naturaltime

# Create your models here.
class Notification(models.Model):
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {'Read' if self.is_read else 'Unread'}"
    
    @staticmethod
    def get_user_unread_notifications(user):
        """
        Static method to get unread notifications for a specific user.
        """
        return Notification.objects.filter(user=user, is_read=False).order_by('-created_at')