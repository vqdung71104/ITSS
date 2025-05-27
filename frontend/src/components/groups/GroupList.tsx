import { useState } from "react";
import { Button } from "../../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Plus, Users, Eye, Edit, Trash } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../../components/ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../components/ui/dialog";
import { toast } from "sonner";
import { GroupForm } from "./GroupForm";
import { Group, GroupMember } from "./GroupCard";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getStudents } from "../../data/userData";
import { createGroup } from "../../services/groupService";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { useParams, useNavigate } from "react-router-dom";

const formSchema = z.object({
  name: z.string().min(3, "Group name must be at least 3 characters"),
  leaderId: z.string().min(1, "Group leader selection is required"),
});

type FormValues = z.infer<typeof formSchema>;

interface GroupListProps {
  groups: Group[];
  projectTitle?: string;
}

export function GroupList({
  groups,
  projectTitle = "Project",
}: GroupListProps) {
  const { projectId } = useParams<{ projectId: string }>();
  const { user } = useAuth();
  const [deleteGroupId, setDeleteGroupId] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<Group | null>(null);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const navigate = useNavigate();

  const isMentor = user?.role === "mentor";

  const queryClient = useQueryClient();
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      name: "",
      leaderId: "",
    },
  });

  const { data: studentss = [], isLoading: isLoadingStudents } = useQuery({
    queryKey: ["availableStudents"],
    queryFn: () => getStudents(),
  });
  const students = studentss.filter((student) => student.groupId === null);

  const createGroupMutation = useMutation({
    mutationFn: (data: FormValues) => {
      const selectedLeader = students.find((s) => s.id === data.leaderId);
      if (!selectedLeader) {
        throw new Error("Selected leader not found");
      }
      const dataAxios = {
        name: data.name,
        project_id: projectId,
        leader_id: data.leaderId,
      };
      return createGroup(dataAxios);
    },
    onSuccess: (createdGroup) => {
      toast.success("Group created successfully");
      queryClient.invalidateQueries({ queryKey: ["groups"] });
      setIsCreateOpen(false);
      form.reset();
      console.log("Created group:", createdGroup);
      // Navigate đến trang chi tiết group vừa tạo
      if (createdGroup?.id) {
        navigate(`/dashboard/groups/${createdGroup.id}`);
      }
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "Failed to create group"
      );
    },
  });

  const handleCreateGroup = (formData: any) => {
    // In a real app, this would be an API call
    const newGroup = {
      id: `group-${Date.now()}`,
      name: formData.name,
      description: formData.description,
      projectId,
      projectTitle,
      progress: 0,
      members: [
        {
          id: `leader-${Date.now()}`,
          name: formData.leaderName,
          role: "leader" as const,
        },
      ],
    };

    // This would update your state with the new group in a real app
    toast.success("Group created successfully");
    setIsCreateOpen(false);
  };

  const handleEditGroup = (formData: any) => {
    if (!selectedGroup) return;

    // In a real app, this would update the group via an API
    toast.success("Group updated successfully");
    setIsEditOpen(false);
    setSelectedGroup(null);
  };

  const handleDeleteGroup = (groupId: string) => {
    // In a real app, this would be an API call
    toast.success("Group deleted successfully");
    setDeleteGroupId(null);
  };

  const getMemberCount = (group: Group) => {
    return group.members.length;
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium">Project Groups</h3>
        {isMentor && (
          <Button
            size="sm"
            onClick={() => setIsCreateOpen(true)}
            className="bg-academe-500 hover:bg-academe-600"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Group
          </Button>
        )}
      </div>

      {groups.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-muted-foreground">
            No groups found for this project.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {groups.map((group) => (
            <Card key={group.id} className="border-academe-100">
              <CardHeader className="pb-2">
                <div className="flex justify-between">
                  <CardTitle className="text-lg">{group.name}</CardTitle>
                  <div className="flex items-center text-muted-foreground">
                    <Users className="h-4 w-4 mr-1" />
                    <span>{getMemberCount(group)}</span>
                  </div>
                </div>
                <CardDescription className="line-clamp-2">
                  {group.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col space-y-2">
                  <div className="text-sm">
                    <span className="text-muted-foreground">Team Leader: </span>
                    <span>
                      {group.members.find((m) => m.role === "leader")?.name ||
                        "Not assigned"}
                    </span>
                  </div>

                  <div className="flex justify-end mt-4 gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="border-academe-200 hover:bg-academe-50"
                      onClick={() => {
                        // Navigate to group details page
                        window.location.href = `dashboard/groups/${group.id}`;
                      }}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View
                    </Button>
                    {/* {isMentor && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedGroup(group);
                            setIsEditOpen(true);
                          }}
                          className="border-academe-200 hover:bg-academe-50"
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setDeleteGroupId(group.id)}
                          className="border-academe-200 hover:bg-academe-50"
                        >
                          <Trash className="h-4 w-4 mr-2" />
                          Delete
                        </Button>
                      </>
                    )} */}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Group Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent className="sm:max-w-[500px] border-academe-200">
          <DialogHeader>
            <DialogTitle className="text-academe-700">
              Create New Group
            </DialogTitle>
          </DialogHeader>
          <form
            onSubmit={form.handleSubmit((data) =>
              createGroupMutation.mutate(data)
            )}
            className="space-y-6"
          >
            <div>
              <label className="block text-sm font-medium mb-1">
                Group Name
              </label>
              <input
                {...form.register("name")}
                className="w-full border rounded px-3 py-2"
                placeholder="Enter group name"
              />
              {form.formState.errors.name && (
                <p className="text-red-500 text-xs mt-1">
                  {form.formState.errors.name.message}
                </p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Group Leader
              </label>
              <select
                {...form.register("leaderId")}
                className="w-full border rounded px-3 py-2"
                disabled={isLoadingStudents || students.length === 0}
              >
                <option value="">Select group leader</option>
                {students.map((student) => (
                  <option key={student.id} value={student.id}>
                    {student.name} ({student.email})
                  </option>
                ))}
              </select>
              {form.formState.errors.leaderId && (
                <p className="text-red-500 text-xs mt-1">
                  {form.formState.errors.leaderId.message}
                </p>
              )}
            </div>
            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsCreateOpen(false)}
                disabled={createGroupMutation.status === "pending"}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createGroupMutation.status === "pending"}
                className="bg-academe-500 hover:bg-academe-600"
              >
                {createGroupMutation.status === "pending"
                  ? "Creating..."
                  : "Create Group"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Group Dialog */}
      <Dialog open={isEditOpen} onOpenChange={setIsEditOpen}>
        <DialogContent className="sm:max-w-[500px] border-academe-200">
          <DialogHeader>
            <DialogTitle className="text-academe-700">Edit Group</DialogTitle>
          </DialogHeader>
          {selectedGroup && (
            <GroupForm
              initialData={selectedGroup}
              projectId={selectedGroup.projectId}
              projectTitle={selectedGroup.projectTitle}
              onSubmit={handleEditGroup}
              onCancel={() => setIsEditOpen(false)}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Group Confirmation Dialog */}
      <AlertDialog
        open={!!deleteGroupId}
        onOpenChange={() => setDeleteGroupId(null)}
      >
        <AlertDialogContent className="border-academe-200">
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete the group and remove all members from
              it.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel className="border-academe-200 hover:bg-academe-50">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteGroupId && handleDeleteGroup(deleteGroupId)}
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
