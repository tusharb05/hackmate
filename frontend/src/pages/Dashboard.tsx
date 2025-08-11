import { useEffect, useState } from "react";
import { useAuthContext } from "../context/AuthContext";
import axios from "axios";
import RequestModal from "../components/RequestModal";
import CreateTeamModal from "../components/CreateTeamModal";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
	const { user, token } = useAuthContext();
	const [applications, setApplications] = useState<any[]>([]);
	const [notifications, setNotifications] = useState<any[]>([]);
	const [showModal, setShowModal] = useState(false);
	const [selectedApp, setSelectedApp] = useState<any | null>(null);
	const [message, setMessage] = useState("");
	const [showCreateModal, setShowCreateModal] = useState(false);

	const navigate = useNavigate();

	const fetchApplications = async () => {
		try {
			const res = await axios.get(
				"http://localhost:8002/api/team-applications/",
				{
					headers: token ? { Authorization: `Bearer ${token}` } : undefined,
				}
			);
			setApplications(res.data);
		} catch (error) {
			console.error("Failed to fetch applications:", error);
		}
	};

	const fetchNotifications = async () => {
		if (!user || !token) return;
		try {
			const res = await axios.get("http://localhost:8003/api/notifications/", {
				headers: { Authorization: `Bearer ${token}` },
			});
			setNotifications(res.data);
			console.log(res.data);
		} catch (error) {
			console.error("Failed to fetch notifications:", error);
		}
	};

	const handleJoinRequest = async () => {
		if (!selectedApp || !token) return;
		try {
			await axios.post(
				"http://localhost:8002/api/join-request/",
				{ team_application: selectedApp.id, message },
				{ headers: { Authorization: `Bearer ${token}` } }
			);
			setShowModal(false);
			setMessage("");
			fetchApplications();
		} catch (error) {
			console.error("Failed to send join request:", error);
		}
	};

	useEffect(() => {
		fetchApplications();
		if (user) {
			fetchNotifications();
		}
	}, [user]);

	const getRoleBorderStyle = (role: string) => {
		switch (role) {
			case "owner":
				return "border-yellow-400";
			case "member":
				return "border-green-500";
			case "pending":
				return "border-blue-500";
			default:
				return "border-transparent";
		}
	};

	const getRoleBadge = (role: string) => {
		const styles: { [key: string]: string } = {
			owner: "bg-yellow-100 text-yellow-800",
			member: "bg-green-100 text-green-800",
			pending: "bg-blue-100 text-blue-800",
		};
		const labels: { [key: string]: string } = {
			owner: "You Own This Team",
			member: "You're a Member",
			pending: "Request Pending",
		};
		if (!labels[role]) return null;
		return (
			<span
				className={`text-xs font-semibold px-2.5 py-1 rounded-md ${styles[role]}`}>
				{labels[role]}
			</span>
		);
	};

	return (
		<div className="bg-slate-50 min-h-screen">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
				<div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
					{/* Main Content */}
					<main className="lg:col-span-2 space-y-6">
						<div className="flex justify-between items-center">
							<h1 className="text-2xl font-bold text-slate-800">Find a Team</h1>
							{user && (
								<button
									onClick={() => setShowCreateModal(true)}
									className="px-4 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2">
									Create Team
								</button>
							)}
						</div>
						<div className="space-y-4">
							{applications.map((app) => (
								<Link
									to={`/team/${app.id}`}
									key={app.id}
									className={`block bg-white p-5 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 border-l-4 ${getRoleBorderStyle(
										app.user_role
									)}`}>
									<div className="flex justify-between items-start">
										<div>
											<h3 className="text-lg font-bold text-slate-800">
												{app.team_name}
											</h3>
											<p className="text-sm text-slate-500">
												Leader: {app.leader_name}
											</p>
										</div>
										{getRoleBadge(app.user_role)}
									</div>
									<p className="mt-3 text-sm text-slate-600">
										{app.description}
									</p>
									<div className="flex flex-wrap mt-3 gap-2">
										{app.skill_names.map((skill: string) => (
											<span
												key={skill}
												className="text-xs bg-slate-100 text-slate-700 font-medium px-2 py-1 rounded-md">
												{skill}
											</span>
										))}
									</div>
									<div className="flex justify-between items-center mt-4">
										<p className="text-sm font-medium text-slate-700">
											Capacity Left:{" "}
											<span className="font-bold text-blue-600">
												{app.capacity_left}
											</span>
										</p>
										{app.user_role === "default" && (
											<button
												onClick={(e) => {
													e.preventDefault();
													setSelectedApp(app);
													setShowModal(true);
												}}
												className="px-4 py-2 text-sm bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600">
												Request to Join
											</button>
										)}
									</div>
								</Link>
							))}
						</div>
					</main>

					{/* Notification Panel */}
					<aside className="space-y-6">
						<div className="bg-white rounded-xl shadow-sm p-5">
							<div className="flex justify-between items-center mb-4">
								<h3 className="text-lg font-bold text-slate-800">
									Notifications
								</h3>
								<button
									onClick={fetchNotifications}
									className="text-sm font-semibold text-blue-600 hover:underline">
									Refresh
								</button>
							</div>
							{!user ? (
								<p className="text-slate-500 text-sm">
									Please log in to see your notifications.
								</p>
							) : (
								<ul className="space-y-3 max-h-96 overflow-y-auto">
									{notifications.length > 0 ? (
										notifications.map((notif: any) => (
											<li
												key={notif.id}
												onClick={() =>
													navigate(`/team/${notif.team_application_id}`)
												}
												className="flex gap-3 items-start p-2 rounded-lg hover:bg-slate-50 cursor-pointer">
												<div>
													<p className="text-sm text-slate-700">
														{notif.message}
													</p>
													<p className="text-xs text-slate-400 mt-1">
														{new Date(notif.created_at).toLocaleString()}
													</p>
												</div>
											</li>
										))
									) : (
										<p className="text-slate-500 text-sm text-center py-4">
											No new notifications.
										</p>
									)}
								</ul>
							)}
						</div>
					</aside>
				</div>
			</div>

			{showModal && selectedApp && (
				<RequestModal
					teamName={selectedApp.team_name}
					message={message}
					setMessage={setMessage}
					onClose={() => setShowModal(false)}
					onSend={handleJoinRequest}
				/>
			)}
			{showCreateModal && (
				<CreateTeamModal
					token={token || ""}
					onClose={() => setShowCreateModal(false)}
					onSuccess={() => {
						fetchApplications();
						setShowCreateModal(false);
					}}
				/>
			)}
		</div>
	);
};

export default Dashboard;
