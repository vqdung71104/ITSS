import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "../components/ui/avatar";
import { Task } from "../components/tasks/TaskCard";
import { getTaskById } from "../data/taskData";
import MyReportViewer from "../components/reports/MyReportViewer";
import ReportForm from "../components/reports/ReportForm";
import { ArrowLeft, ClipboardList } from "lucide-react";
import { EvaluationButton } from "../components/reports/EvaluationButton";
// import TaskFileTab from "../components/tasks/TaskFileTab";
// Update the import path below if the file exists elsewhere:
import TaskFileTab from "../components/tasks/TaskFileTab";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";

export default function TaskDetail() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [reloadReports, setReloadReports] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (taskId) {
      setIsLoading(true);
      getTaskById(taskId)
        .then((taskData) => setTask(taskData))
        .catch((err) => console.error("Failed to load task", err))
        .finally(() => setIsLoading(false));
    }
  }, [taskId]);

  const handleReload = () => setReloadReports((r) => r + 1);

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-96">
          <div className="animate-pulse text-lg">Loading task details...</div>
        </div>
      </DashboardLayout>
    );
  }

  if (!task) {
    return (
      <DashboardLayout>
        <div className="flex flex-col items-center justify-center h-96">
          <h2 className="text-xl font-semibold">Task not found</h2>
          <p className="text-muted-foreground mb-4">
            The task you're looking for doesn't exist or has been removed.
          </p>
          <Button onClick={() => navigate("/dashboard/tasks")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Tasks
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="w-full px-16 py-10 space-y-10">
        {/* Header: Back, Create Evaluation, và Task title */}
        <div className="flex flex-col gap-2 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/dashboard/tasks")}
                className="flex items-center gap-2 text-base font-semibold px-2"
              >
                <ArrowLeft className="h-5 w-5" />
                Back to Tasks
              </Button>
            </div>
            {/* Nút Create Evaluation ở đầu trang */}
            {/* <EvaluationButton
              studentId={
                task.assignee && task.assignee.length > 0
                  ? task.assignee[0].id
                  : ""
              }
              projectId={task.projectId}
            /> */}
          </div>
          <div className="flex items-center gap-3 ml-2">
            <div className="h-10 w-10 bg-academe-100 rounded-full flex items-center justify-center">
              <ClipboardList className="h-6 w-6 text-academe-700" />
            </div>
            <h1 className="text-3xl font-bold text-academe-700">
              {task.title}
            </h1>
          </div>
        </div>
        {/* Grid: Group/Desc và Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full">
          {/* Group/Students/Desc: chiếm 2/3 */}
          <div className="md:col-span-2 bg-white p-8 rounded-2xl border shadow-sm flex flex-col gap-6 border-l-4 border-academe-500">
            <div>
              <span className="text-xs font-semibold text-muted-foreground">
                Group
              </span>
              <div className="font-bold text-xl">{task.projectTitle}</div>
            </div>
            <div>
              <span className="text-xs font-semibold text-muted-foreground">
                Assigned Students
              </span>
              <div className="flex gap-4 mt-3">
                {task.assignee && task.assignee.length > 0 ? (
                  task.assignee.map((student) => (
                    <div key={student.id} className="flex items-center gap-2">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={student.avatar} />
                        <AvatarFallback>
                          {student.name
                            ?.split(" ")
                            .map((w: string) => w[0])
                            .join("") || "?"}
                        </AvatarFallback>
                      </Avatar>
                      <span className="font-semibold text-lg">
                        {student.name}
                      </span>
                    </div>
                  ))
                ) : (
                  <span className="italic text-muted-foreground">
                    Unassigned
                  </span>
                )}
              </div>
            </div>
            <div>
              <span className="text-xs font-semibold text-muted-foreground">
                Description
              </span>
              <div className="bg-muted/30 rounded-lg px-4 py-2 mt-2">
                {task.description}
              </div>
            </div>
          </div>
          {/* Status: chiếm 1/3, kéo sát phải */}
          <div className="bg-white p-8 rounded-2xl border shadow-sm flex flex-col gap-7 border-l-4 border-academe-500 ml-auto w-full max-w-sm">
            <div>
              <span className="text-xs font-semibold text-muted-foreground">
                Status
              </span>
              <div>
                <Badge className="text-base px-3 py-1 bg-academe-100 text-academe-700">
                  {task.status}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-xs font-semibold text-muted-foreground">
                Priority
              </span>
              <div>
                <Badge className="text-base px-3 py-1 bg-academe-100 text-academe-700">
                  {task.priority}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-xs font-semibold text-muted-foreground">
                Due Date
              </span>
              <div className="text-lg">
                {new Date(task.dueDate).toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>
        {/* Report & Upload File Tabs - Full width, chia đều */}
        <Tabs defaultValue="report" className="w-full">
          <TabsList className="mb-4 grid grid-cols-2 w-full">
            <TabsTrigger value="report" className="w-full">
              Report
            </TabsTrigger>
            <TabsTrigger value="files" className="w-full">
              Upload File
            </TabsTrigger>
          </TabsList>
          <TabsContent value="report">
            <div className="bg-card p-8 rounded-2xl border border-l-4 border-academe-500">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-bold">
                  {task.assignee && task.assignee.length > 0
                    ? `${task.assignee[0].name}'s Report`
                    : "Report"}
                </h2>
                <ReportForm taskId={task.id} onReportCreated={handleReload} />
              </div>
              <MyReportViewer taskId={task.id} reload={reloadReports} />
            </div>
          </TabsContent>
          <TabsContent value="files">
            <div className="bg-card p-8 rounded-2xl border border-l-4 border-academe-500">
              <TaskFileTab taskId={task.id} />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
