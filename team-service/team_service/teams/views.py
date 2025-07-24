from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import FetchSkillsSerializer, CustomUserSerializer, CreateTeamApplicationSerializer,TeamApplicationListSerializer, TeamJoinRequestSerializer, TeamJoinRequestStatusUpdateSerializer
from rest_framework.response import Response
import requests
import os
from .models import TeamApplication, TeamJoinRequest, CustomUser, Skill
from datetime import date
from .utils.verify_user import verify_user
from rest_framework.exceptions import AuthenticationFailed


# Create your views here.

class CreateTeamApplicationView(APIView):
    def post(self, request):
        # Step 1: Validate token using the local verify_user
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            user_id = verify_user(token)
        except IndexError:
            return Response({"error": "Authorization header is missing or invalid"}, status=401)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=401)

        # Step 2: Verify the user exists in the local db
        try:
            CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found in this service"}, status=404)

        # Step 3: Extract and validate data from request body
        data = request.data
        skills = data.get("skills", [])
        serializer = CreateTeamApplicationSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        
        validated_data = serializer.validated_data

        # Step 4: Sync skills with user-service to get/create skill IDs
        user_service_skill_sync_url = os.getenv("USER_SERVICE_SKILL_SYNC_URL", "http://user-service:8000/api/sync-get-skills/")
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            skill_sync_res = requests.post(user_service_skill_sync_url, json={"skills": skills}, headers=headers)
            skill_sync_res.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            skill_data = skill_sync_res.json()
            skill_ids = [skill["id"] for skill in skill_data.get("skills", [])]

        except requests.exceptions.RequestException as e:
            return Response({"error": "Skill sync with user-service failed", "details": str(e)}, status=502) # 502 Bad Gateway is appropriate here
        except (KeyError, TypeError):
             return Response({"error": "Invalid response format from skill service"}, status=500)

        # Step 5: Create TeamApplication
        try:
            team_app = TeamApplication.objects.create(
                leader_user_id=user_id,
                skills=skill_ids,
                member_user_ids=[user_id],
                capacity_left=validated_data['capacity'],
                **validated_data
            )
        except Exception as e:
            return Response({"error": "Could not create team application", "details": str(e)}, status=500)

        return Response({
            "message": "Team application created successfully",
            "team_id": team_app.id,
            "skills": skill_data # Return the full skill data from user-service
        }, status=201)

class ListTeamApplicationsView(APIView):
    def get(self, request):
        try:
            team_apps = TeamApplication.objects.all().order_by('-created_at')
            serializer = TeamApplicationListSerializer(team_apps, many=True)
            return Response(serializer.data, status=200)
        except Exception as e:
            return Response({"error": "Failed to fetch team applications", "details": str(e)}, status=500)

class CreateTeamJoinRequestView(APIView):
    def post(self, request):
        # Step 1: Validate token using local utility
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            user_id = verify_user(token)
        except IndexError:
            return Response({"error": "Authorization header is missing or invalid"}, status=401)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=401)
        
        # Step 2: Verify user exists locally
        try:
            CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found in this service"}, status=404)

        # Step 3: Validate request data
        data = request.data
        try:
            team_app_id = data["team_application"]
            message = data.get("message", "")
        except KeyError as e:
            return Response({"error": f"Missing required field: {e.args[0]}"}, status=400)

        # Step 4: Validate team application
        try:
            team_app = TeamApplication.objects.get(id=team_app_id)
        except TeamApplication.DoesNotExist:
            return Response({"error": "Team application not found"}, status=404)

        if team_app.hackathon_date < date.today():
            return Response({"error": "Hackathon date has already passed"}, status=400)

        if TeamJoinRequest.objects.filter(team_application=team_app, user_id=user_id).exists():
            return Response({"error": "Join request already submitted for this team"}, status=400)

        # Step 5: Create join request
        try:
            join_request = TeamJoinRequest.objects.create(
                team_application=team_app,
                user_id=user_id,
                message=message,
            )
            serializer = TeamJoinRequestSerializer(join_request)
            return Response(serializer.data, status=201)
        except Exception as e:
            return Response({"error": "Could not create join request", "details": str(e)}, status=500)

