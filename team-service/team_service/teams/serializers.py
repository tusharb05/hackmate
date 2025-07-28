# serializers.py

from rest_framework import serializers
from .models import TeamApplication, TeamJoinRequest, CustomUser, Skill

# --- Base Serializers ---

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'profile_image', 'email'] # More specific than '__all__'

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
