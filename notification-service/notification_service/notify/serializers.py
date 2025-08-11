from rest_framework import serializers
from notify.models import Notification, NotificationType

class NotificationSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField()
    leader_name = serializers.CharField()
    # profile_image = serializers.URLField()

    class Meta:
        model = Notification
        fields = ['id', 'user_id', 'message', 'type', 'team_application_id', 'is_read', 'created_at', 'team_name', 'leader_name']
