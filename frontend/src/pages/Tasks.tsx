import { useState, useEffect } from "react";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { TaskBoard } from "../components/tasks/TaskBoard";
import { Task, TaskCard } from "../components/tasks/TaskCard";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { useAuth } from "../contexts/AuthContext";
import { Plus } from "lucide-react";
import { toast } from "../components/ui/sonner";
import { Link } from "react-router-dom";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "../components/ui/card";
import { getTasks } from "../data/taskData";
const Tasks = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [projectFilter, setProjectFilter] = useState<string>("all");
  const recentTasks = tasks.slice(0, 5); // Example: Get the first 5 tasks as recent tasks

  // Mock data loading
  useEffect(() => {
    const loadTasks = async () => {
      try {
        console.log("Loading Tasks...");
        const tasksData = await getTasks();
        setTasks(tasksData);
        console.log("Tasks state updated:", tasksData);
      } catch (error) {
        console.error("Error loading Tasks:", error);
        // Có thể thêm thông báo lỗi cho người dùng
      }
    };
    if (user?.id) {
      loadTasks();
    }
    // Generate mock tasks data
    // const mockTasks: Task[] = [
    //   {
    //     id: "task1",
    //     title: "Literature Review",
    //     description:
    //       "Review existing research papers on the topic and create a summary",
    //     status: "in-progress",
    //     priority: "high",
    //     dueDate: "2025-05-20",
    //     assignee: [
    //       {
    //         id: user?.id || "user1",
    //         name: user?.name || "John Doe",
    //         avatar: user?.avatar,
    //       },
    //     ],
    //     projectId: "project1",
    //     projectTitle: "Research on Machine Learning Applications",
    //   },
    //   {
    //     id: "task2",
    //     title: "Data Collection",
    //     description: "Collect dataset from the provided sources",
    //     status: "todo",
    //     priority: "medium",
    //     dueDate: "2025-05-25",
    //     assignee: [
    //       {
    //         id: user?.id || "user1",
    //         name: user?.name || "John Doe",
    //         avatar: user?.avatar,
    //       },
    //     ],
    //     projectId: "project1",
    //     projectTitle: "Research on Machine Learning Applications",
    //   },
    //   {
    //     id: "task3",
    //     title: "Methodology Design",
    //     description: "Design research methodology and framework",
    //     status: "review",
    //     priority: "high",
    //     dueDate: "2025-05-15",
    //     assignee: [
    //       {
    //         id: "user2",
    //         name: "Alice Smith",
    //         avatar: `https://ui-avatars.com/api/?name=Alice+Smith&background=random`,
    //       },
    //     ],
    //     projectId: "project1",
    //     projectTitle: "Research on Machine Learning Applications",
    //   },
    //   {
    //     id: "task4",
    //     title: "Survey Creation",
    //     description: "Create survey questions for data collection",
    //     status: "completed",
    //     priority: "low",
    //     dueDate: "2025-05-10",
    //     assignee: [
    //       {
    //         id: user?.id || "user1",
    //         name: user?.name || "John Doe",
    //         avatar: user?.avatar,
    //       },
    //     ],
    //     projectId: "project1",
    //     projectTitle: "Research on Machine Learning Applications",
    //   },
    //   {
    //     id: "task5",
    //     title: "Energy Audit",
    //     description: "Conduct energy audit of campus buildings",
    //     status: "todo",
    //     priority: "medium",
    //     dueDate: "2025-06-05",
    //     projectId: "project2",
    //     projectTitle: "Sustainable Energy Solutions",
    //   },
    // ];

    // setTasks(mockTasks);
  }, [user]);

  const handleTaskStatusChange = (
    taskId: string,
    newStatus: Task["status"]
  ) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId ? { ...task, status: newStatus } : task
      )
    );

    toast.success(`Task status updated to ${newStatus.replace("-", " ")}`);
  };

  const handleTaskClick = (task: Task) => {
    console.log("Task clicked:", task);
    // This would open a task detail dialog in a real application
  };

  // Unique projects for filter
  const projects = Array.from(
    new Set(
      tasks.map((task) => ({ id: task.projectId, title: task.projectTitle }))
    )
  );

  //   return (
  //     <DashboardLayout>
  //       <div className="space-y-6">
  //         <div className="flex justify-between items-center">
  //           <div>
  //             <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
  //             <p className="text-muted-foreground">
  //               {user?.role === "leader"
  //                 ? "Assign and manage tasks for your team members"
  //                 : "Track and update your assigned tasks"}
  //             </p>
  //           </div>

  //           {user?.role === "mentor" && (
  //             <Button>
  //               <Plus className="h-4 w-4 mr-2" /> Create Task
  //             </Button>
  //           )}
  //         </div>

  //         <div className="flex flex-col sm:flex-row gap-4">
  //           <div className="flex-1">
  //             <Input
  //               placeholder="Search tasks..."
  //               value={searchTerm}
  //               onChange={(e) => setSearchTerm(e.target.value)}
  //               className="w-full"
  //             />
  //           </div>
  //           <div className="w-full sm:w-48">
  //             <Select value={projectFilter} onValueChange={setProjectFilter}>
  //               <SelectTrigger>
  //                 <SelectValue placeholder="Filter by Project" />
  //               </SelectTrigger>
  //               <SelectContent>
  //                 <SelectItem value="all">All Projects</SelectItem>
  //                 {projects.map((project) => (
  //                   <SelectItem key={project.id} value={project.id}>
  //                     {project.title}
  //                   </SelectItem>
  //                 ))}
  //               </SelectContent>
  //             </Select>
  //           </div>
  //         </div>

  //         <TaskBoard
  //           tasks={tasks.filter(
  //             (task) =>
  //               (projectFilter === "all" || task.projectId === projectFilter) &&
  //               (task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
  //                 task.description
  //                   .toLowerCase()
  //                   .includes(searchTerm.toLowerCase()))
  //           )}
  //           onTaskClick={handleTaskClick}
  //           onTaskStatusChange={handleTaskStatusChange}
  //         />
  //       </div>
  //     </DashboardLayout>
  //   );
  // };
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Tasks</h1>
            <p className="text-muted-foreground">
              {user?.role === "mentor"
                ? "Assign and manage tasks for your team members"
                : "Track and update your assigned tasks"}
            </p>
          </div>

          {user?.role === "mentor" && (
            <Button>
              <Plus className="h-4 w-4 mr-2" /> Create Task
            </Button>
          )}
        </div>
        {/* Task Filters and Board */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full"
            />
          </div>
          <div className="w-full sm:w-48">
            <Select value={projectFilter} onValueChange={setProjectFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by Project" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                {projects.map((project) => (
                  <SelectItem key={project.id} value={project.id}>
                    {project.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Recent Tasks */}
        <Card>
          {/* <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Recent Tasks</CardTitle>
                <CardDescription>
                  Your recently assigned or updated tasks
                </CardDescription>
              </div>
              <Button asChild>
                <Link to="/dashboard/tasks">View All</Link>
              </Button>
            </div>
          </CardHeader> */}
          <CardContent>
            {recentTasks.length === 0 ? (
              <p className="text-center py-8 text-muted-foreground">
                No tasks assigned yet
              </p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recentTasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* <TaskBoard
          tasks={tasks.filter(
            (task) =>
              (projectFilter === "all" || task.projectId === projectFilter) &&
              (task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                task.description
                  .toLowerCase()
                  .includes(searchTerm.toLowerCase()))
          )}
          onTaskClick={handleTaskClick}
          onTaskStatusChange={handleTaskStatusChange}
        /> */}
      </div>
    </DashboardLayout>
  );
};
export default Tasks;
