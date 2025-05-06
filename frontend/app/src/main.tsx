import { StrictMode } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import * as ReactDOM from "react-dom/client";
import { App } from "./pages/app";
import Register from "./components/Auth/Register";
import ForgotPassword from "./components/Auth/ForgotPassword";
import Login from "./components/home/Login";
import Dashboard from "./pages/dashboard";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/register" element={<Register />}></Route>
        <Route path="/forgot-password" element={<ForgotPassword />}></Route>
        <Route path="/login" element={<Login />}></Route>
        <Route path="/dashboard" element={<Dashboard />}></Route>
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
