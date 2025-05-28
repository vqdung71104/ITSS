import { useState } from "react";
import { Button } from "../ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../ui/dialog";
import { Input } from "../ui/input";
import { toast } from "sonner";
import axiosInstance from "../../axios-config";

export function EvaluationButton({
  studentId,
  projectId,
}: {
  studentId: string;
  projectId: string;
}) {
  const [open, setOpen] = useState(false);
  const [score, setScore] = useState<number>(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axiosInstance.post("/evaluations/", {
        student_id: studentId,
        project_id: projectId,
        score,
        comment,
      });
      toast.success("Evaluation submitted!");
      setOpen(false);
      setScore(0);
      setComment("");
    } catch (err) {
      toast.error("Failed to submit evaluation");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        className="ml-2 bg-academe-500 hover:bg-academe-600 text-white border-0 shadow-sm"
        onClick={() => setOpen(true)}
        type="button"
      >
        + Create Evaluation
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Evaluation</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Score</label>
              <Input
                type="number"
                min={0}
                max={10}
                value={score}
                onChange={(e) => setScore(Number(e.target.value))}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Comment</label>
              <Input
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Enter evaluation comment"
                required
              />
            </div>
            <div className="flex justify-end">
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
    </>
  );
}
