const USER_SERVICE_BASE = import.meta.env.VITE_USER_SERVICE_BASE;
const TEAM_SERVICE_BASE = import.meta.env.VITE_TEAM_SERVICE_BASE;
const NOTIFICATION_SERVICE_BASE = import.meta.env
	.VITE_NOTIFICATION_SERVICE_BASE;

export const FETCH_TEAM_APPLICATIONS = `${TEAM_SERVICE_BASE}/team-applications/`;
export const FETCH_NOTIFICATIONS = `${NOTIFICATION_SERVICE_BASE}/notifications/`;
export const CREATE_JOIN_REQUEST = `${TEAM_SERVICE_BASE}/join-request/`;
export const LOGIN_URL = `${USER_SERVICE_BASE}/login/`;
export const FETCH_MY_TEAMS = `${TEAM_SERVICE_BASE}/user/teams/`;
export const REGISTER_URL = `${USER_SERVICE_BASE}/register/`;
export const FETCH_TEAM_DETAIL = `${TEAM_SERVICE_BASE}/team/`;
export const FETCH_JOIN_REQUESTS = `${TEAM_SERVICE_BASE}/join-requests/`;
export const APPROVE_REJECT_URL = "";
export const FETCH_USER_DETAILS = `${USER_SERVICE_BASE}/users/`;
export const CREATE_TEAM_APPLICATION = `${TEAM_SERVICE_BASE}/create-team-application/`;
