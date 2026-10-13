import { useState } from "react";

export default function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    // Replace with actual backend API logic
    onLogin(email);
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#0d1117] px-4">
      <div className="bg-white/[10%] backdrop-blur-lg p-8 rounded-xl w-full max-w-md shadow-lg transform transition-transform hover:scale-[1.02]">
        <h1 className="text-3xl font-bold text-center text-white mb-6">
          {isLogin ? "Welcome Back" : "Create Your Pulse Account"}
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-3 rounded-md bg-white/[20%] placeholder-white/[70%] text-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
              required
            />
          )}
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 rounded-md bg-white/[20%] placeholder-white/[70%] text-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-md bg-white/[20%] placeholder-white/[70%] text-white focus:outline-none focus:ring-2 focus:ring-indigo-400"
            required
          />
          <button
            type="submit"
            className="w-full py-3 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-md font-semibold text-white hover:opacity-90 transition"
          >
            {isLogin ? "Login" : "Sign Up"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-white/[70%]">
          {isLogin ? "New here?" : "Already have an account?"}{" "}
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="font-bold text-indigo-300 hover:underline"
          >
            {isLogin ? "Create account" : "Login"}
          </button>
        </p>
      </div>
    </div>
  );
}
