import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Navbar from "./components/Navbar";
import { AuthProvider } from "./context/AuthContext";
import TeamDetail from "./pages/TeamDetail";

const App = () => {
	return (
		<>
			<AuthProvider>
				<Navbar />
				<Routes>
					<Route path="/dashboard" element={<Dashboard />} />
					<Route path="/team/:teamId" element={<TeamDetail />} /> {/* ✅ */}
					<Route path="/login" element={<Login />} />
					<Route path="/register" element={<Register />} />
				</Routes>
			</AuthProvider>
		</>
	);
};

export default App;