class ListTeamJoinRequestsView(APIView):
    def get(self, request, team_id):
        # Step 1: Validate token and get user_id
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            user_id = verify_user(token)
        except IndexError:
            return Response({"error": "Authorization header is missing or invalid"}, status=401)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=401)

        # Step 2: Validate the team application and leader
        try:
            team_app = TeamApplication.objects.get(id=team_id)
        except TeamApplication.DoesNotExist:
            return Response({"error": "Team application not found"}, status=404)

        if int(team_app.leader_user_id) != int(user_id):
            return Response({"error": "Only the team leader can view join requests"}, status=403)

        # Step 3: Fetch all join requests for this team
        join_requests = TeamJoinRequest.objects.filter(team_application=team_app).order_by('-created_at')
        serializer = TeamJoinRequestSerializer(join_requests, many=True)
        return Response(serializer.data, status=200)

class UpdateJoinRequestStatusView(APIView):
    def patch(self, request, request_id):
        # Step 1: Authenticate requester
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            user_id = verify_user(token)
        except IndexError:
            return Response({"error": "Authorization header is missing or invalid"}, status=401)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=401)
            
        # Step 2: Fetch join request and verify leader
        try:
            join_request = TeamJoinRequest.objects.select_related('team_application').get(id=request_id)
        except TeamJoinRequest.DoesNotExist:
            return Response({"error": "Join request not found"}, status=404)

        team_app = join_request.team_application

        if int(team_app.leader_user_id) != int(user_id):
            return Response({"error": "Only the team leader can update the request status"}, status=403)

        if join_request.status != 'pending':
            return Response({"error": f"Request already {join_request.status}"}, status=400)
        
        # Step 3: Update status
        serializer = TeamJoinRequestStatusUpdateSerializer(join_request, data=request.data, partial=True)
        if serializer.is_valid():
            new_status = serializer.validated_data.get('status')
            
            if new_status == 'accepted':
                if team_app.capacity_left <= 0:
                    return Response({"error": "Team is already full"}, status=400)

                team_app.member_user_ids.append(join_request.user_id)
                team_app.capacity_left -= 1
                team_app.save()

            serializer.save()
            return Response({"message": f"Request {new_status} successfully"})
        
        return Response(serializer.errors, status=400)

class FetchUserView(APIView):
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response({"data": serializer.data})

class FetchSkillsView(APIView):
    def get(self, request):
        skills = Skill.objects.all()
        serializer = FetchSkillsSerializer(skills, many=True)
        return Response({"data": serializer.data})











# class CreateTeamApplicationView(APIView):
#     def post(self, request):
#         # Step 1: Validate token
#         try:
#             token = request.headers.get('Authorization', '').split(' ')[1]
#             print("TOKEN: ")
#             print(token)
#         except IndexError:
#             return Response({"error": "Invalid or missing token"}, status=400)

#         headers = {
#             'Authorization': f'Bearer {token}'
#         }

#         user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000/api/verify-user/")
#         user_service_skill_sync_url = os.getenv("USER_SERVICE_SKILL_SYNC_URL", "http://user-service:8000/api/sync-get-skills/")

#         try:
#             # Step 2: Verify user
#             response = requests.get(user_service_url, headers=headers)
#             print("User service response JSON:", response.json())
#             if response.status_code != 200 or not response.json().get("valid"):
#                 return Response({"error": "Unauthorized"}, status=401)

#             user_json = response.json()
#             user_id = user_json.get("user_id")
#             # leader_name = user_json.get("name")  
#         except Exception as e:
#             return Response({"error": "User service unreachable", "details": str(e)}, status=500)

