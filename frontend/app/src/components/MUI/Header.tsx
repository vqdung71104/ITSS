import React from "react";
import { AppBar, Toolbar, Typography, Button, Box } from "@mui/material";

const Header: React.FC = () => {
  return (
    <AppBar position="static" color="primary">
      <Toolbar>
        {/* Tiêu đề */}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Project Management
        </Typography>

        {/* Các nút điều hướng */}
        <Box>
          <Button color="inherit" href="/dashboard">
            Dashboard
          </Button>
          <Button color="inherit" href="/projects">
            Projects
          </Button>
          <Button color="inherit" href="/login">
            Login
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
