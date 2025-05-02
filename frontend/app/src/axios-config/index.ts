// File này chứa cấu hình cho Axios, bao gồm base URL, timeout, và các interceptor cho request và response.
import axios, { AxiosInstance,  AxiosResponse } from 'axios';

// Định nghĩa base URL (thay thế bằng URL API của bạn)
const BASE_URL = 'http://localhost:8000'; // Ví dụ: API backend của bạn

// Tạo một instance Axios
const axiosInstance: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000, // Thời gian chờ tối đa (10 giây)`
  withCredentials: true, // Nếu bạn cần gửi cookie cùng với request
  headers: {
    'Content-Type': 'application/json',
    // Bạn có thể thêm các header khác nếu cần
    // 'Authorization': `Bearer ${yourToken}, // Ví dụ: Nếu cần token
    'Authorization' : `Bearer ${localStorage.getItem('token')}`, // Lấy token từ localStorage
  },
});

// Interceptor cho request (xử lý trước khi gửi request)
axiosInstance.interceptors.request.use(
  (config: any) => {
    // Thêm logic trước khi gửi request (ví dụ: thêm token vào header)
    const token = localStorage.getItem('token'); // Lấy token từ localStorage (nếu có)
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // Xử lý lỗi khi gửi request
    return Promise.reject(error);
  }
);

// Interceptor cho response (xử lý sau khi nhận response)
axiosInstance.interceptors.response.use(
  (response: AxiosResponse) => {
    // Xử lý response thành công
    return response;
  },
  (error) => {
    // Xử lý lỗi khi nhận response
    if (error.response) {
      // Xử lý lỗi dựa trên status code
      switch (error.response.status) {
        case 401:
          console.error('Unauthorized! Redirecting to login...');
          // Ví dụ: Chuyển hướng đến trang login
          window.location.href = '/login';
          break;
        case 403:
          console.error('Forbidden! You do not have access.');
          break;
        case 500:
          console.error('Server error! Please try again later.');
          break;
        default:
          console.error('An error occurred:', error.response.data);
      }
    } else if (error.request) {
      // Không nhận được phản hồi từ server
      console.error('No response received:', error.request);
    } else {
      // Lỗi khác
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// Export instance để sử dụng trong các file khác
export default axiosInstance;