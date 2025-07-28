import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useAuthContext } from "../context/AuthContext";

const Login = () => {
	const navigate = useNavigate();
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [error, setError] = useState("");

	const { login } = useAuthContext();

	const handleLogin = async (e: React.FormEvent) => {
		e.preventDefault();
		setError("");

		try {
			const res = await axios.post("http://localhost:8001/api/login/", {
				email,
				password,
			});

			const { token, user } = res.data;
			login(user, token);
			localStorage.setItem("token", token);
			localStorage.setItem("user", JSON.stringify(user));

			navigate("/dashboard");
		} catch (err: any) {
			setError("Invalid email or password");
		}
	};

	return (
		<div className="flex items-center justify-center min-h-screen bg-slate-50">
			<form
				onSubmit={handleLogin}
				className="bg-white p-8 rounded-2xl shadow-lg border border-slate-200 w-full max-w-md space-y-6">
				<h2 className="text-3xl font-bold text-center text-slate-800">
					Sign In
				</h2>

				{error && (
					<div className="bg-red-50 text-red-700 text-sm font-medium p-3 rounded-lg text-center">
						{error}
					</div>
				)}

				<div className="space-y-2">
					<label
						htmlFor="email"
						className="block text-sm font-medium text-slate-700">
						Email
					</label>
					<input
						id="email"
						type="email"
						required
						value={email}
						onChange={(e) => setEmail(e.target.value)}
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
					/>
				</div>

				<div className="space-y-2">
					<label
						htmlFor="password"
						className="block text-sm font-medium text-slate-700">
						Password
					</label>
					<input
						id="password"
						type="password"
						required
						value={password}
						onChange={(e) => setPassword(e.target.value)}
						className="bg-slate-50 border border-slate-300 text-slate-900 text-sm rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
					/>
				</div>

				<button
					type="submit"
					className="w-full text-white bg-blue-600 hover:bg-blue-700 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-3 text-center transition-colors">
					Sign In
				</button>
			</form>
		</div>
	);
};

export default Login;
