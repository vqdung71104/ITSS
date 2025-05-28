import { useEffect, useState } from "react";
import axiosInstance from "../../axios-config";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { toast } from "sonner";
import { useAuth } from "../../contexts/AuthContext";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Badge } from "../ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";

type Feedback = {
  id: string | number;
  text: string;
  from: string;
  date: string;
  score: number;
};

export default function GroupEvaluationTab({ group }: { group: any }) {
  const { user } = useAuth();
  const [evaluations, setEvaluations] = useState<any[]>([]);
  const [toStudentId, setToStudentId] = useState("");
  const [score, setScore] = useState(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<any>(null);

  // Lấy tất cả evaluation, lọc theo group.members
  useEffect(() => {
    axiosInstance
      .get(`/evaluations/`)
      .then((res) => {
        setEvaluations(
          (res.data || []).map((ev: any) => ({
            id: ev.id,
            to_student: {
              id: ev.student?.id,
              name: ev.student?.ho_ten,
              email: ev.student?.email,
            },
            from_student: {
              id: ev.evaluator?.id,
              name: ev.evaluator?.ho_ten,
              email: ev.evaluator?.email,
            },
            project: ev.project,
            score: ev.score,
            comment: ev.comment,
            created_at: ev.created_at || "",
          }))
        );
      })
      .catch(() => setEvaluations([]));
  }, [loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!toStudentId) {
      toast.error("Please select a member to evaluate");
      return;
    }
    setLoading(true);
    try {
      await axiosInstance.post("/evaluations/", {
        student_id: toStudentId,
        project_id: group.projectId,
        score,
        comment,
        from_student_id: user?.id,
      });
      toast.success("Evaluation submitted!");
      setScore(0);
      setComment("");
      setToStudentId("");
      setIsDialogOpen(false);
    } catch {
      toast.error("Failed to submit evaluation");
    } finally {
      setLoading(false);
    }
  };

  // Hàm chọn thành viên để xem chi tiết
  const handleMemberSelect = (member: any) => {
    // Gắn thêm feedbacks cho member từ evaluations
    const memberEvaluations = evaluations.filter(
      (ev) => ev.to_student?.id === member.id
    );
    setSelectedMember({
      ...member,
      feedbacks: memberEvaluations.map((ev) => ({
        id: ev.id,
        text: ev.comment,
        from: ev.from_student?.name,
        date: ev.created_at,
        score: ev.score,
      })),
    });
  };

  // Hàm lấy class badge theo nhãn
  const getPerformanceBadge = (performance: string) => {
    const badgeClasses: Record<string, string> = {
      excellent:
        "bg-academe-100 text-academe-800 dark:bg-academe-900/30 dark:text-academe-300",
      good: "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400",
      satisfactory:
        "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400",
      needsImprovement:
        "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400",
      na: "bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400",
    };
    return badgeClasses[performance] || badgeClasses.na;
  };

  // Hàm gán nhãn theo điểm trung bình
  const getPerformanceLabel = (avgScore: number | null) => {
    if (avgScore === null) return "N/A";
    if (avgScore >= 8) return "excellent";
    if (avgScore >= 6.5) return "good";
    if (avgScore >= 5) return "satisfactory";
    return "needsImprovement";
  };

  return (
    <div className="space-y-8 w-full">
      <div className="flex justify-between items-center mb-4 w-full">
        <h3 className="text-lg font-semibold">All Peer Evaluations</h3>
        <Button
          onClick={() => setIsDialogOpen(true)}
          className="bg-academe-500 hover:bg-academe-600 text-white"
        >
          + Create Evaluation
        </Button>
      </div>
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="w-full max-w-lg">
          <DialogHeader>
            <DialogTitle>Peer Evaluation</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-6 w-full">
            <div>
              <label className="block text-sm font-medium mb-1">
                Evaluate Member
              </label>
              <Select value={toStudentId} onValueChange={setToStudentId}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select member" />
                </SelectTrigger>
                <SelectContent className="w-full">
                  {group.members.map((m: any) => (
                    <SelectItem key={m.id} value={m.id} className="w-full">
                      {m.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Score</label>
              <input
                type="number"
                min={0}
                max={10}
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
                className="w-full border rounded px-3 py-2"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Comment</label>
              <Textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Enter evaluation comment"
                required
                className="w-full"
              />
            </div>
            <div className="flex justify-end w-full gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
                className="border-academe-300 hover:bg-academe-50"
                disabled={loading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={loading}
                className="bg-academe-500 hover:bg-academe-600"
              >
                {loading ? "Submitting..." : "Submit"}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
      <div className="w-full overflow-x-auto">
        {group.members.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">
              No members found for the selected project/group.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {group.members.map((member: any) => {
              const memberEvaluations = evaluations.filter(
                (ev) => ev.to_student?.id === member.id
              );
              const hasScore = memberEvaluations.some(
                (ev) => ev.score !== undefined && ev.score !== null
              );
              const avgScore = hasScore
                ? memberEvaluations.reduce(
                    (sum, ev) => sum + (ev.score || 0),
                    0
                  ) /
                  memberEvaluations.filter(
                    (ev) => ev.score !== undefined && ev.score !== null
                  ).length
                : null;
              const performanceLabel = getPerformanceLabel(avgScore);

              return (
                <Card
                  key={member.id}
                  className="border-academe-100 hover:border-academe-300 transition-colors cursor-pointer"
                  onClick={() => handleMemberSelect(member)}
                >
                  <CardHeader className="pb-2">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center space-x-4">
                        <Avatar>
                          <AvatarImage src={member.avatar} />
                          <AvatarFallback>
                            {member.name?.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <CardTitle className="text-lg">
                            {member.name}
                          </CardTitle>
                          <p className="text-sm text-muted-foreground">
                            {member.role}
                          </p>
                          {/* Thêm tổng số feedback và điểm trung bình */}
                          <div className="mt-2 space-y-1">
                            <p className="text-xs text-muted-foreground">
                              Total Feedback:{" "}
                              <span className="font-semibold">
                                {memberEvaluations.length}
                              </span>
                            </p>
                            {hasScore && (
                              <p className="text-xs text-muted-foreground">
                                Average Score:{" "}
                                <span className="font-semibold">
                                  {avgScore}
                                </span>
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                      {/* Example badge, you can customize getPerformanceBadge */}
                      <Badge className={getPerformanceBadge(performanceLabel)}>
                        {performanceLabel === "N/A"
                          ? "N/A"
                          : performanceLabel.charAt(0).toUpperCase() +
                            performanceLabel.slice(1)}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-medium mb-2">
                          Recent Feedback:
                        </h4>
                        {memberEvaluations.length > 0 ? (
                          <div className="space-y-2">
                            {memberEvaluations.slice(0, 1).map((feedback) => (
                              <div
                                key={feedback.id}
                                className="bg-muted p-3 rounded-md text-sm"
                              >
                                <p>"{feedback.comment}"</p>
                                <div className="mt-1 text-xs text-muted-foreground">
                                  {feedback.from_student?.name} -{" "}
                                  {new Date(
                                    feedback.created_at
                                  ).toLocaleDateString()}
                                  {" | Score: "}
                                  <span className="font-semibold">
                                    {feedback.score}
                                  </span>
                                </div>
                              </div>
                            ))}
                            {memberEvaluations.length > 1 && (
                              <p className="text-xs text-muted-foreground">
                                +{memberEvaluations.length - 1} more feedback
                                entries
                              </p>
                            )}
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">
                            No feedback yet
                          </p>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Dialog xem chi tiết thành viên */}
      {selectedMember && (
        <Dialog
          open={!!selectedMember}
          onOpenChange={(open) => !open && setSelectedMember(null)}
        >
          <DialogContent className="sm:max-w-[600px] border-academe-200">
            <DialogHeader>
              <DialogTitle className="text-academe-700">
                Member Details: {selectedMember.name}
              </DialogTitle>
            </DialogHeader>
            <div className="mt-4 space-y-6">
              <div className="flex items-center space-x-4">
                <Avatar className="h-16 w-16">
                  <AvatarImage src={selectedMember.avatar} />
                  <AvatarFallback>
                    {selectedMember.name.charAt(0)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-xl font-semibold">
                    {selectedMember.name}
                  </h3>
                  <p className="text-muted-foreground">{selectedMember.role}</p>
                  <Badge
                    className={getPerformanceBadge(
                      getPerformanceLabel(
                        selectedMember.feedbacks.length > 0
                          ? selectedMember.feedbacks
                              .filter(
                                (fb: Feedback) =>
                                  fb.score !== undefined && fb.score !== null
                              )
                              .reduce(
                                (sum: number, fb: Feedback) =>
                                  sum + (fb.score || 0),
                                0
                              ) /
                              selectedMember.feedbacks.filter(
                                (fb: Feedback) =>
                                  fb.score !== undefined && fb.score !== null
                              ).length
                          : null
                      )
                    )}
                  >
                    {getPerformanceLabel(
                      selectedMember.feedbacks.length > 0
                        ? selectedMember.feedbacks
                            .filter(
                              (fb: Feedback) =>
                                fb.score !== undefined && fb.score !== null
                            )
                            .reduce(
                              (sum: number, fb: Feedback) =>
                                sum + (fb.score || 0),
                              0
                            ) /
                            selectedMember.feedbacks.filter(
                              (fb: Feedback) =>
                                fb.score !== undefined && fb.score !== null
                            ).length
                        : null
                    ) === "N/A"
                      ? "N/A"
                      : getPerformanceLabel(
                          selectedMember.feedbacks.length > 0
                            ? selectedMember.feedbacks
                                .filter(
                                  (fb: Feedback) =>
                                    fb.score !== undefined && fb.score !== null
                                )
                                .reduce(
                                  (sum: number, fb: Feedback) =>
                                    sum + (fb.score || 0),
                                  0
                                ) /
                                selectedMember.feedbacks.filter(
                                  (fb: Feedback) =>
                                    fb.score !== undefined && fb.score !== null
                                ).length
                            : null
                        )
                          .charAt(0)
                          .toUpperCase() +
                        getPerformanceLabel(
                          selectedMember.feedbacks.length > 0
                            ? selectedMember.feedbacks
                                .filter(
                                  (fb: Feedback) =>
                                    fb.score !== undefined && fb.score !== null
                                )
                                .reduce(
                                  (sum: number, fb: Feedback) =>
                                    sum + (fb.score || 0),
                                  0
                                ) /
                                selectedMember.feedbacks.filter(
                                  (fb: Feedback) =>
                                    fb.score !== undefined && fb.score !== null
                                ).length
                            : null
                        ).slice(1)}
                  </Badge>
                  <div className="mt-2 space-y-1">
                    <p className="text-sm text-muted-foreground">
                      Total Feedback:{" "}
                      <span className="font-semibold">
                        {selectedMember.feedbacks.length}
                      </span>
                    </p>
                    {selectedMember.feedbacks.some(
                      (fb: Feedback) =>
                        fb.score !== undefined && fb.score !== null
                    ) && (
                      <p className="text-sm text-muted-foreground">
                        Average Score:{" "}
                        <span className="font-semibold">
                          {(
                            selectedMember.feedbacks
                              .filter(
                                (fb: Feedback) =>
                                  fb.score !== undefined && fb.score !== null
                              )
                              .reduce(
                                (sum: number, fb: Feedback) =>
                                  sum + (fb.score || 0),
                                0
                              ) /
                            selectedMember.feedbacks.filter(
                              (fb: Feedback) =>
                                fb.score !== undefined && fb.score !== null
                            ).length
                          ).toFixed(2)}
                        </span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
              <div>
                <h4 className="text-lg font-medium mb-3">Feedback History</h4>
                {selectedMember.feedbacks.length > 0 ? (
                  <div className="space-y-3">
                    {selectedMember.feedbacks.map((feedback: any) => (
                      <div
                        key={feedback.id}
                        className="bg-muted p-4 rounded-md"
                      >
                        <p>"{feedback.text}"</p>
                        <div className="mt-2 text-sm text-muted-foreground">
                          {feedback.from} -{" "}
                          {new Date(feedback.date).toLocaleDateString()}
                          {" | Score: "}
                          <span className="font-semibold">
                            {feedback.score}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">
                    No feedback recorded yet
                  </p>
                )}
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
