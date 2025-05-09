import React, { useState } from "react";
import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";

interface Project {
  id: number;
  name: string;
  description: string;
}

const MuiProjectManager: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [open, setOpen] = useState(false);
  const [newProject, setNewProject] = useState({ name: "", description: "" });
  const [editIndex, setEditIndex] = useState<number | null>(null);

  const handleOpen = () => {
    setNewProject({ name: "", description: "" });
    setEditIndex(null);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSave = () => {
    if (editIndex !== null) {
      const updatedProjects = [...projects];
      updatedProjects[editIndex] = {
        ...updatedProjects[editIndex],
        ...newProject,
      };
      setProjects(updatedProjects);
    } else {
      setProjects([...projects, { id: projects.length + 1, ...newProject }]);
    }
    setOpen(false);
  };

  const handleEdit = (index: number) => {
    setNewProject({
      name: projects[index].name,
      description: projects[index].description,
    });
    setEditIndex(index);
    setOpen(true);
  };

  const handleDelete = (index: number) => {
    setProjects(projects.filter((_, i) => i !== index));
  };

  return (
    <Box p={4}>
      <Typography variant="h4" gutterBottom>
        Project Management
      </Typography>
      <Button variant="contained" color="primary" onClick={handleOpen}>
        Add Project
      </Button>
      <TableContainer component={Paper} sx={{ marginTop: 2 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {projects.map((project, index) => (
              <TableRow key={project.id}>
                <TableCell>{project.id}</TableCell>
                <TableCell>{project.name}</TableCell>
                <TableCell>{project.description}</TableCell>
                <TableCell>
                  <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => handleEdit(index)}
                    sx={{ marginRight: 1 }}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => handleDelete(index)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={handleClose}>
        <DialogTitle>
          {editIndex !== null ? "Edit Project" : "Add Project"}
        </DialogTitle>
        <DialogContent>
          <TextField
            label="Project Name"
            fullWidth
            margin="normal"
            value={newProject.name}
            onChange={(e) =>
              setNewProject({ ...newProject, name: e.target.value })
            }
          />
          <TextField
            label="Description"
            fullWidth
            margin="normal"
            value={newProject.description}
            onChange={(e) =>
              setNewProject({ ...newProject, description: e.target.value })
            }
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary">
            Cancel
          </Button>
          <Button onClick={handleSave} color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MuiProjectManager;
