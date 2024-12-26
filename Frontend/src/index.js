// import { StrictMode } from "react";
// import ReactDOM from "react-dom";

// import App from "./App";

// const rootElement = document.getElementById("root");
// ReactDOM.render(
//   <StrictMode>
//     <App />
//   </StrictMode>,
//   rootElement
// );
// src/index.js


import React from "react";
import ReactDOM from "react-dom/client";
// import "./index.css";
import { BrowserRouter as Router } from "react-router-dom";
import App from "./App";
import { Routes, Route } from "react-router-dom";
import Login from "./Components/Login";
import Signup from "./Components/Signup";
import Auth from "./Components/Auth";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <Router>
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route path="/app" element={<App />} />{" "}
      {/* App.js is your main content */}
    </Routes>
  </Router>
);
