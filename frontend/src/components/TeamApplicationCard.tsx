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

const TeamApplicationCard = ({
	app,
	onRequest,
}: {
	app: any;
	onRequest: () => void;
}) => {
	const role = app.user_role || "default";

	return (
		<div
			className={`block bg-white p-5 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 border-l-4 ${getRoleBorderStyle(
				role
			)}`}>
			<div className="flex justify-between items-start">
				<div>
					<h3 className="text-lg font-bold text-slate-800">{app.team_name}</h3>
					<p className="text-sm text-slate-500">Leader: {app.leader_name}</p>
				</div>
				{getRoleBadge(role)}
			</div>
			<p className="mt-3 text-sm text-slate-600">{app.description}</p>
			<div className="flex flex-wrap mt-3 gap-2">
				{app.skill_names.map((skill: any) => (
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
					<span className="font-bold text-blue-600">{app.capacity_left}</span>
				</p>
				{role === "default" && (
					<button
						onClick={onRequest}
						className="px-4 py-2 text-sm bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600">
						Request to Join
					</button>
				)}
			</div>
		</div>
	);
};

export default TeamApplicationCard;
