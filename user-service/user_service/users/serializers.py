from rest_framework import serializers
from .models import CustomUser, Skill

class UserDetailSerializer(serializers.ModelSerializer):
    skills = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "profile_image",
            "skills",
        ]

    def get_skills(self, obj):
        return [s.skill for s in obj.skills.all()]

    def get_profile_image(self, obj):
        request = self.context.get("request")
        if obj.profile_image and request is not None:
            return request.build_absolute_uri(obj.profile_image.url)
        elif obj.profile_image:
            return obj.profile_image.url
        return None