import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000', // đổi theo API của bạn
  withCredentials: true, // quan trọng!
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;