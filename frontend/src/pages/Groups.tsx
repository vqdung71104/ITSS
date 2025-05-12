import { useState, useEffect } from "react";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { GroupCard, Group } from "../components/groups/GroupCard";
import { Input } from "../components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { useAuth } from "../contexts/AuthContext";
import { getGroups } from "../data/groupData";

const Groups = () => {
  const { user } = useAuth();
  const [groups, setGroups] = useState<Group[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [projectFilter, setProjectFilter] = useState<string>("all");

  useEffect(() => {
    const loadGroups = async () => {
      try {
        console.log("Loading Groups...");
        const GroupsData = await getGroups();
        setGroups(GroupsData);
        console.log("Groups state updated:", GroupsData);
      } catch (error) {
        console.error("Error loading Groups:", error);
        // Có thể thêm thông báo lỗi cho người dùng
      }
    };
    if (user?.id) {
      loadGroups();
    }
  }, [user]);

  const filteredGroups = groups.filter((group) => {
    const matchesSearch =
      group.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      group.projectTitle.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesProject =
      projectFilter === "all" || group.projectId === projectFilter;

    return matchesSearch && matchesProject;
  });

  // Unique projects for filter
  const projects = Array.from(
    new Set(
      groups.map((group) => ({
        id: group.projectId,
        title: group.projectTitle,
      }))
    )
  );

  const handleGroupClick = (group: Group) => {
    console.log("Group clicked:", group);
    // This would navigate to group details in a real application
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Groups</h1>
          <p className="text-muted-foreground">
            {user?.role === "mentor"
              ? "Supervise and monitor project groups"
              : user?.role === "leader"
              ? "Lead and manage your teams"
              : "Collaborate with your project teams"}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Search groups..."
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

        {filteredGroups.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No groups found</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredGroups.map((group) => (
              <GroupCard
                key={group.id}
                group={group}
                onClick={() => handleGroupClick(group)}
              />
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Groups;