#         # Step 3: Extract data from request body
#         data = request.data
#         try:
#             title = data["title"]
#             description = data.get("description", "")
#             team_name = data["team_name"]
#             capacity = int(data["capacity"])
#             hackathon_date = data["hackathon_date"]
#             skills = data.get("skills", [])  # List of skill names (strings)
#         except KeyError as e:
#             return Response({"error": f"Missing required field: {e.args[0]}"}, status=400)

#         # Step 4: Sync skills with user-service
#         try:
#             skill_sync_res = requests.post(user_service_skill_sync_url, json={"skills": skills}, headers=headers)
#             if skill_sync_res.status_code != 200:
#                 return Response({"error": "Failed to sync skills"}, status=skill_sync_res.status_code)

#             skill_data = skill_sync_res.json()
#             skill_ids = [skill["id"] for skill in skill_data.get("skills", [])]

#         except Exception as e:
#             return Response({"error": "Skill sync failed", "details": str(e)}, status=500)


#         # Step 5: Create TeamApplication
#         try:
#             team_app = TeamApplication.objects.create(
#                 title=title,
#                 description=description,
#                 leader_user_id=user_id,
#                 # leader_name=leader_name, 
#                 team_name=team_name,
#                 capacity=capacity,
#                 capacity_left=capacity,  # initially all spots are open
#                 skills=skill_ids,
#                 member_user_ids=[user_id],  # leader is also a member
#                 hackathon_date=hackathon_date,
#             )
#         except Exception as e:
#             return Response({"error": "Could not create team application", "details": str(e)}, status=500)


#         return Response({
#             "message": "Team application created successfully",
#             "team_id": team_app.id,
#             "skills": skill_data
#         }, status=201)
        

# class ListTeamApplicationsView(APIView):
#     def get(self, request):
#         try:
#             team_apps = TeamApplication.objects.all().order_by('-created_at')
#             serializer = TeamApplicationListSerializer(team_apps, many=True)
#             return Response(serializer.data, status=200)
#         except Exception as e:
#             return Response({"error": "Failed to fetch team applications", "details": str(e)}, status=500)


# class CreateTeamJoinRequestView(APIView):
#     def post(self, request):

#         try:
#             token = request.headers.get('Authorization', '').split(' ')[1]
#         except IndexError:
#             return Response({"error": "Invalid or missing token"}, status=400)

#         headers = {'Authorization': f'Bearer {token}'}
#         user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000/api/verify-user/")

#         try:
#             res = requests.get(user_service_url, headers=headers)
#             if res.status_code != 200 or not res.json().get("valid"):
#                 return Response({"error": "Unauthorized"}, status=401)
#             user_id = res.json().get("user_id")
#             # user_name = res.json().get("name")
#         except Exception as e:
#             return Response({"error": "User service unreachable", "details": str(e)}, status=500)

#         data = request.data
#         try:
#             team_app_id = data["team_application"]
#             message = data.get("message", "")
#         except KeyError as e:
#             return Response({"error": f"Missing required field: {e.args[0]}"}, status=400)


#         try:
#             team_app = TeamApplication.objects.get(id=team_app_id)
#         except TeamApplication.DoesNotExist:
#             return Response({"error": "Team application not found"}, status=404)

#         try:
#             hackathon_date = team_app.hackathon_date
#             if hackathon_date < date.today():
#                 return Response({"error": "Hackathon date has already passed"}, status=400)
#         except Exception:
#             return Response({"error": "Invalid hackathon date in record"}, status=500)


#         if TeamJoinRequest.objects.filter(team_application=team_app, user_id=user_id).exists():
#             return Response({"error": "Join request already submitted for this team"}, status=400)


#         try:
#             join_request = TeamJoinRequest.objects.create(
#                 team_application=team_app,
#                 user_id=user_id,
#                 # user_name=user_name,
#                 message=message,
#             )
#             serializer = TeamJoinRequestSerializer(join_request)
#             return Response(serializer.data, status=201)
#         except Exception as e:
#             return Response({"error": "Could not create join request", "details": str(e)}, status=500)


