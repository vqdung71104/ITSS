import { useEffect, useRef, useState } from "react";
import axiosInstance from "../../axios-config";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { toast } from "sonner";
import { Download } from "lucide-react";

export default function TaskFileTab({ taskId }: { taskId: string }) {
  const [files, setFiles] = useState<{ filename: string; uploaded_at: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const res = await axiosInstance.get(`/upload/tasks/${taskId}/list-files/`);
      setFiles(res.data.files || []);
    } catch (err) {
      setFiles([]);
      toast.error("Failed to load files");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (taskId) fetchFiles();
    // eslint-disable-next-line
  }, [taskId]);

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!fileInputRef.current?.files?.[0]) return;
    const file = fileInputRef.current.files[0];
    const formData = new FormData();
    formData.append("file", file);
    setLoading(true);
    try {
      await axiosInstance.post(`/upload/tasks/${taskId}/upload-file/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success("File uploaded successfully");
      fetchFiles();
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) {
      toast.error("Failed to upload file");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (filename: string) => {
    try {
      const res = await axiosInstance.get(
        `/upload/tasks/${taskId}/download-file/${filename}`,
        { responseType: "blob" }
      );
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      toast.error("Failed to download file");
    }
  };

  return (
    <div>
      <form onSubmit={handleUpload} className="flex gap-2 mb-4">
        <Input
          type="file"
          ref={fileInputRef}
          className="w-auto"
          disabled={loading}
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Uploading..." : "Upload"}
        </Button>
      </form>
      <div>
        <h3 className="font-semibold mb-2">Files</h3>
        {files.length === 0 ? (
          <p className="text-muted-foreground">No files uploaded for this task.</p>
        ) : (
          <ul className="space-y-2">
            {files.map((file) => (
              <li
                key={file.filename}
                className="flex items-center justify-between border rounded px-3 py-2"
              >
                <span>
                  <span className="font-medium">{file.filename}</span>
                  <span className="ml-2 text-xs text-muted-foreground">
                    {file.uploaded_at}
                  </span>
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleDownload(file.filename)}
                  className="ml-2"
                >
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </Button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}