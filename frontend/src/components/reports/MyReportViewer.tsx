import { useEffect, useState } from "react";
import { getAllReports, Report } from "../../data/reportData";
import { Card, CardContent } from "../ui/card";
import { Skeleton } from "../ui/skeleton";

interface MyReportViewerProps {
  taskId: string;
  reload?: number;
}

export default function MyReportViewer({
  taskId,
  reload,
}: MyReportViewerProps) {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!taskId) return;
    setLoading(true);
    getAllReports()
      .then((allReports) => {
        // Lọc các report theo taskId
        const filtered = allReports.filter(
          (r) =>
            r.task && r.task.id && r.task.id.toString() === taskId.toString()
        );
        setReports(filtered);
        setLoading(false);
      })
      .catch((err) => {
        setReports([]);
        setLoading(false);
        console.error("Lỗi gọi getAllReports: ", err);
      });
  }, [taskId, reload]);

  if (loading) return <Skeleton className="w-full h-20" />;

  if (!reports.length)
    return (
      <div className="p-4 text-center text-muted-foreground">
        Bạn chưa có báo cáo nào cho task này.
      </div>
    );

  return (
    <div className="space-y-4">
      {reports.map((report) => (
        <Card key={report.id} className="border-academe-200 shadow-sm">
          <CardContent className="p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-base text-academe-600">
                {report.title}
              </span>
              <span className="text-xs text-muted-foreground">
                {new Date(report.created_at).toLocaleString()}
              </span>
            </div>
            <div>
              <span className="font-semibold text-base text-academe-600 mr-2">
                Content:
              </span>
              <span className="text-sm text-gray-700">{report.content}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
