import axiosInstance from "../axios-config";

// Định nghĩa lại type Task tại đây (tránh import gây xung đột)
export type Task = {
  id: string;
  title: string;
  description: string;
  status: "todo" | "in-progress" | "review" | "completed" | "pending";
  groupId: string;
  priority: "low" | "medium" | "high";
  dueDate: string;
  assignee?: {
    id: string;
    name: string;
    avatar?: string;
  }[];
  projectId: string;
  projectTitle: string;
  createdAt?: string;
};

let cachedTasks: Task[] = [];
let lastFetchTime = 0;
const CACHE_DURATION = 100 * 60 * 1000;

export const getTasks = async (forceRefresh = false): Promise<Task[]> => {
  const now = Date.now();

  if (
    cachedTasks.length > 0 &&
    now - lastFetchTime < CACHE_DURATION &&
    !forceRefresh
  ) {
    return cachedTasks;
  }

  try {
    const response = await axiosInstance.get("/tasks/");
    const tasks: Task[] = response.data.map((task: any) => ({
      id: task.id,
      title: task.title,
      description: task.description,
      status: task.status,
      groupId: task.group_id,
      priority: task.priority,
      dueDate: task.deadline,
      assignee: Array.isArray(task.assigned_students)
        ? task.assigned_students.map((student: any) => ({
            id: student.id,
            name: student.ho_ten || "Unnamed",
            avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(
              student.ho_ten || "Unnamed"
            )}&background=random`,
          }))
        : [],
      projectId: task.group_id,
      projectTitle: task.group_name || "",
      createdAt: task.created_at,
    }));

    cachedTasks = tasks;
    lastFetchTime = now;
    return tasks;
  } catch (error) {
    console.error("Error fetching tasks:", error);
    if (cachedTasks.length > 0) {
      console.warn("Using cached tasks due to API error");
      return cachedTasks;
    }
    throw error;
  }
};

export const getCachedTasks = (): Task[] => {
  return cachedTasks;
};

export const getTaskById = async (taskId: string): Promise<Task | null> => {
  try {
    const response = await axiosInstance.get(`/tasks/${taskId}`);
    const task = response.data;
    return {
      id: task.id,
      title: task.title,
      description: task.description,
      status: task.status,
      groupId: task.group_id,
      priority: task.priority,
      dueDate: task.deadline,
      assignee: Array.isArray(task.assigned_students)
        ? task.assigned_students.map((student: any) => ({
            id: student.id,
            name: student.ho_ten ? student.ho_ten : student.name ? student.name : "Unnamed",
            avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(student.ho_ten ? student.ho_ten : student.name ? student.name : "Unnamed")}&background=random`,
          }))
        : [],
      projectId: task.group_id,
      projectTitle: task.group_name || "",
      createdAt: task.created_at,
    };
  } catch (error) {
    console.error("❌ Error fetching task by ID:", error);
    return null;
  }
};
