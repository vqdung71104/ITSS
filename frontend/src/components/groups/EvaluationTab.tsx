// src/components/groups/EvaluationTab.tsx
import { useEffect, useState } from "react";
import axiosInstance from "../../axios-config";
import { Card, CardContent } from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { toast } from "sonner";

interface Evaluation {
  id: string;
  from_student: { id: string; name: string };
  to_student: { id: string; name: string };
  project_id: string;
  score: number;
  comment: string;
  created_at: string;
}

export default function EvaluationTab({ group }: { group: any }) {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!group?.id) return;
    setLoading(true);
    axiosInstance
      .get(`/evaluations/group/${group.id}`)
      .then((res) => setEvaluations(res.data))
      .catch(() => {
        toast.error("Failed to load evaluations");
        setEvaluations([]);
      })
      .finally(() => setLoading(false));
  }, [group?.id]);

  if (loading) return <Skeleton className="w-full h-32" />;
  if (!evaluations.length)
    return (
      <div className="text-center text-muted-foreground py-8">
        No peer evaluations found for this group.
      </div>
    );

  return (
    <div className="space-y-4">
      {evaluations.map((evalItem) => (
        <Card key={evalItem.id} className="border-academe-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-2">
              <span>
                <span className="font-semibold text-academe-700">
                  {evalItem.from_student?.name}
                </span>{" "}
                <span className="text-xs text-muted-foreground">→</span>{" "}
                <span className="font-semibold text-academe-700">
                  {evalItem.to_student?.name}
                </span>
              </span>
              <span className="text-xs text-muted-foreground">
                {new Date(evalItem.created_at).toLocaleString()}
              </span>
            </div>
            <div>
              <span className="font-semibold text-base text-academe-600 mr-2">
                Score:
              </span>
              <span className="text-base text-gray-800">{evalItem.score}</span>
            </div>
            <div>
              <span className="font-semibold text-base text-academe-600 mr-2">
                Comment:
              </span>
              <span className="text-sm text-gray-700">{evalItem.comment}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