# class ListTeamJoinRequestsView(APIView):
#     def get(self, request, team_id):
#         # Step 1: Extract and verify token
#         try:
#             token = request.headers.get('Authorization', '').split(' ')[1]
#         except IndexError:
#             return Response({"error": "Invalid or missing token"}, status=400)

#         headers = {'Authorization': f'Bearer {token}'}
#         user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000/api/verify-user/")

#         try:
#             res = requests.get(user_service_url, headers=headers)
#             if res.status_code != 200 or not res.json().get("valid"):
#                 return Response({"error": "Unauthorized"}, status=401)
#             user_id = res.json().get("user_id")
#         except Exception as e:
#             return Response({"error": "User service unreachable", "details": str(e)}, status=500)

#         # Step 2: Validate the team application and leader
#         try:
#             team_app = TeamApplication.objects.get(id=team_id)
#             print("CREATOR OF APPLICATION: ")
#             print(team_app.leader_user_id)
#             print("SENDER ID: ")
#             print(user_id)
#         except TeamApplication.DoesNotExist:
#             return Response({"error": "Team application not found"}, status=404)

#         if int(team_app.leader_user_id) != int(user_id):
#             return Response({"error": "Only the team leader can view join requests"}, status=403)

#         # Step 3: Fetch all join requests for this team
#         join_requests = TeamJoinRequest.objects.filter(team_application=team_app).order_by('-created_at')
#         serializer = TeamJoinRequestSerializer(join_requests, many=True)
#         return Response(serializer.data, status=200)


# class UpdateJoinRequestStatusView(APIView):
#     def patch(self, request, request_id):
#         # Step 1: Authenticate requester
#         try:
#             token = request.headers.get('Authorization', '').split(' ')[1]
#         except IndexError:
#             return Response({"error": "Invalid or missing token"}, status=400)

#         headers = {'Authorization': f'Bearer {token}'}
#         user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000/api/verify-user/")

#         try:
#             res = requests.get(user_service_url, headers=headers)
#             if res.status_code != 200 or not res.json().get("valid"):
#                 return Response({"error": "Unauthorized"}, status=401)
#             user_id = res.json().get("user_id")
#         except Exception as e:
#             return Response({"error": "User service unreachable", "details": str(e)}, status=500)


#         try:
#             join_request = TeamJoinRequest.objects.select_related('team_application').get(id=request_id)
#         except TeamJoinRequest.DoesNotExist:
#             return Response({"error": "Join request not found"}, status=404)

#         team_app = join_request.team_application

#         if int(team_app.leader_user_id) != int(user_id):
#             return Response({"error": "Only the team leader can update the request status"}, status=403)

#         if join_request.status != 'pending':
#             return Response({"error": f"Request already {join_request.status}"}, status=400)


#         serializer = TeamJoinRequestStatusUpdateSerializer(join_request, data=request.data, partial=True)
#         if serializer.is_valid():
#             new_status = serializer.validated_data.get('status')
#             serializer.save()


#             if new_status == 'accepted':
#                 if team_app.capacity_left <= 0:
#                     return Response({"error": "Team is already full"}, status=400)

#                 team_app.member_user_ids.append(join_request.user_id)
#                 team_app.capacity_left -= 1
#                 team_app.save()

#             return Response({"message": f"Request {new_status} successfully"})
#         return Response(serializer.errors, status=400)


# class FetchUserView(APIView):
#     def get(self, request):
#         users = CustomUser.objects.all()
#         serializer = CustomUserSerializer(users, many=True)
#         return Response({"data": serializer.data})
    

# class FetchSkillsView(APIView):
#     def get(self, request):
#         skills = Skill.objects.all()
#         serializer = FetchSkillsSerializer(skills, many=True)
#         return Response({"data": serializer.data})