import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Tabs,
  Tab,
  Avatar,
} from "@mui/material";
import { Link } from "react-router-dom";
import Login from "./Login";
import logo from "../../assets/image.png"; // Import logo image

const Navbar = () => {
  const [showLogin, setShowLogin] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <>
      <AppBar
        position="sticky"
        elevation={3}
        sx={{ backgroundColor: "#1e88e5" }}
      >
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          {/* Logo + Brand */}
          <Box display="flex" alignItems="center">
            <Avatar
              src={logo}
              alt="Logo"
              sx={{ width: 64, height: 64, marginRight: 2 }}
            />
            <Typography variant="h6" fontWeight={700}>
              ProjectHub
            </Typography>
          </Box>

          {/* Tabs */}
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            textColor="inherit"
            indicatorColor="secondary"
            sx={{ flexGrow: 1, justifyContent: "center" }}
          >
            <Tab label="Home" component={Link} to="/" />
            <Tab label="Lecturer" href="#Lecturer" />
            <Tab label="Group" href="#Group" />
            <Tab label="About Us" href="#AboutUs" />
          </Tabs>

          {/* Login button */}
          <Button
            variant="contained"
            color="secondary"
            sx={{ borderRadius: 2, fontWeight: 600 }}
            onClick={() => setShowLogin(true)}
          >
            Login
          </Button>
        </Toolbar>
      </AppBar>

      {/* Hiển thị component Login khi click */}
      {showLogin && <Login onClose={() => setShowLogin(false)} />}
    </>
  );
};

export default Navbar;
