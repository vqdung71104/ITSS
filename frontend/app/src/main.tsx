import { StrictMode } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import * as ReactDOM from "react-dom/client";
import { App } from "./pages/app";
import Register from "./components/Auth/Register";
import ForgotPassword from "./components/Auth/ForgotPassword";

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
      </Routes>
    </BrowserRouter>
  </StrictMode>
);
