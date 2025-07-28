import { useState } from "react";
import axios from "axios";

interface Props {
	token: string;
	onClose: () => void;
	onSuccess: () => void;
}

const CreateTeamModal = ({ token, onClose, onSuccess }: Props) => {
	const [title, setTitle] = useState("");
	const [description, setDescription] = useState("");
	const [teamName, setTeamName] = useState("");
	const [capacity, setCapacity] = useState(5);
	const [date, setDate] = useState("");
	const [skillInput, setSkillInput] = useState("");
	const [skills, setSkills] = useState<string[]>([]);

	const addSkill = () => {
		if (skillInput.trim() && !skills.includes(skillInput.trim())) {
			setSkills([...skills, skillInput.trim()]);
		}
		setSkillInput("");
	};

	const removeSkill = (skill: string) => {
		setSkills(skills.filter((s) => s !== skill));
	};

	const handleSubmit = async () => {
		try {
			await axios.post(
				"http://localhost:8002/api/create-team-application/",
				{
					title,
					description,
					team_name: teamName,
					capacity,
					hackathon_date: date,
					skills,
				},
				{ headers: { Authorization: `Bearer ${token}` } }
			);
			onSuccess();
		} catch (err) {
			console.error("Error creating team:", err);
		}
	};

	return (
		<div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex justify-center items-center p-4">
			<div className="bg-white p-6 rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
				<h2 className="text-xl font-bold mb-6 text-slate-800">
					Create a New Team
				</h2>

				<div className="space-y-4">
					<input
						type="text"
						placeholder="Project Title"
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
						value={title}
						onChange={(e) => setTitle(e.target.value)}
					/>
					<textarea
						placeholder="Project Description"
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
						value={description}
						onChange={(e) => setDescription(e.target.value)}
						rows={3}
					/>
					<input
						type="text"
						placeholder="Team Name"
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
						value={teamName}
						onChange={(e) => setTeamName(e.target.value)}
					/>
					<div className="grid grid-cols-2 gap-4">
						<input
							type="number"
							placeholder="Team Capacity"
							className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
							value={capacity}
							onChange={(e) => setCapacity(parseInt(e.target.value))}
						/>
						<input
							type="date"
							className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
							value={date}
							onChange={(e) => setDate(e.target.value)}
						/>
					</div>
					<div>
						<div className="flex gap-2">
							<input
								type="text"
								placeholder="Add a required skill and press Enter"
								className="flex-1 bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
								value={skillInput}
								onChange={(e) => setSkillInput(e.target.value)}
								onKeyDown={(e) => e.key === "Enter" && addSkill()}
							/>
							<button
								onClick={addSkill}
								className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700">
								Add
							</button>
						</div>
						<div className="flex flex-wrap gap-2 mt-3">
							{skills.map((skill) => (
								<span
									key={skill}
									className="cursor-pointer bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-1 rounded-full"
									onClick={() => removeSkill(skill)}>
									{skill}
									<button
										type="button"
										className="inline-flex items-center p-0.5 ml-2 text-sm text-blue-400 bg-transparent rounded-full hover:bg-blue-200 hover:text-blue-900">
										&times;
									</button>
								</span>
							))}
						</div>
					</div>
				</div>

				<div className="flex justify-end gap-3 mt-8">
					<button
						onClick={onClose}
						className="px-5 py-2.5 text-sm font-medium text-gray-900 bg-white rounded-lg border border-gray-200 hover:bg-gray-100">
						Cancel
					</button>
					<button
						onClick={handleSubmit}
						className="px-5 py-2.5 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700">
						Create Team
					</button>
				</div>
			</div>
		</div>
	);
};

export default CreateTeamModal;
