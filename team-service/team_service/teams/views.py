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
from django.core.files.storage import default_storage

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
            skill_sync_res.raise_for_status()

            skill_data = skill_sync_res.json()
            skill_ids = [skill["id"] for skill in skill_data.get("skills", [])]

        except requests.exceptions.RequestException as e:
            return Response({"error": "Skill sync with user-service failed", "details": str(e)}, status=502)
        except (KeyError, TypeError):
            return Response({"error": "Invalid response format from skill service"}, status=500)

        # Step 5: Create TeamApplication
        try:
            team_app = TeamApplication.objects.create(
                leader_user_id=user_id,
                skills=skill_ids,
                member_user_ids=[user_id],
                capacity_left=validated_data['capacity'] - 1,
                **validated_data
            )
        except Exception as e:
            return Response({"error": "Could not create team application", "details": str(e)}, status=500)

        return Response({
            "message": "Team application created successfully",
            "team_id": team_app.id,
            "skills": skill_data
        }, status=201)

class ListTeamApplicationsView(APIView):
    def get(self, request):
        try:
            # Step 1: Extract and verify JWT token
            token = request.headers.get("Authorization", "").split(" ")[1]
            user_id = verify_user(token)  # This should return the user_id
        except IndexError:
            user_id = None  # No token means unauthenticated
        except AuthenticationFailed:
            user_id = None  # Invalid token means unauthenticated

        # Step 2: Fetch all team applications
        team_apps = TeamApplication.objects.all().order_by("-created_at")

        # Step 3: Prepare maps to avoid N+1 queries
        user_ids = set(app.leader_user_id for app in team_apps)
        skill_ids = set(skill_id for app in team_apps for skill_id in app.skills)

        user_map = {
            user.id: user for user in CustomUser.objects.filter(id__in=user_ids)
        }
        skill_map = {
            skill.id: skill.skill for skill in Skill.objects.filter(id__in=skill_ids)
        }

        # Step 4: If user is logged in, find all pending join requests made by them
        user_join_requests_map = set()
        if user_id:
            pending_requests = TeamJoinRequest.objects.filter(
                user_id=user_id, status="pending"
            ).values_list("team_application_id", flat=True)
            user_join_requests_map = set(pending_requests)

        # Step 5: Serialize with custom context
        serializer = TeamApplicationListSerializer(
            team_apps,
            many=True,
            context={
                "user_map": user_map,
                "skill_map": skill_map,
                "current_user_id": user_id,
                "user_join_requests_map": user_join_requests_map,
            },
        )

        return Response(serializer.data, status=200)
    


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
        # — your existing auth + leader check —
        auth_header = request.headers.get("Authorization", "")
        try:
            token = auth_header.split()[1]
            user_id = verify_user(token)
        except Exception:
            return Response({"error": "Invalid or missing token"}, status=401)

        try:
            team_app = TeamApplication.objects.get(id=team_id)
        except TeamApplication.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)

        if int(team_app.leader_user_id) != int(user_id):
            return Response({"error": "Only leader can view requests"}, status=403)

        # Fetch join requests
        join_requests = list(
            TeamJoinRequest.objects
                .filter(team_application=team_app)
                .order_by("-created_at")
        )

        # 1️⃣ Collect all user_ids, dedupe
        user_ids = list({jr.user_id for jr in join_requests})
        if user_ids:
            # 2️⃣ Batch‑fetch from User Service
            try:
                resp = requests.get(
                    "http://user-service:8000/api/users/details/",
                    params={"ids": ",".join(map(str, user_ids))},
                    timeout=2
                )
                resp.raise_for_status()
                users = resp.json()
            except requests.RequestException as exc:
                return Response(
                    {"error": "Failed to fetch user details", "details": str(exc)},
                    status=502
                )
            # build a map: user_id → user‑object
            user_map = {u["id"]: u for u in users}
        else:
            user_map = {}

        # 3️⃣ Serialize and merge
        output = []
        for jr in join_requests:
            jr_data = TeamJoinRequestSerializer(jr).data
            jr_data["user_details"] = user_map.get(jr.user_id, None)
            output.append(jr_data)

        return Response(output, status=200)



