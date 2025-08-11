import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const TeamDetail = () => {
	const navigate = useNavigate();
	const { teamId } = useParams();
	const { user, token } = useAuthContext();
	const [team, setTeam] = useState<any>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [joinRequests, setJoinRequests] = useState<any[]>([]);

	const fetchTeamData = async () => {
		if (!teamId) return;
		try {
			setLoading(true);
			const res = await fetch(`http://localhost:8002/api/team/${teamId}/`);
			if (!res.ok) throw new Error("Failed to fetch team details");
			const data = await res.json();
			setTeam(data);

			// If the logged-in user is the leader, fetch join requests
			if (user && token && parseInt(data.leader.id) === parseInt(user.id)) {
				fetchJoinRequests(data.id);
			}
		} catch (err: any) {
			setError(err.message);
		} finally {
			setLoading(false);
		}
	};

	const fetchJoinRequests = async (id: string) => {
		try {
			const res = await fetch(
				`http://localhost:8002/api/join-requests/${id}/`,
				{
					headers: { Authorization: `Bearer ${token}` },
				}
			);
			if (!res.ok) throw new Error("Failed to fetch join requests");
			const data = await res.json();
			setJoinRequests(data);
		} catch (err: any) {
			console.error("Join request fetch error:", err.message);
		}
	};

	const handleStatusChange = async (
		requestId: number,
		status: "accepted" | "rejected"
	) => {
		try {
			const res = await fetch(
				`http://localhost:8002/api/join-requests/${requestId}/status/`,
				{
					method: "PATCH",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
					body: JSON.stringify({ status }),
				}
			);
			if (!res.ok) throw new Error("Failed to update status");
			// Refresh data instead of full page reload for a better UX
			fetchTeamData();
		} catch (err: any) {
			console.error("Status update error:", err.message);
		}
	};

	useEffect(() => {
		fetchTeamData();
	}, [teamId, user, token]);

	if (loading)
		return (
			<div className="flex justify-center items-center h-screen bg-slate-50">
				<p className="text-lg font-semibold text-slate-600">Loading...</p>
			</div>
		);
	if (error)
		return (
			<div className="p-6 text-center text-red-500 bg-red-50 rounded-lg max-w-md mx-auto mt-10">
				Error: {error}
			</div>
		);
	if (!team) return null;

	const isLeader =
		user && token && parseInt(team.leader.id) === parseInt(user.id);

	return (
		<div className="bg-slate-50 min-h-screen">
			<div className="max-w-4xl mx-auto p-4 md:p-8 space-y-8">
				{/* Header */}
				<div className="bg-white p-6 rounded-2xl shadow-md border border-slate-200">
					<h1 className="text-3xl md:text-4xl font-extrabold text-slate-900 tracking-tight">
						{team.title}
					</h1>
					<p className="mt-2 text-lg text-slate-600">
						Team: <strong>{team.team_name}</strong>
					</p>
					<div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6 text-sm">
						<InfoPill label="Status" value={team.status} />
						<InfoPill label="Hackathon Date" value={team.hackathon_date} />
						<InfoPill
							label="Capacity"
							value={`${team.members.length}/${team.capacity}`}
						/>
					</div>
				</div>

				{/* Sections */}
				<div className="space-y-8">
					<TeamSection title="Team Leader">
						<UserCard
							user={team.leader}
							onClick={() => navigate(`/user/${team.leader.id}`)}
						/>
					</TeamSection>

					<TeamSection title="Team Members">
						{team.members.length > 0 ? (
							<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
								{team.members.map((member: any) => (
									<UserCard
										key={member.id}
										user={member}
										onClick={() => navigate(`/user/${member.id}`)}
									/>
								))}
							</div>
						) : (
							<p className="text-slate-500 text-sm">No members yet.</p>
						)}
					</TeamSection>

					<TeamSection title="Required Skills">
						<div className="flex flex-wrap gap-2">
							{team.skill_names.map((skill: string, idx: number) => (
								<span
									key={idx}
									className="bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1.5 rounded-full">
									{skill}
								</span>
							))}
						</div>
					</TeamSection>

					{isLeader && joinRequests.length > 0 && (
						<TeamSection title="Join Requests">
							<div className="space-y-4">
								{joinRequests.map((req: any) => (
									<JoinRequestCard
										key={req.id}
										request={req}
										onStatusChange={handleStatusChange}
									/>
								))}
							</div>
						</TeamSection>
					)}
				</div>
			</div>
		</div>
	);
};

