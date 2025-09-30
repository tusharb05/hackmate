import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import { FETCH_USER_DETAILS } from "../urls";

const UserDetail = () => {
	const { userId } = useParams();
	const [user, setUser] = useState<any>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState("");

	useEffect(() => {
		const fetchUser = async () => {
			try {
				const res = await axios.get(
					// `http://localhost:8001/api/users/${userId}/`
					`${FETCH_USER_DETAILS}${userId}/`
				);
				console.log(res);
				setUser(res.data);
			} catch (err) {
				setError("Failed to fetch user details");
			} finally {
				setLoading(false);
			}
		};

		if (userId) fetchUser();
	}, [userId]);

	if (loading) return <p className="text-gray-500">Loading user...</p>;
	if (error) return <p className="text-red-500">{error}</p>;

	return (
		<div className="max-w-xl mx-auto p-4 bg-white rounded shadow">
			<h2 className="text-xl font-semibold mb-4">User Profile</h2>
			<div className="flex items-center gap-4 mb-4">
				{user.profile_image && (
					<img
						src={user.profile_image}
						alt={user.full_name}
						className="w-20 h-20 rounded-full object-cover border"
					/>
				)}
				<div>
					<p className="text-lg font-medium">{user.full_name}</p>
					<p className="text-sm text-gray-600">{user.email}</p>
				</div>
			</div>
			<div>
				<h3 className="font-semibold text-sm text-gray-700 mb-2">
					Skills:
				</h3>
				<ul className="list-disc list-inside text-sm text-gray-600">
					{user.skills.map((skill: any) => (
						<li key={skill.id}>{skill.skill}</li>
					))}
				</ul>
			</div>
		</div>
	);
};

export default UserDetail;
