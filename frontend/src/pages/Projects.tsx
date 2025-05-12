// import { useState, useEffect } from "react";
// import { DashboardLayout } from "../components/layout/DashboardLayout";
// import { ProjectList } from "../components/projects/ProjectList";
// import { Project } from "../components/projects/ProjectCard";
// import { Button } from "../components/ui/button";
// import { useAuth } from "../contexts/AuthContext";
// import { Plus } from "lucide-react";
// import axiosInstance from "../axios-config";
// const Projects = () => {
//   const { user } = useAuth();
//   const [projects, setProjects] = useState<Project[]>([]);

//   // Mock data loading
//   useEffect(() => {
//     // Generate mock project data
//     const fetchProjects = async () => {
//       try {
//         const response = await axiosInstance.get("/projects");
//         console.log("Projects fetched:", response.data);
//         // Giả sử API trả về mảng projects
//         const projectsData = response.data.map((project: any) => ({
//           id: project._id,
//           title: project.title,
//           description: project.description,
//           mentorName: project.mentor.ho_ten,
//           mentorId: project.mentor._id,
//           teamLeaderId: "con cac",
//           teamLeaderName: "dau buoi",
//           members: 4,
//           status: "open",
//           progress: 50,
//           tags: ["tag1", "tag2"],
//         }));
//         setProjects(projectsData);
//         console.log("Projects state updated:", projectsData);
//       } catch (error) {
//         console.error("Error fetching projects:", error);
//         // Có thể thêm thông báo lỗi cho người dùng
//       }
//     };
//     fetchProjects();
//   }, [user]);

//   const handleProjectClick = (project: Project) => {
//     alert(`Project clicked: ${project.title}`);
//     console.log("Project clicked:", project);
//     // This would navigate to project details in a real application
//   };

//   return (
//     <DashboardLayout>
//       <div className="space-y-6">
//         <div className="flex justify-between items-center">
//           <div>
//             <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
//             <p className="text-muted-foreground">
//               {user?.role === "mentor"
//                 ? "Create and manage academic projects"
//                 : user?.role === "leader"
//                 ? "Lead and organize your project teams"
//                 : "Browse and join academic projects"}
//             </p>
//           </div>

//           {user?.role === "mentor" && (
//             <Button>
//               <Plus className="h-4 w-4 mr-2" /> Create Project
//             </Button>
//           )}
//         </div>

//         <ProjectList projects={projects} onProjectClick={handleProjectClick} />
//       </div>
//     </DashboardLayout>
//   );
// };

// export default Projects;
import { useState, useEffect } from "react";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { ProjectList } from "../components/projects/ProjectList";
import { Project } from "../components/projects/ProjectCard";
import { Button } from "../components/ui/button";
import { useAuth } from "../contexts/AuthContext";
import { Plus } from "lucide-react";
import { getProjects } from "../data/projectsData";

const Projects = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        const projectsData = await getProjects();
        setProjects(projectsData);
        console.log("Projects state updated:", projectsData);
      } catch (error) {
        console.error("Error loading projects:", error);
        // Có thể thêm thông báo lỗi cho người dùng
      }
    };

    if (user?.id) {
      loadProjects();
    }
  }, [user]);

  const handleProjectClick = (project: Project) => {
    alert(`Project clicked: ${project.title}`);
    console.log("Project clicked:", project);
  };

  return (
    <DashboardLayout>
      {/* Giữ nguyên phần JSX */}
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Projects</h1>
            <p className="text-muted-foreground">
              {user?.role === "mentor"
                ? "Create and manage academic projects"
                : user?.role === "leader"
                ? "Lead and organize your project teams"
                : "Browse and join academic projects"}
            </p>
          </div>

          {user?.role === "mentor" && (
            <Button>
              <Plus className="h-4 w-4 mr-2" /> Create Project
            </Button>
          )}
        </div>

        <ProjectList projects={projects} onProjectClick={handleProjectClick} />
      </div>
    </DashboardLayout>
  );
};

export default Projects;