// Sub-components for cleaner structure
const TeamSection = ({
	title,
	children,
}: {
	title: string;
	children: React.ReactNode;
}) => (
	<div>
		<h2 className="text-2xl font-bold text-slate-800 mb-4">{title}</h2>
		{children}
	</div>
);

const UserCard = ({ user, onClick }: { user: any; onClick?: () => void }) => (
	<div
		className="bg-white border border-slate-200 p-4 rounded-xl shadow-sm flex items-center gap-4 hover:shadow-md transition-shadow cursor-pointer"
		onClick={onClick}>
		<img
			src={user.profile_image || "https://via.placeholder.com/80"}
			alt={user.full_name}
			className="w-14 h-14 rounded-full object-cover border-2 border-white ring-2 ring-slate-200"
		/>
		<div>
			<p className="font-bold text-slate-800">{user.full_name}</p>
			<p className="text-sm text-slate-500">{user.email}</p>
		</div>
	</div>
);


const JoinRequestCard = ({
	request,
	onStatusChange,
}: {
	request: any;
	onStatusChange: Function;
}) => (
	<div className="bg-white p-5 border border-slate-200 rounded-xl shadow-sm">
		<div className="flex flex-col sm:flex-row items-start justify-between gap-4">
			<div className="flex gap-4">
				<img
					src={
						request.user_details.profile_image ||
						"https://via.placeholder.com/80"
					}
					alt={request.user_details.full_name}
					className="w-12 h-12 rounded-full object-cover"
				/>
				<div>
					<p className="font-bold text-slate-800">
						{request.user_details.full_name}
					</p>
					<p className="text-sm text-slate-500">{request.user_details.email}</p>
					<p className="mt-2 text-sm bg-slate-50 p-2 rounded-md">
						"{request.message}"
					</p>
					<div className="mt-2 flex gap-2 flex-wrap">
						{request.user_details.skills.map((skill: string, idx: number) => (
							<span
								key={idx}
								className="text-xs bg-slate-200 text-slate-700 font-medium px-2 py-1 rounded-md">
								{skill}
							</span>
						))}
					</div>
				</div>
			</div>
			<div className="flex-shrink-0 w-full sm:w-auto">
				{request.status === "pending" ? (
					<div className="flex gap-2 justify-end">
						<button
							onClick={() => onStatusChange(request.id, "accepted")}
							className="px-3 py-1.5 text-sm font-semibold bg-green-100 text-green-700 rounded-lg hover:bg-green-200">
							Accept
						</button>
						<button
							onClick={() => onStatusChange(request.id, "rejected")}
							className="px-3 py-1.5 text-sm font-semibold bg-red-100 text-red-700 rounded-lg hover:bg-red-200">
							Reject
						</button>
					</div>
				) : (
					<span
						className={`px-3 py-1.5 text-sm font-semibold rounded-lg ${
							request.status === "accepted"
								? "bg-green-100 text-green-700"
								: "bg-red-100 text-red-700"
						}`}>
						{request.status.charAt(0).toUpperCase() + request.status.slice(1)}
					</span>
				)}
			</div>
		</div>
	</div>
);

const InfoPill = ({ label, value }: { label: string; value: string }) => (
	<div className="bg-slate-50 p-3 rounded-lg">
		<p className="text-xs text-slate-500 font-medium uppercase tracking-wider">
			{label}
		</p>
		<p className="font-bold text-slate-800 capitalize">{value}</p>
	</div>
);

export default TeamDetail;
