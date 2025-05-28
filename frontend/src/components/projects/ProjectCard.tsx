import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Progress } from "../../components/ui/progress";
import { Eye, Edit, Trash, Users, MoreVertical } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import { useNavigate } from "react-router-dom";

export type Project = {
  id: string;
  title: string;
  description: string;
  mentorName: string;
  mentorId: string;
  status: "open" | "in-progress" | "completed";
  progress: number;
  tags: string[];
};

type ProjectCardProps = {
  project: Project;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  userRole?: string;
  userId?: string;
};

export function ProjectCard({
  project,
  onClick,
  onEdit,
  onDelete,
  userRole = "student",
  userId = "",
}: ProjectCardProps) {
  const { user } = useAuth();
  const navigate = useNavigate();

  const statusColor = {
    open: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
    "in-progress":
      "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400",
    completed:
      "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
  };

  const isUserMentor = user?.role === "mentor";
  const isUserOwner = isUserMentor && user?.id === project.mentorId;

  return (
    <Card className="card-hover overflow-hidden border-t-4 border-t-academe-400">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg line-clamp-2 min-h-[3em]">
            {project.title}
          </CardTitle>
          <Badge className={statusColor[project.status]} variant="outline">
            {project.status === "in-progress"
              ? "In Progress"
              : project.status.charAt(0).toUpperCase() +
                project.status.slice(1)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pb-2">
        <div className="space-y-4">
          {/* Description */}
          <CardDescription
            className="text-sm line-clamp-2 min-h-[3em]"
            style={{ overflow: "hidden", textOverflow: "ellipsis" }}
          >
            {project.description}
          </CardDescription>

          {/* Tags */}
          <div
            className="flex flex-wrap gap-1 mt-4 min-h-[2.5rem]"
            style={{ overflow: "hidden" }}
          >
            {project.tags.map((tag) => (
              <Badge key={tag} variant="secondary" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>

          {/* Mentor */}
          <div className="flex justify-between text-sm mt-8 min-h-[4em]">
            <div>
              <span className="text-muted-foreground">Mentor: </span>
              <span>{project.mentorName}</span>
            </div>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-2">
        <Button
          onClick={() => navigate(`/dashboard/projects/${project.id}`)}
          className="w-full"
        >
          {isUserOwner
            ? "Manage Project"
            : user?.role === "mentor" && user?.id === project.mentorId
            ? "Manage Team"
            : project.status === "open"
            ? "View Details"
            : "View Details"}
        </Button>
      </CardFooter>
    </Card>
  );
}
