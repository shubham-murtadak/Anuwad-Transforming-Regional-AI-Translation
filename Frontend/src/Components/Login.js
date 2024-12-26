import React, { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";
import './Auth.css';  // Ensure unique classes are applied

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      await signInWithEmailAndPassword(auth, email, password);
      navigate("/app");
    } catch (err) {
      setError("Invalid credentials");
    }
  };

  const handleSignUp = () => {
    navigate("/signup");
  };

  return (
    <>
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <img
            src="https://images.unsplash.com/photo-1485827404703-89b55fcc595e?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1770&q=80"
            alt="Anuwad Logo"
            className="navbar-icon"
          />
          <span>Anuwad</span>
        </div>
        <div className="navbar-links">
          <a href="#about">About</a>
          <a href="#contactus">Contact Us</a>
          <a href="login">Logout</a>
        </div>
      </nav>
      
      {/* Login Form */}
      <div className="auth-wrapper">
        <div className="auth-auth-container">
          <h2>Login</h2>
          <form onSubmit={handleLogin}>
            <input
              type="email"
              className="auth-auth-input"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              type="password"
              className="auth-auth-input"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && <p className="auth-error">{error}</p>}
            <button type="submit" className="auth-auth-button">Login</button>
          </form>
          <button onClick={handleSignUp} className="auth-signup-button">Sign Up</button>
        </div>
      </div>
        {/* Footer */}
        <footer className="footer">
        <p>&copy; 2024 Anuwad - Multilingual Translation System</p>
      </footer>
    
    </>
  );
};

export default Login;
