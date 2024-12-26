import React, { useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from "firebase/auth";
import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";
import './Auth.css';  // Ensure unique classes are applied

const Signup = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      // Create a new user
      await createUserWithEmailAndPassword(auth, email, password);

      // Automatically log the user in after successful sign-up
      await signInWithEmailAndPassword(auth, email, password);

      // Navigate to the app or dashboard
      navigate("/app");
    } catch (err) {
      // Provide detailed error feedback
      setError(err.message || "Error creating account");
    }
  };

  const handleLogin = () => {
    // Navigate to the Login page
    navigate("/login");
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
      
      {/* Sign Up Form */}
      <div className="auth-wrapper">
        <div className="auth-auth-container">
          <h2>Sign Up</h2>
          <form onSubmit={handleSignUp}>
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
            <button type="submit" className="auth-auth-button">Sign Up</button>
          </form>
          <button onClick={handleLogin} className="auth-signup-button">Login</button>
        </div>
      </div>
        {/* Footer */}
        <footer className="footer">
        <p>&copy; 2024 Anuwad - Multilingual Translation System</p>
      </footer>
    
    </>
  );
};

export default Signup;
