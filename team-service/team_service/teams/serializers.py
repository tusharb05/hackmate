from rest_framework import serializers
from .models import TeamApplication, TeamJoinRequest, CustomUser, Skill


# class CreateTeamApplicationSerializer(serializers.ModelSerializer):
#     member_user_ids = serializers.ListField(child=serializers.IntegerField())
#     skills = serializers.ListField(child=serializers.IntegerField())  

#     class Meta:
#         model = TeamApplication
#         fields = [
#             'title',
#             'description',
#             'leader_user_id',
#              'leader_name'
#             'team_name',
#             'member_user_ids',
#             'hackathon_date',
#             'skills',
#             'capacity',
#         ]

#     def create(self, validated_data):
#         member_user_ids = validated_data.pop('member_user_ids')
#         skills = validated_data.pop('skills')
#         capacity_left = validated_data['capacity'] - len(member_user_ids)

#         team_application = TeamApplication.objects.create(
#             **validated_data,
#             member_user_ids=member_user_ids,
#             skills=skills,
#             capacity_left=capacity_left
#         )

#         return team_application

class CreateTeamApplicationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TeamApplication
        fields = [
            'title', 'description', 'team_name', 'capacity', 'hackathon_date',
            'leader_user_id', 'skills', 'member_user_ids'
        ]
 
        read_only_fields = ['leader_user_id', 'skills', 'member_user_ids']

    def create(self, validated_data):
        """
        This method is called when `serializer.save()` is executed in the view.
        It handles the creation of the TeamApplication instance.
        """

        capacity = validated_data.get('capacity')
        validated_data['capacity_left'] = capacity - 1
        
       
        validated_data['member_user_ids'] = [validated_data.get('leader_user_id')]

        team_application = TeamApplication.objects.create(**validated_data)
        return team_application
    


class TeamApplicationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamApplication
        fields = [
            'id',
            'title',
            'description',
            'leader_user_id',
            # 'leader_name',
            'team_name',
            'skills',
            'capacity',
            'capacity_left',
            'status',
            'hackathon_date',
            'created_at',
        ]


class TeamJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamJoinRequest
        fields = [
            'id',
            'team_application',
            'user_id',
            'message',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']


class TeamJoinRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamJoinRequest
        fields = [
            'id',
            'team_application',
            'user_id',
            # 'user_name',
            'message',
            'status',
            'created_at',
            'updated_at',
        ]


class TeamJoinRequestStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamJoinRequest
        fields = ['status']

    def validate_status(self, value):
        if value not in ['accepted', 'rejected']:
            raise serializers.ValidationError("Status must be either 'accepted' or 'rejected'.")
        return value
    

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class FetchSkillsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"