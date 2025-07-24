from django.db import models
from django.contrib.postgres.fields import ArrayField

class TeamApplication(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    leader_user_id = models.IntegerField()
    # leader_name = models.CharField(max_length=255)
    team_name = models.CharField(max_length=100)

    member_user_ids = ArrayField(models.IntegerField(default=[]))  
    # required_skill_ids = ArrayField(models.IntegerField()) 
    skills = ArrayField(models.IntegerField(default=[]))

    capacity = models.PositiveIntegerField()
    capacity_left = models.PositiveIntegerField()

    status = models.CharField(
        max_length=10,
        choices=[
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('filled', 'Filled'),
            ('expired', 'Expired')
        ],
        default='open'
    )

    hackathon_date = models.DateField(blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class TeamJoinRequest(models.Model):
    team_application = models.ForeignKey(TeamApplication, on_delete=models.CASCADE)
    user_id = models.IntegerField()  # Refers to CustomUser.id (integer)
    # user_name = models.CharField()
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('pending', 'Pending')
        ],
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CustomUser(models.Model):
    id = models.IntegerField(primary_key=True)       
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    profile_image = models.URLField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.email
    

class Skill(models.Model):
    id = models.IntegerField(primary_key=True) 
    skill = models.CharField(max_length=100)

    def __str__(self):
        return self.skill