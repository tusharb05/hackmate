import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Notification
from .serializers import NotificationSerializer
import os

# class GetNotificationsView(APIView):
#     def get(self, request):
#         token = request.headers.get("Authorization")
#         if not token:
#             return Response({"error": "Missing token"}, status=401)

#         # Verify user from user-service
#         try:
#             verify_response = requests.get("http://user-service:8000/api/verify-user/", headers={"Authorization": token})
#             data = verify_response.json()

#             if not data.get("valid"):
#                 return Response({"error": "Invalid user"}, status=401)

#             user_id = data["user_id"]
#         except Exception as e:
#             return Response({"error": "User verification failed", "detail": str(e)}, status=500)

#         notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')

#         enriched_notifications = []
#         for notif in notifications:
#             try:
#                 # Fetch team data from team-service
#                 team_res = requests.get(f"http://team-service:8000/api/teams/{notif.team_application_id}/meta/")
#                 team_data = team_res.json()
                
#                 enriched = {
#                     "id": notif.id,
#                     "user_id": notif.user_id,
#                     "message": notif.message,
#                     "type": notif.type,
#                     "team_application_id": notif.team_application_id,
#                     "is_read": notif.is_read,
#                     "created_at": notif.created_at,
#                     "team_name": team_data.get("team_name"),
#                     "leader_name": team_data.get("leader_name"),
#                     # "profile_image": team_data.get("profile_image")
#                 }
#                 enriched_notifications.append(enriched)
#             except Exception as e:
#                 print(f"Failed to fetch team data for notif {notif.id}: {e}")

#         return Response(NotificationSerializer(enriched_notifications, many=True).data)

class GetNotificationsView(APIView):
    def get(self, request):
        token = request.headers.get("Authorization")
        if not token:
            return Response({"error": "Missing token"}, status=401)

        # Get service URLs from env
        user_service_url = os.getenv("USER_SERVICE_URL", "http://user-service:8000")
        team_service_url = os.getenv("TEAM_SERVICE_URL", "http://team-service:8000")

        # Verify user from user-service
        try:
            verify_response = requests.get(
                f"{user_service_url}/api/verify-user/",
                headers={"Authorization": token}
            )
            data = verify_response.json()

            if not data.get("valid"):
                return Response({"error": "Invalid user"}, status=401)

            user_id = data["user_id"]
        except Exception as e:
            return Response({"error": "User verification failed", "detail": str(e)}, status=500)

        notifications = Notification.objects.filter(user_id=user_id).order_by('-created_at')

        enriched_notifications = []
        for notif in notifications:
            try:
                # Fetch team data from team-service
                team_res = requests.get(f"{team_service_url}/api/teams/{notif.team_application_id}/meta/")
                team_data = team_res.json()

                enriched = {
                    "id": notif.id,
                    "user_id": notif.user_id,
                    "message": notif.message,
                    "type": notif.type,
                    "team_application_id": notif.team_application_id,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at,
                    "team_name": team_data.get("team_name"),
                    "leader_name": team_data.get("leader_name"),
                }
                enriched_notifications.append(enriched)
            except Exception as e:
                print(f"Failed to fetch team data for notif {notif.id}: {e}")

        return Response(NotificationSerializer(enriched_notifications, many=True).data)