import React, { useEffect, useState } from "react";
import { useAuthContext } from "../context/AuthContext";
import { Link } from "react-router-dom";
import { FETCH_MY_TEAMS } from "../urls";

const MyTeams = () => {
	const { token } = useAuthContext();
	const [teams, setTeams] = useState<any[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchTeams = async () => {
			try {
				const res = await fetch(
					// "http://localhost:8002/api/user/teams/",
					FETCH_MY_TEAMS,
					{
						headers: {
							Authorization: `Bearer ${token}`,
						},
					}
				);
				if (!res.ok) throw new Error("Failed to fetch teams");
				const data = await res.json();
				setTeams(data);
			} catch (err: any) {
				setError(err.message);
			} finally {
				setLoading(false);
			}
		};

		if (token) fetchTeams();
	}, [token]);

	if (loading) return <div className="p-4">Loading...</div>;
	if (error) return <div className="p-4 text-red-600">Error: {error}</div>;
	if (teams.length === 0)
		return <div className="p-4">You’re not part of any teams yet.</div>;

	return (
		<div className="max-w-5xl mx-auto px-4 py-8">
			<h1 className="text-3xl font-bold text-slate-800 mb-6">My Teams</h1>
			<div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
				{teams.map((team) => (
					<Link
						key={team.id}
						to={`/team/${team.id}`}
						className="bg-white rounded-2xl shadow-md p-6 border border-slate-200 hover:shadow-lg transition hover:ring-2 hover:ring-blue-200 cursor-pointer block">
						<h2 className="text-xl font-semibold text-slate-800 mb-2">
							{team.team_name}
						</h2>
						<p className="text-slate-600 mb-2">
							{team.description}
						</p>
						<div className="text-sm text-slate-500 mb-1">
							<b>Status:</b> {team.status} &nbsp;|&nbsp;{" "}
							<b>Role:</b> {team.user_role}
						</div>
						<div className="text-sm text-slate-500 mb-1">
							<b>Leader:</b> {team.leader_name}
						</div>
						<div className="text-sm text-slate-500 mb-1">
							<b>Hackathon Date:</b>{" "}
							{new Date(team.hackathon_date).toDateString()}
						</div>
						<div className="text-sm text-slate-500 mb-1">
							<b>Capacity:</b> {team.capacity} total,{" "}
							{team.capacity_left} spots left
						</div>
						<div className="mt-3">
							<span className="text-sm font-medium text-slate-700">
								Skills:
							</span>
							<div className="flex flex-wrap mt-1 gap-2">
								{team.skill_names.map((skill: string) => (
									<span
										key={skill}
										className="bg-slate-100 text-slate-800 text-xs px-2 py-1 rounded-full">
										{skill}
									</span>
								))}
							</div>
						</div>
					</Link>
				))}
			</div>
		</div>
	);
};

export default MyTeams;
