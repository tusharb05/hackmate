# serializers.py

from rest_framework import serializers
from .models import TeamApplication, TeamJoinRequest, CustomUser, Skill
from django.conf import settings
import boto3
from botocore.exceptions import ClientError

# --- Base Serializers ---


import logging

# It's good practice to set up a logger for utility functions
logger = logging.getLogger(__name__)

def generate_presigned_s3_url(object_key: str) -> str | None:
    """
    Generates a pre-signed URL for a given S3 object key.

    This function is designed to work with a CharField that stores the
    path to the file in S3 (e.g., 'profile_images/scdc9r8ud5pb1.jpg').

    Args:
        object_key: The key (path) of the object in the S3 bucket.

    Returns:
        A pre-signed URL string if successful, otherwise None.
    """
    if not object_key:
        return None

    # Initialize the S3 client using credentials from Django settings
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
        # You might need to add this for pre-signed URLs
        config=boto3.session.Config(signature_version='s3v4')
    )

    try:
        # Generate the pre-signed URL.
        # The 'Key' is the object_key passed to the function.
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': object_key
            },
            ExpiresIn=3600  # URL expires in 1 hour (in seconds)
        )
        return presigned_url
    except ClientError as e:
        # Log the error for debugging purposes
        logger.error(f"Error generating pre-signed URL for key '{object_key}': {e}")
        return None


from .utils.generate_s3_url import generate_presigned_s3_url

class CustomUserSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'full_name', 'profile_image']

    def get_profile_image(self, obj):
        return generate_presigned_s3_url(obj.profile_image)
    

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'skill']

class FetchSkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"

# --- Team Creation Serializers ---

class CreateTeamApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamApplication
        fields = ['title', 'description', 'team_name', 'capacity', 'hackathon_date']
    # Removed read_only_fields and create method as they are handled in the view

# --- Join Request Serializers ---

# FIX: Consolidated into a single, correct definition for TeamJoinRequestSerializer
class TeamJoinRequestSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True) # Fetch user details based on user_id relationship

    class Meta:
        model = TeamJoinRequest
        fields = ['id', 'user_id', 'message', 'status', 'created_at', 'user']

class TeamJoinRequestStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamJoinRequest
        fields = ['status']

    def validate_status(self, value):
        if value not in ['accepted', 'rejected']:
            raise serializers.ValidationError("Status must be either 'accepted' or 'rejected'.")
        return value

# --- Listing and Detail Serializers ---

class TeamApplicationListSerializer(serializers.ModelSerializer):
    leader_name = serializers.SerializerMethodField()
    skill_names = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()

    class Meta:
        model = TeamApplication
        fields = [
            'id', 'title', 'description', 'leader_user_id', 'leader_name',
            'team_name', 'skills', 'skill_names', 'capacity', 'capacity_left',
            'status', 'hackathon_date', 'created_at', 'user_role',
        ]

    def get_leader_name(self, obj):
        user = self.context.get("user_map", {}).get(obj.leader_user_id)
        return user.full_name if user else None

    def get_skill_names(self, obj):
        skill_map = self.context.get("skill_map", {})
        return [skill_map.get(skill_id) for skill_id in obj.skills if skill_map.get(skill_id)]

    def get_user_role(self, obj):
        user_id = self.context.get("current_user_id")
        if user_id is None: return "default"
        if int(obj.leader_user_id) == int(user_id): return "owner"
        if int(user_id) in obj.member_user_ids: return "member"
        if int(obj.id) in self.context.get("user_join_requests_map", set()): return "pending"
        return "default"



class TeamApplicationDetailSerializer(serializers.ModelSerializer):
    skill_names = serializers.SerializerMethodField()
    leader = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = TeamApplication
        fields = [
            'id', 'title', 'description',
            'team_name', 'capacity', 'capacity_left',
            'status', 'hackathon_date', 'created_at', 'updated_at',
            'skills', 'skill_names', 'leader_user_id', 'leader',
            'member_user_ids', 'members',
        ]

    def get_skill_names(self, obj):
        skill_map = self.context.get("skill_map", {})
        return [skill_map.get(skill_id) for skill_id in obj.skills if skill_map.get(skill_id)]

    def get_leader(self, obj):
        user_map = self.context.get("user_map", {})
        user = user_map.get(obj.leader_user_id)
        return CustomUserSerializer(user).data if user else None

    def get_members(self, obj):
        user_map = self.context.get("user_map", {})
        member_data = []
        for user_id in obj.member_user_ids:
            user = user_map.get(user_id)
            if user:
                member_data.append(CustomUserSerializer(user).data)
        return member_data
