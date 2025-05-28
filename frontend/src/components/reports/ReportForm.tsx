import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../ui/dialog";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from "../ui/form";
import { toast } from "sonner";
import { createReport } from "../../data/reportData";

const schema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  content: z.string().min(5, "Content must be at least 5 characters"),
});

type ReportFormValues = z.infer<typeof schema>;

interface ReportFormProps {
  taskId: string;
  onReportCreated?: () => void;
}

export default function ReportForm({
  taskId,
  onReportCreated,
}: ReportFormProps) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const form = useForm<ReportFormValues>({
    resolver: zodResolver(schema),
    defaultValues: { title: "", content: "" },
  });

  const handleSubmit = async (data: ReportFormValues) => {
    setLoading(true);
    try {
      // Tạo report
      const report = await createReport({
        title: data.title,
        content: data.content,
        task_id: taskId,
      });
      // Lưu report_id vào localStorage
      if (report && report.id) {
        localStorage.setItem(`report_id_${taskId}`, report.id);
        onReportCreated && onReportCreated(); // Đảm bảo gọi lại hàm reload
      }
      toast.success("Report created");
      onReportCreated && onReportCreated();
      setOpen(false);
    } catch (err) {
      toast.error("Failed to create report");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-academe-500 hover:bg-academe-600 text-white border-0 shadow-sm">
          + Create Report
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create Report</DialogTitle>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(handleSubmit)}
            className="space-y-4"
          >
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="report-title">Report Title</FormLabel>
                  <FormControl>
                    <Input
                      id="report-title"
                      autoComplete="off"
                      placeholder="Enter report title"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="content"
              render={({ field }) => (
                <FormItem>
                  <FormLabel htmlFor="report-content">Report Content</FormLabel>
                  <FormControl>
                    <Input
                      id="report-content"
                      autoComplete="off"
                      placeholder="Enter your report"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="flex justify-end">
              <Button type="submit" disabled={loading}>
                {loading ? "Submitting..." : "Submit Report"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
