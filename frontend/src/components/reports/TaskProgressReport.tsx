import { use, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Progress } from "../ui/progress";
import { useAuth } from "../../contexts/AuthContext";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { getGroups } from "../../data/groupData";
import { getProjects } from "../../data/projectsData";
import { getTasks } from "../../data/taskData";
import dayjs from "dayjs";
import isoWeek from "dayjs/plugin/isoWeek";
dayjs.extend(isoWeek);

// Mock data
const mockProjects = [
  { id: "project1", name: "Research on Machine Learning Applications" },
  { id: "project2", name: "Sustainable Energy Solutions" },
  { id: "project3", name: "Mobile App Development" },
];

// const mockGroups = [
//   { id: "group1", name: "ML Analysis Team", projectId: "project1" },
//   { id: "group2", name: "Data Collection Team", projectId: "project1" },
//   { id: "group3", name: "Energy Research Team", projectId: "project2" },
// ];

// Tạo mockTimeData động theo tuần từ filteredTasks
const mockTimeData = (filteredTasks: any[]) => {
  if (!filteredTasks.length) return [];

  // Sắp xếp task theo createdAt tăng dần
  const sortedTasks = [...filteredTasks].sort(
    (a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
  );

  // Chia tuần: mỗi tuần là 7 ngày, bắt đầu từ task đầu tiên
  const firstDate = new Date(sortedTasks[0].createdAt);
  const weekMap: { [week: number]: { planned: number; actual: number } } = {};

  sortedTasks.forEach((task) => {
    if (!task.createdAt) return;
    const daysDiff = Math.floor(
      (new Date(task.createdAt).getTime() - firstDate.getTime()) /
        (1000 * 60 * 60 * 24)
    );
    const weekNum = Math.floor(daysDiff / 7) + 1; // Week 1 bắt đầu từ task đầu tiên
    if (!weekMap[weekNum]) {
      weekMap[weekNum] = { planned: 0, actual: 0 };
    }
    weekMap[weekNum].planned += 1;
    if (task.status === "completed") {
      weekMap[weekNum].actual += 1;
    }
  });

  return Object.entries(weekMap).map(([week, value]) => ({
    name: `Week ${week}`,
    planned: value.planned,
    actual: value.actual,
  }));
};

export function TaskProgressReport() {
  const { user } = useAuth();
  const [selectedProject, setSelectedProject] = useState("");
  const [selectedGroup, setSelectedGroup] = useState("");
  const [groups, setGroups] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);
  const [tasks, setTasks] = useState<any[]>([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(true);
  const [isLoadingProjects, setIsLoadingProjects] = useState(true);
  const [isLoadingGroups, setIsLoadingGroups] = useState(true);
  const isMentor = user?.role === "mentor";
  useEffect(() => {
    const fetchTasks = async () => {
      setIsLoadingTasks(true);
      try {
        const data = await getTasks();
        setTasks(data);
      } catch (error) {
        setTasks([]);
        console.error("Error fetching tasks:", error);
      } finally {
        setIsLoadingTasks(false);
      }
    };
    fetchTasks();
  }, []);
  console.log("Tasks:", tasks);
  useEffect(() => {
    const fetchProjects = async () => {
      setIsLoadingProjects(true);
      try {
        const data = await getProjects();
        setProjects(data);
      } catch (error) {
        setProjects([]);
        console.error("Error fetching projects:", error);
      } finally {
        setIsLoadingProjects(false);
      }
    };
    fetchProjects();
  }, []);
  console.log("Projects:", projects);
  useEffect(() => {
    const fetchGroups = async () => {
      setIsLoadingGroups(true);
      try {
        const data = await getGroups();
        setGroups(data);
      } catch (error) {
        setGroups([]);
        console.error("Error fetching groups:", error);
      } finally {
        setIsLoadingGroups(false);
      }
    };
    fetchGroups();
  }, []);
  console.log("Groups:", groups);
  // const filteredGroups = groups.filter(
  //   (group) => group.projectId === selectedProject
  // );
  const filteredGroups = groups;
  console.log("Filtered groups:", filteredGroups);
  // When project changes, reset group selection
  const handleProjectChange = (value: string) => {
    setSelectedProject(value);
    setSelectedGroup("");
  };
  // Lọc tasks theo group đã chọn, nếu chưa chọn thì trả về mảng rỗng
  const filteredTasks = selectedGroup
    ? tasks.filter((t) => t.groupId === selectedGroup)
    : [];

  // Tính toán thống kê task cho group đã chọn
  const mockTaskProgress = [
    {
      name: "Todo",
      value: filteredTasks.filter((t) => t.status === "todo").length,
    },
    {
      name: "In Progress",
      value: filteredTasks.filter((t) => t.status === "in-progress").length,
    },
    {
      name: "In Review",
      value: filteredTasks.filter((t) => t.status === "review").length,
    },
    {
      name: "Completed",
      value: filteredTasks.filter((t) => t.status === "completed").length,
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-4">
        <div className="w-full md:w-1/2">
          <Select
            value={selectedGroup}
            onValueChange={setSelectedGroup}
            disabled={filteredGroups.length === 0}
          >
            <SelectTrigger className="border-academe-300 focus:ring-academe-400">
              <SelectValue
                placeholder={
                  filteredGroups.length
                    ? "Select Group (Optional)"
                    : "No groups available"
                }
              />
            </SelectTrigger>
            <SelectContent>
              {filteredGroups.map((group) => (
                <SelectItem key={group.id} value={group.id}>
                  {group.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {mockTaskProgress.map((item, idx) => (
          <Card className="border-academe-100" key={item.name}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {item.name === "Todo"
                  ? "Tasks To Do"
                  : item.name === "In Progress"
                  ? "Tasks In Progress"
                  : item.name === "In Review"
                  ? "Tasks In Review"
                  : "Tasks Completed"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {selectedGroup ? item.value : 0}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="border-academe-100">
        <CardHeader>
          <CardTitle>
            {selectedGroup
              ? `Progress of ${
                  filteredGroups.find((g) => g.id === selectedGroup)?.name || ""
                }`
              : "Project Progress"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between">
                <div className="text-sm font-medium">Overall Completion</div>
                <div className="text-sm font-medium text-academe-600">
                  {selectedGroup && filteredTasks.length > 0
                    ? `${Math.round(
                        (mockTaskProgress[3].value / filteredTasks.length) * 100
                      )}%`
                    : "0%"}
                </div>
              </div>
              <Progress
                value={
                  selectedGroup && filteredTasks.length > 0
                    ? (mockTaskProgress[3].value / filteredTasks.length) * 100
                    : 0
                }
                className="h-2 mt-2"
              />
            </div>

            <div className="h-[300px] mt-8">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={selectedGroup ? mockTaskProgress : []}
                  margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" name="Number of Tasks" fill="#9b87f5" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="h-[300px] mt-8">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={selectedGroup ? mockTimeData(filteredTasks) : []}
                  margin={{ top: 5, right: 20, left: 20, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="planned" name="Planned Tasks" fill="#9b87f5" />
                  <Bar dataKey="actual" name="Completed Tasks" fill="#7E69AB" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
