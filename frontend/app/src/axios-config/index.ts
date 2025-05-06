import axios from "axios";

const axiosInstance = axios.create({
  baseURL: "http://localhost:8000", // Thay bằng URL API của bạn
  withCredentials: true, // Cho phép gửi cookie cùng với yêu cầu
  headers: {
    "Content-Type": "application/json",
  },
});

export default axiosInstance;