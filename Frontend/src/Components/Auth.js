import React, { useState } from 'react';
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import './Auth.css';

const Auth = ({ setUser }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const auth = getAuth();

  const handleAuth = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
      } else {
        await createUserWithEmailAndPassword(auth, email, password);
      }
      setUser(auth.currentUser);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-auth-container">
        <h2>{isLogin ? 'Login to Your Account' : 'Create an Account'}</h2>
        <form onSubmit={handleAuth}>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              className="auth-auth-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              className="auth-auth-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          <button type="submit" className="auth-auth-button" disabled={loading}>
            {loading ? 'Processing...' : isLogin ? 'Login' : 'Sign Up'}
          </button>
        </form>
        {error && <p className="error-message">{error}</p>}
        <p className="toggle-auth">
          {isLogin ? "Don't have an account?" : 'Already have an account?'}
          <button className="toggle-button" onClick={() => setIsLogin(!isLogin)}>
            {isLogin ? ' Sign Up' : ' Login'}
          </button>
        </p>
      </div>
    </div>
  );
};

export default Auth;
