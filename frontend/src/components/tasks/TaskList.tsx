import { useEffect, useState } from "react";
import { Button } from "../ui/button";
import { Plus, Eye, Edit, Trash } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { Badge } from "../ui/badge";
import { toast } from "sonner";
import { TaskForm } from "./TaskForm";
import { useQueryClient } from "@tanstack/react-query";
import axiosInstance from "../../axios-config";
import { getGroupById } from "../../data/groupData"; // Đảm bảo đúng đường dẫn

type Task = {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  dueDate: string;
  assignee?: {
    id: string;
    name: string;
  }[];
  projectId: string;
  projectTitle: string;
};

interface TaskListProps {
  tasks: Task[];
  projectId: string;
  projectTitle?: string;
  groupMembers?: { id: string; role: string }[];
}

export function TaskList({
  tasks,
  projectId = "abc",
  projectTitle = "Project",
}: TaskListProps) {
  const { user } = useAuth();
  const [deleteTaskId, setDeleteTaskId] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isViewOpen, setIsViewOpen] = useState(false);
  const [groupLeaderId, setGroupLeaderId] = useState<string | null>(null);

  useEffect(() => {
    const fetchGroup = async () => {
      try {
        const group = await getGroupById(projectId);
        const leader =
          group && group.members
            ? group.members.find((m: any) => m.role === "leader")
            : null;
        setGroupLeaderId(leader?.id || null);
      } catch (error) {
        setGroupLeaderId(null);
      }
    };
    fetchGroup();
  }, [projectId]);

  const isUserLeader = user?.id === groupLeaderId;

  const handleCreateTask = async (formData: any) => {
    try {
      // Gọi API để tạo task mới
      const response = await axiosInstance.post("/tasks/", {
        title: formData.title,
        description: formData.description,
        group_id: projectId,
        assigned_student_ids: [formData.assigneeName],
        status: formData.status,
        deadline: formData.dueDate,
        priority: formData.priority,
      });

      const newTask = response.data;

      // Chuyển đổi assigned_students thành assignee
      const taskWithAssignee = {
        ...newTask,
        assignee: newTask.assigned_students.map((student: any) => ({
          id: student.id,
          name: student.name,
          avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(
            student.name
          )}&background=random`,
        })),
        dueDate: newTask.deadline,
        projectId: newTask.group_id,
        projectTitle: newTask.group_name,
      };

      // Cập nhật danh sách task trong react-query cache (giống Tasks.tsx)
      queryClient.setQueryData(["tasks"], (oldTasks: any[] | undefined) => {
        return oldTasks ? [taskWithAssignee, ...oldTasks] : [taskWithAssignee];
      });

      toast.success("Task created successfully");
      setIsCreateOpen(false);
    } catch (error) {
      console.error("Failed to create task:", error);
      toast.error("Failed to create task. Please try again.");
    }
  };

  const handleEditTask = async (formData: any) => {
    if (!selectedTask) return;
    try {
      // Gọi API để cập nhật task
      const response = await axiosInstance.put(`/tasks/${selectedTask.id}`, {
        title: formData.title,
        description: formData.description,
        group_id: projectId,
        assigned_student_ids: [formData.assigneeName],
        status: formData.status,
        deadline: formData.dueDate,
        priority: formData.priority,
      });

      const updatedTask = response.data;

      // Chuyển đổi assigned_students thành assignee
      const taskWithAssignee = {
        ...updatedTask,
        assignee: updatedTask.assigned_students.map((student: any) => ({
          id: student.id,
          name: student.name,
          avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(
            student.name
          )}&background=random`,
        })),
        dueDate: updatedTask.deadline,
        projectId: updatedTask.group_id,
        projectTitle: updatedTask.group_name,
      };

      // Cập nhật danh sách task trong react-query cache
      queryClient.setQueryData(["tasks"], (oldTasks: Task[] | undefined) => {
        return oldTasks
          ? oldTasks.map((task) =>
              task.id === selectedTask.id ? taskWithAssignee : task
            )
          : [];
      });

      toast.success("Task updated successfully");
      setIsEditOpen(false);
      setSelectedTask(null);
    } catch (error) {
      console.error("Failed to update task:", error);
      toast.error("Failed to update task. Please try again.");
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      // Gọi API để xóa task
      await axiosInstance.delete(`/tasks/${taskId}`);

      // Xóa task khỏi react-query cache (giống Tasks.tsx)
      queryClient.setQueryData(["tasks"], (oldTasks: Task[] | undefined) => {
        return oldTasks ? oldTasks.filter((task) => task.id !== taskId) : [];
      });

      toast.success("Task deleted successfully");
      setDeleteTaskId(null);
    } catch (error) {
      console.error("Failed to delete task:", error);
      toast.error("Failed to delete task. Please try again.");
    }
  };

  const statusColor = {
    todo: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
    "in-progress":
      "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    review:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
    completed:
      "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
  };

  const priorityColor = {
    low: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    medium:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
    high: "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Project Tasks</h3>
        {isUserLeader && (
          <Button
            size="sm"
            onClick={() => setIsCreateOpen(true)}
            className="bg-academe-500 hover:bg-academe-600"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Task
          </Button>
        )}
      </div>

      {tasks.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No tasks found for this project.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Title</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Due Date</TableHead>
                <TableHead>Assignee</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell className="font-medium">{task.title}</TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        statusColor[task.status as keyof typeof statusColor]
                      }
                    >
                      {task.status === "in-progress"
                        ? "In Progress"
                        : task.status.charAt(0).toUpperCase() +
                          task.status.slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant="outline"
                      className={
                        priorityColor[
                          task.priority as keyof typeof priorityColor
                        ]
                      }
                    >
                      {task.priority.charAt(0).toUpperCase() +
                        task.priority.slice(1)}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {new Date(task.dueDate).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    {task.assignee && task.assignee.length > 0
                      ? task.assignee
                          .map((assignee) => assignee.name)
                          .join(", ")
                      : "Unassigned"}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setSelectedTask(task);
                          setIsViewOpen(true);
                        }}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {isUserLeader && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setSelectedTask(task);
                              setIsEditOpen(true);
                            }}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setDeleteTaskId(task.id)}
                          >
                            <Trash className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      {/* Create Task Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="sm:max-w-[500px] border-academe-200">
          <DialogHeader>
            <DialogTitle className="text-academe-700">
              Create New Task
            </DialogTitle>
          </DialogHeader>
          <TaskForm
            projectId={projectId}
            // projectTitle={projectTitle}
            onSubmit={handleCreateTask}
            onCancel={() => setIsCreateOpen(false)}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Task Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="sm:max-w-[500px] border-academe-200">
          <DialogHeader>
            <DialogTitle className="text-academe-700">Edit Task</DialogTitle>
          </DialogHeader>
          {selectedTask && (
            <TaskForm
              initialData={selectedTask}
              projectId={selectedTask.projectId}
              // projectTitle={selectedTask.projectTitle}
              onSubmit={handleEditTask}
              onCancel={() => setIsEditOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* View Task Dialog */}
      <Dialog open={isViewOpen} onOpenChange={setIsViewOpen}>
        <DialogContent className="sm:max-w-[500px] border-academe-200">
          <DialogHeader>
            <DialogTitle className="text-academe-700">Task Details</DialogTitle>
          </DialogHeader>
          {selectedTask && (
            <div className="space-y-4 mt-4">
              <div>
                <h3 className="font-medium text-sm text-muted-foreground">
                  Title
                </h3>
                <p>{selectedTask.title}</p>
              </div>
              <div>
                <h3 className="font-medium text-sm text-muted-foreground">
                  Description
                </h3>
                <p>{selectedTask.description}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h3 className="font-medium text-sm text-muted-foreground">
                    Status
                  </h3>
                  <Badge
                    variant="outline"
                    className={
                      statusColor[
                        selectedTask.status as keyof typeof statusColor
                      ]
                    }
                  >
                    {selectedTask.status === "in-progress"
                      ? "In Progress"
                      : selectedTask.status.charAt(0).toUpperCase() +
                        selectedTask.status.slice(1)}
                  </Badge>
                </div>
                <div>
                  <h3 className="font-medium text-sm text-muted-foreground">
                    Priority
                  </h3>
                  <Badge
                    variant="outline"
                    className={
                      priorityColor[
                        selectedTask.priority as keyof typeof priorityColor
                      ]
                    }
                  >
                    {selectedTask.priority.charAt(0).toUpperCase() +
                      selectedTask.priority.slice(1)}
                  </Badge>
                </div>
                <div>
                  <h3 className="font-medium text-sm text-muted-foreground">
                    Due Date
                  </h3>
                  <p>{new Date(selectedTask.dueDate).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="font-medium text-sm text-muted-foreground">
                    Assignee
                  </h3>
                  <p>
                    {selectedTask.assignee && selectedTask.assignee.length > 0
                      ? selectedTask.assignee
                          .map((assignee) => assignee.name)
                          .join(", ")
                      : "Unassigned"}
                  </p>
                </div>
              </div>
              <div className="flex justify-end gap-2 pt-4">
                <Button
                  onClick={() => setIsViewOpen(false)}
                  className="bg-academe-500 hover:bg-academe-600"
                >
                  Close
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Task Confirmation Dialog */}
      <AlertDialog
        open={!!deleteTaskId}
        onOpenChange={() => setDeleteTaskId(null)}
      >
        <AlertDialogContent className="border-academe-200">
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the task and cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-academe-300 hover:bg-academe-50">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteTaskId && handleDeleteTask(deleteTaskId)}
              className="bg-destructive text-destructive-foreground"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
