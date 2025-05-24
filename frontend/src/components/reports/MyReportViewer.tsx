import { useEffect, useState } from "react";
import { getReportById, Report } from "../../data/reportData";
import { Card, CardContent } from "../ui/card";
import { Skeleton } from "../ui/skeleton";

interface MyReportViewerProps {
  taskId: string;
  reload?: number;
}

export default function MyReportViewer({ taskId, reload }: MyReportViewerProps) {
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    const reportId = localStorage.getItem(`report_id_${taskId}`);
    if (!reportId) {
      setReport(null);
      setLoading(false);
      return;
    }
    setLoading(true);
    getReportById(reportId)
      .then((data) => {
        setReport(data);
        setLoading(false);
      })
      .catch((err) => {
        setReport(null);
        setLoading(false);
        console.error("Lỗi gọi getReportById: ", err);
      });
  }, [taskId, reload]);

  if (loading) return <Skeleton className="w-full h-20" />;
  if (!report) return <p className="text-muted-foreground">Bạn chưa có báo cáo nào cho task này.</p>;

  return (
    <Card>
      <CardContent className="p-4">
        <p className="text-sm">{report.content}</p>
        <p className="text-xs text-muted-foreground mt-2">
          {report.student?.ho_ten || "Bạn"} – {new Date(report.created_at).toLocaleString()}
        </p>
      </CardContent>
    </Card>
  );
}
