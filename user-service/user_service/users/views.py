from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import CustomUser, Skill
from .utils.jwt_utils import generate_jwt
from rest_framework import status
import jwt
import os
from .rabbitmq.sender_users import publish_user_created
from .rabbitmq.sender_skill_created import publish_skill_created_event

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            token = generate_jwt(user)
            return Response({"token": token})
        return Response({"error": "Invalid credentials"}, status=401)


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")
        full_name = request.data.get("full_name")
        password = request.data.get("password")

        # Get list of skill names
        skills_names = request.POST.getlist("skills")
        print(request.POST)

        # Get uploaded profile image (optional)
        profile_image_file = request.FILES.get("profile_image")

        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=400)

        valid_skills = []
        for skill_name in skills_names:
            skill_name_cleaned = skill_name.strip()
            skill_obj, created = Skill.objects.get_or_create(skill=skill_name_cleaned)
            
            # If skill is newly created, publish event
            if created:
                publish_skill_created_event(skill_obj)
            
            valid_skills.append(skill_obj)

        # Create user
        user = CustomUser.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
            profile_image=profile_image_file
        )

        # Assign skills
        user.skills.set(valid_skills)

        # Publish user.created (optional if you're syncing users too)
        publish_user_created(user)

        # Generate JWT token
        token = generate_jwt(user)
        return Response({"token": token}, status=status.HTTP_201_CREATED)


# class RegisterView(APIView):
#     def post(self, request):
#         email = request.data.get("email")
#         full_name = request.data.get("full_name")
#         password = request.data.get("password")
#         # skills_names = request.data.get("skills", [])
#         skills_names = request.POST.getlist("skills")
#         print(request.POST)

#         profile_image_file = request.FILES.get("profile_image")  

#         if CustomUser.objects.filter(email=email).exists():
#             return Response({"error": "Email already registered."}, status=400)

#         valid_skills = []
#         for skill_name in skills_names:
#             skill_obj, _ = Skill.objects.get_or_create(skill__iexact=skill_name.strip())
#             valid_skills.append(skill_obj)

#         # Create user with profile image
#         user = CustomUser.objects.create_user(
#             email=email,
#             full_name=full_name,
#             password=password,
#             profile_image=profile_image_file
#         )
#         user.skills.set(valid_skills)

#         publish_user_created(user)
        
#         token = generate_jwt(user)
#         return Response({"token": token}, status=status.HTTP_201_CREATED)


class VerifyUser(APIView):
    def get(self, request):
        try:
            token = request.headers['Authorization'].split(' ')[1]
            payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=["HS256"])
            # print(payload)
            # print("\n\n\n\n\n")
            user_id = payload.get("user_id")

            if not user_id:
                return Response({"valid": False, "error": "user_id not found in token"})

            print(f'userid: {user_id}')
            user = CustomUser.objects.get(id=user_id)
            print(user)
            return Response({"valid": True, "user_id": user_id, "name": user.full_name})
        except Exception as e:
            return Response({"valid": False, "error": str(e)})


class SyncAndReturnSkillsView(APIView):
    def post(self, request):
        skills = request.data.get('skills', [])
        if not isinstance(skills, list):
            return Response({"error": "skills must be a list"}, status=status.HTTP_400_BAD_REQUEST)
        
        result = []
        for skill in skills:
            skill_clean = skill.strip().lower()
            s, created = Skill.objects.get_or_create(skill=skill_clean)
            
            if created:
                publish_skill_created_event(s)

            result.append({'id': s.id, 'skill': s.skill})

        return Response({'skills': result}, status=status.HTTP_200_OK)
