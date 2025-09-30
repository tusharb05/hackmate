import { Link, useNavigate } from "react-router-dom";
import { useAuthContext } from "../context/AuthContext";

const Navbar = () => {
	const { user, logout } = useAuthContext();
	const navigate = useNavigate();

	const handleLogout = () => {
		logout();
		navigate("/login");
	};

	return (
		<nav className="sticky top-0 z-40 w-full bg-white/80 backdrop-blur-md border-b border-slate-200">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="flex items-center justify-between h-16">
					{/* Left - Logo */}
					<div className="flex-shrink-0">
						<Link to="/dashboard" className="text-2xl font-bold text-slate-800">
							HackMate
						</Link>
					</div>



					{/* Right - User Info / Auth Buttons */}
					<div className="flex items-center space-x-4">
						{user ? (
							<>
								<span className="text-slate-700 font-medium hidden sm:block">
									{user.full_name}
								</span>
								{user.profile_image && (
									<Link to={`/user/${user.id}`}>
										<img
											src={user.profile_image}
											alt="Profile"
											className="w-10 h-10 rounded-full object-cover border-2 border-slate-200 hover:ring-2 hover:ring-slate-400 transition"
										/>
									</Link>
								)}

								<button
									onClick={handleLogout}
									className="px-4 py-2 text-sm font-semibold text-red-600 bg-red-100 rounded-lg hover:bg-red-200 transition-colors">
									Logout
								</button>
							</>
						) : (
							<>
								<Link
									to="/login"
									className="px-4 py-2 text-sm font-semibold text-slate-700 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors">
									Sign In
								</Link>
								<Link
									to="/register"
									className="px-4 py-2 text-sm font-semibold text-white bg-slate-800 rounded-lg hover:bg-slate-900 transition-colors">
									Sign Up
								</Link>
							</>
						)}
					</div>
				</div>
			</div>
		</nav>
	);
};

export default Navbar;
