import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuthContext } from "../context/AuthContext";

const Register = () => {
	const navigate = useNavigate();
	const { login } = useAuthContext();

	const [email, setEmail] = useState("");
	const [fullName, setFullName] = useState("");
	const [password, setPassword] = useState("");
	const [profileImageFile, setProfileImageFile] = useState<File | null>(null);
	const [previewUrl, setPreviewUrl] = useState<string | null>(null);
	const [error, setError] = useState("");

	const [skillInput, setSkillInput] = useState("");
	const [skillList, setSkillList] = useState<string[]>([]);

	const handleSkillKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
		if (e.key === "Enter" && skillInput.trim()) {
			e.preventDefault();
			if (!skillList.includes(skillInput.trim())) {
				setSkillList([...skillList, skillInput.trim()]);
			}
			setSkillInput("");
		}
	};

	const removeSkill = (skillToRemove: string) => {
		setSkillList(skillList.filter((skill) => skill !== skillToRemove));
	};

	const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const file = e.target.files?.[0];
		if (file) {
			setProfileImageFile(file);
			setPreviewUrl(URL.createObjectURL(file));
		}
	};

	const handleRegister = async (e: React.FormEvent) => {
		e.preventDefault();
		setError("");

		const formData = new FormData();
		formData.append("email", email);
		formData.append("password", password);
		formData.append("full_name", fullName);
		if (profileImageFile) {
			formData.append("profile_image", profileImageFile);
		}
		skillList.forEach((skill) => {
			formData.append("skills", skill);
		});

		try {
			const response = await axios.post(
				"http://localhost:8001/api/register/",
				formData,
				{
					headers: { "Content-Type": "multipart/form-data" },
				}
			);

			const { token, user } = response.data;
			login(user, token);
			localStorage.setItem("token", token);
			localStorage.setItem("user", JSON.stringify(user));
			navigate("/dashboard");
		} catch (err) {
			setError("Registration failed. Please try again.");
		}
	};

	return (
		<div className="flex items-center justify-center min-h-screen bg-slate-50 py-12">
			<form
				onSubmit={handleRegister}
				className="bg-white p-8 rounded-2xl shadow-lg border border-slate-200 w-full max-w-md space-y-6"
				encType="multipart/form-data">
				<h2 className="text-3xl font-bold text-center text-slate-800">
					Create Account
				</h2>

				{error && (
					<div className="bg-red-50 text-red-700 text-sm font-medium p-3 rounded-lg text-center">
						{error}
					</div>
				)}

				<div className="space-y-2">
					<label className="block text-sm font-medium text-slate-700">
						Full Name
					</label>
					<input
						type="text"
						required
						value={fullName}
						onChange={(e) => setFullName(e.target.value)}
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
					/>
				</div>

				<div className="space-y-2">
					<label className="block text-sm font-medium text-slate-700">
						Email
					</label>
					<input
						type="email"
						required
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
					/>
				</div>

				<div className="space-y-2">
					<label className="block text-sm font-medium text-slate-700">
						Password
					</label>
					<input
						type="password"
						required
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
					/>
				</div>

				<div className="space-y-2">
					<label className="block text-sm font-medium text-slate-700">
						Skills
					</label>
					<input
						type="text"
						placeholder="Type a skill and press Enter"
						value={skillInput}
						onChange={(e) => setSkillInput(e.target.value)}
						onKeyDown={handleSkillKeyDown}
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
					/>
					<div className="flex flex-wrap pt-2 gap-2">
						{skillList.map((skill, idx) => (
							<span
								key={idx}
								className="bg-blue-100 text-blue-800 text-xs font-medium inline-flex items-center px-2.5 py-1 rounded-full">
								{skill}
								<button
									type="button"
									onClick={() => removeSkill(skill)}
									className="inline-flex items-center p-0.5 ml-2 text-sm text-blue-400 bg-transparent rounded-full hover:bg-blue-200 hover:text-blue-900">
									&times;
								</button>
							</span>
						))}
					</div>
				</div>

				<div className="space-y-2">
					<label className="block text-sm font-medium text-slate-700">
						Profile Image
					</label>
					<div className="flex items-center gap-4">
						{previewUrl ? (
							<img
								src={previewUrl}
								alt="Preview"
								className="h-16 w-16 object-cover rounded-full border-2 border-slate-200 p-1"
							/>
						) : (
							<div className="h-16 w-16 bg-slate-100 rounded-full" />
						)}
						<input
							type="file"
							accept="image/*"
							onChange={handleImageChange}
							className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
						/>
					</div>
				</div>

				<button
					type="submit"
					className="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-3 text-center transition-colors">
					Sign Up
				</button>
			</form>
		</div>
	);
};

export default Register;
