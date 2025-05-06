import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import axiosInstance from "../../axios-config"; // Import axios instance
const Login = ({ onClose }: any) => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);
  const [error, setError] = useState(""); // State for error message
  const [username, setUsername] = useState(""); // State for email input
  const [password, setPassword] = useState(""); // State for password input

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => {
      onClose();
    }, 300);
  };
  // Function to handle navigation to register
  const goToRegister = () => {
    handleClose();
    navigate("/register");
  };
  const handleLogin = async () => {
    try {
      // Gửi yêu cầu POST đến API /users/login
      console.log(
        "Logging in with email:",
        username,
        "and password:",
        password
      );
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);
      console.log("Form Data:", formData);
      const response = await axiosInstance.post("/users/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      console.log("Response:", response);
      // Kiểm tra phản hồi từ server
      if (response.status === 200) {
        // Lưu token hoặc thực hiện hành động sau khi đăng nhập thành công
        console.log("Login successful:", response.data);
        // Ví dụ: Lưu token vào localStorage
        localStorage.setItem("token", response.data.token);
        // Điều hướng đến trang chính
        navigate("/dashboard");
      }
    } catch (error: any) {
      // Xử lý lỗi và hiển thị thông báo
      if (
        error.response &&
        error.response.data &&
        error.response.data.message
      ) {
        setError(error.response.data.message);
      } else {
        setError("An error occurred. Please try again.");
      }
    }
  };

  return (
    <div
      className={`fixed inset-0 flex items-center justify-center bg-black/70 z-50 transition-opacity duration-500 ${
        isVisible ? "opacity-100" : "opacity-0"
      }`}
      onClick={(e) => e.target === e.currentTarget && handleClose()}
    >
      <div
        className={`bg-white p-6 rounded-lg shadow-lg w-96 relative transform transition-transform duration-500 ${
          isVisible ? "translate-y-0" : "translate-y-[-20px]"
        }`}
      >
        {/* Nút Close (X) */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-blue-500 text-xl font-bold transition duration-200"
        >
          X
        </button>

        {/* Title */}
        <h2 className="text-2xl font-bold text-center text-blue-500">Login</h2>

        {/* Input Email */}
        <input
          type="email"
          placeholder="Email"
          className="w-full mt-4 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={username}
          onChange={(e) => {
            setUsername(e.target.value);
            setError("");
          }} // Update email state on change
        />

        {/* Input Password */}
        <input
          type="password"
          placeholder="Password"
          className="w-full mt-4 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={password}
          onChange={(e) => {
            setPassword(e.target.value);
            setError("");
          }}
        />

        {/* Login Button */}
        <button
          className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg mt-6 hover:bg-blue-600 transition duration-200"
          onClick={handleLogin} // Call handleLogin on button click
        >
          Login
        </button>

        {error && <div className="text-blue-500 text-left mt-2">{error}</div>}

        <p className="mt-4 text-center text-gray-600">
          You don't have an account?{" "}
          <button
            onClick={goToRegister}
            className="text-blue-500 font-semibold hover:underline"
          >
            Create Account
          </button>
        </p>
        {/* Forgot Password Link */}
        <p className="mt-2 text-center text-gray-600">
          Forgot your password?{" "}
          <Link
            to="/forgot-password"
            className="text-blue-500 font-semibold hover:underline"
          >
            Reset Password
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Login;
