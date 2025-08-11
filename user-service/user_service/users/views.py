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
from .serializers import UserDetailSerializer, CustomUserDetailSerializer
from django.core.files.storage import default_storage
from rest_framework.exceptions import NotFound

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user:
            token = generate_jwt(user)
            return Response({
                "token": token,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "profile_image": request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
                }
            })
        return Response({"error": "Invalid credentials"}, status=401)
    


class RegisterView(APIView):
    def post(self, request):
        email = request.data.get("email")
        full_name = request.data.get("full_name")
        password = request.data.get("password")
        
        skills_names = request.POST.getlist("skills")
        profile_image_file = request.FILES.get("profile_image")
        print('check 1')
        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=400)
        print('check 2')
        valid_skills = []
        for skill_name in skills_names:
            skill_name_cleaned = skill_name.strip()
            skill_obj, created = Skill.objects.get_or_create(skill=skill_name_cleaned)
            if created:
                publish_skill_created_event(skill_obj)
            valid_skills.append(skill_obj)
        print('check 3')
        user = CustomUser.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
            profile_image=profile_image_file
        )
        print('check 4')
        # print("USER")
        # print(user.profile_image)
        # print("\n\n\n\n\n\n\n\n\n")
        
        user.skills.set(valid_skills)
        publish_user_created(user)
        print('check 5')
        token = generate_jwt(user)
        return Response({
            "token": token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "profile_image": request.build_absolute_uri(user.profile_image.url) if user.profile_image else None
            }
        }, status=status.HTTP_201_CREATED)




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


class UserBatchDetailView(APIView):
    """
    GET /api/users/details/?ids=2,4,6
    Returns [{"id":2, "full_name":..., ...}, ...]
    """
    def get(self, request):
        ids_param = request.query_params.get("ids", "")
        try:
            ids = [int(i) for i in ids_param.split(",") if i.strip()]
        except ValueError:
            return Response(
                {"detail": "Invalid ids parameter; must be comma‑separated ints."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = CustomUser.objects.filter(id__in=ids)
        serializer = UserDetailSerializer(users, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class PublicUserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = CustomUserDetailSerializer(user, context={"request": request})
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            raise NotFound("User not found.")