from team_service.producers.send_notification import publish_notification_event

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

                # Add new member and reduce capacity
                team_app.member_user_ids.append(join_request.user_id)
                team_app.capacity_left -= 1

                # Check if team is now full
                if team_app.capacity_left == 0:
                    team_app.status = "filled"

                team_app.save()

            serializer.save()

            # Notification for other team members
            try:
                new_member = CustomUser.objects.get(id=join_request.user_id)
                new_member_name = new_member.full_name
            except CustomUser.DoesNotExist:
                new_member_name = "A new member"

            for member_id in team_app.member_user_ids:
                if member_id == join_request.user_id:
                    continue

                notification_payload = {
                    "user_id": member_id,
                    "team_application_id": team_app.id,
                    "message": f"{new_member_name} has joined your team '{team_app.team_name}'",
                    "type": "new_member_added"
                }
                publish_notification_event(notification_payload)

            # Notification to new member
            notification_payload = {
                "user_id": join_request.user_id,
                "team_application_id": team_app.id,
                "message": f"You have been added to team '{team_app.team_name}'",
                "type": "request_accepted"
            }
            publish_notification_event(notification_payload)

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


from .utils.generate_s3_url import generate_presigned_s3_url

class TeamMetaView(APIView):
    def get(self, request, team_id):
        try:
            team = TeamApplication.objects.get(id=team_id)
            leader = CustomUser.objects.get(id=team.leader_user_id)

            image_url = leader.profile_image
            print("URLLLLLLLLLLL")
            print(generate_presigned_s3_url(leader.profile_image))
            print("\n\n\n\n\n\n\n\n")
            
            return Response({
                "team_name": team.team_name,
                "leader_name": leader.full_name,
                "profile_image": image_url
            })

        except TeamApplication.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        except CustomUser.DoesNotExist:
            return Response({"error": "Leader not found"}, status=404)




from rest_framework import status
from .serializers import TeamApplicationDetailSerializer
# or whatever function you use to decode JWT manually

class TeamApplicationDetailView(APIView):
    def get(self, request, pk):
        # Step 1: Get the team application
        try:
            app = TeamApplication.objects.get(id=pk)
        except TeamApplication.DoesNotExist:
            return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

        # Step 2: Extract user ID (optional, in case you still need it later)
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split(" ")[1] if " " in auth_header else None

        try:
            user_id = verify_user(token) if token else None
        except (AuthenticationFailed, ValueError, TypeError):
            user_id = None

        # Step 3: Build user + skill maps
        all_user_ids = set([app.leader_user_id] + app.member_user_ids)
        skill_ids = app.skills

        user_map = {
            user.id: user for user in CustomUser.objects.filter(id__in=all_user_ids)
        }
        skill_map = {
            skill.id: skill.skill for skill in Skill.objects.filter(id__in=skill_ids)
        }

        # Step 4: Serialize with context (no join requests)
        serializer = TeamApplicationDetailSerializer(
            app,
            context={
                "request": request,
                "user_map": user_map,
                "skill_map": skill_map,
            },
        )
        return Response(serializer.data, status=status.HTTP_200_OK)




from django.db.models import Q

class UserTeamsView(APIView):
    def get(self, request):
        try:
            token = request.headers.get('Authorization', '').split(' ')[1]
            user_id = verify_user(token)
        except IndexError:
            return Response({"error": "Authorization header is missing or invalid"}, status=401)
        except AuthenticationFailed as e:
            return Response({"error": str(e)}, status=401)


        # Fetch all relevant teams
        teams = TeamApplication.objects.filter(
            Q(leader_user_id=user_id) |
            Q(member_user_ids__contains=[user_id])
        )

        # Fetch all needed user and skill data for enrichment
        all_user_ids = set()
        all_skill_ids = set()
        for team in teams:
            all_user_ids.add(team.leader_user_id)
            all_user_ids.update(team.member_user_ids)
            all_skill_ids.update(team.skills)

        user_map = {user.id: user for user in CustomUser.objects.filter(id__in=all_user_ids)}
        skill_map = {skill.id: skill.skill for skill in Skill.objects.filter(id__in=all_skill_ids)}

        # Map of team IDs that user has sent join requests to (optional if not needed here)
        user_join_requests = set()

        serializer = TeamApplicationListSerializer(
            teams,
            many=True,
            context={
                "current_user_id": user_id,
                "user_map": user_map,
                "skill_map": skill_map,
                "user_join_requests_map": user_join_requests,
            }
        )
        return Response(serializer.data)