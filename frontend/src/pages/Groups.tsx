import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { GroupsHeader } from "../components/groups/GroupsHeader";
import { GroupsContent } from "../components/groups/GroupsContent";
import { CreateGroupForm } from "../components/groups/CreateGroupForm";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
// import { getProjects } from "../services/groupService";
import { Group } from "../types/group";
import { getGroups } from "../data/groupData";
// import { getGroups } from "../services/groupService";

import { getProjects } from "../data/projectsData";
import { getTasks } from "../data/taskData";
const Groups = () => {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedProjectId, setSelectedProjectId] = useState<string>("all");

  const { data: groups = [], isLoading: isLoadingGroups } = useQuery({
    queryKey: ["groups", selectedProjectId],
    queryFn: () =>
      getGroups(
        selectedProjectId === "all"
          ? undefined
          : selectedProjectId !== undefined
      ),
  });
  console.log("groupasbss", groups);
  const { data: projects = [], isLoading: isLoadingProjects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => getProjects(),
  });
  const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ["tasks"],
    queryFn: () => getTasks(),
  });

  const handleCreateSuccess = () => {
    setIsCreateDialogOpen(false);
  };

  const groupsWithProgress = groups.map((group) => {
    const groupTasks = tasks.filter((t) => t.groupId === group.id);
    const completed = groupTasks.filter((t) => t.status === "completed").length;
    const total = groupTasks.length;
    const progress = total > 0 ? Math.round((completed / total) * 100) : 0;
    return { ...group, progress };
  });

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <GroupsHeader onCreateGroup={() => setIsCreateDialogOpen(true)} />

        <GroupsContent
          groups={groupsWithProgress}
          projects={projects}
          isLoading={isLoadingGroups || isLoadingProjects}
          selectedProjectId={selectedProjectId}
          onProjectFilterChange={setSelectedProjectId}
        />
      </div>

      <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
        <DialogContent className="sm:max-w-[550px]">
          <DialogHeader>
            <DialogTitle>Create New Group</DialogTitle>
          </DialogHeader>
          <CreateGroupForm
            projects={projects}
            onSuccess={handleCreateSuccess}
            onCancel={() => setIsCreateDialogOpen(false)}
          />
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
};

export default Groups;
