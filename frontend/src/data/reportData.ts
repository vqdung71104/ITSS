import axiosInstance from "../axios-config";

export interface Report {
  id: string;
  content: string;
  task: { id: string; title: string }; // Phù hợp với trả về backend
  created_at: string;
  student?: { id: string; ho_ten: string };
}

// Tạo report và trả về report vừa tạo
export const createReport = async (data: {
  content: string;
  task_id: string;
}): Promise<Report> => {
  const response = await axiosInstance.post("/reports/", data);
  return response.data;
};

// Lấy report theo ID (dùng cho sinh viên tự xem)
export const getReportById = async (reportId: string): Promise<Report | null> => {
  try {
    const response = await axiosInstance.get(`/reports/${reportId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching report by ID:", error);
    return null;
  }
};
