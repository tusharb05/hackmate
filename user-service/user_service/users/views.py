from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import CustomUser, Skill
from .utils.jwt_utils import generate_jwt
from rest_framework import status

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
        # skills_names = request.data.get("skills", [])
        skills_names = request.POST.getlist("skills")
        print(request.POST)

        profile_image_file = request.FILES.get("profile_image")  

        if CustomUser.objects.filter(email=email).exists():
            return Response({"error": "Email already registered."}, status=400)

        valid_skills = []
        for skill_name in skills_names:
            skill_obj, _ = Skill.objects.get_or_create(skill__iexact=skill_name.strip())
            valid_skills.append(skill_obj)

        # Create user with profile image
        user = CustomUser.objects.create_user(
            email=email,
            full_name=full_name,
            password=password,
            profile_image=profile_image_file
        )
        user.skills.set(valid_skills)

        token = generate_jwt(user)
        return Response({"token": token}, status=status.HTTP_201_CREATED)


