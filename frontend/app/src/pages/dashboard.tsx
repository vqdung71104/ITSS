import React from "react";
import Slidebar from "../components/Dashboard/Slidebar";
import { Outlet } from "react-router-dom";
import Navbar from "../components/home/Navbar";

const Dashboard = () => {
  return (
    <div className="flex min-h-screen">
      <Slidebar />
      <div className="flex-1 ml-64 bg-gray-100 min-h-full w-full">
        <Navbar />
        <Outlet />
      </div>
    </div>
  );
};

export default Dashboard;
