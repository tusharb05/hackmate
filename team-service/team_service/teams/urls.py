from django.urls import path
from .views import FetchSkillsView, FetchUserView, UpdateJoinRequestStatusView, CreateTeamApplicationView, ListTeamApplicationsView, CreateTeamJoinRequestView, ListTeamJoinRequestsView

urlpatterns = [
    path('create-team-application/', CreateTeamApplicationView.as_view(), name='create-team'),
    path('team-applications/', ListTeamApplicationsView.as_view(), name='list-team-applications'),
    path('join-request/', CreateTeamJoinRequestView.as_view(), name='create-team-join-request'),
    path('join-requests/<int:team_id>/', ListTeamJoinRequestsView.as_view(), name='list-team-join-requests'),
    path('join-requests/<int:request_id>/status/', UpdateJoinRequestStatusView.as_view(), name='update-join-request-status'),
    path('fetch-users/', FetchUserView.as_view(), name='get-users'),
    path('fetch-skills/', FetchSkillsView.as_view(), name='get-skills'),
]