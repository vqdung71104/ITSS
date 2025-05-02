import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import axios from "axios";

const Register = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    dateOfBirth: "",
    phoneNumber: "",
    role: "",
    specialization: "",
    department: "",
  });

  const API_PATH = import.meta.env.VITE_API_PATH;

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
    setError("");
  };

  const handleRegister = async () => {
    // Validate form data
    if (
      !formData.email ||
      !formData.password ||
      !formData.confirmPassword ||
      !formData.phoneNumber ||
      !formData.firstName ||
      !formData.lastName ||
      !formData.dateOfBirth ||
      !formData.role
    ) {
      setError("Please fill all required fields");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters long");
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if(!/^0[0-9]{9}$/.test(formData.phoneNumber)){
      setError("Phone number must start with 0 and be exactly 10 digits.")
      return;
    }

    // Validate role-specific fields
    const roleValue = parseInt(formData.role);

    if (roleValue === 2 && !formData.specialization) {
      // Trainer
      setError("Specialization is required for Trainer role");
      return;
    }

    try {
      setLoading(true);

      // Prepare request payload based on backend requirements
      const requestData = {
        email: formData.email,
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        firstName: formData.firstName,
        lastName: formData.lastName,
        dateOfBirth: formData.dateOfBirth,
        phoneNumber: formData.phoneNumber,
        role: roleValue,
      };

      // Add role-specific fields based on the selected role
      if (roleValue === 2) {
        // Trainer
        requestData.specialization = parseInt(formData.specialization);
      }

      // Send registration request to the API
      console.log(requestData)
      const response = await axios.post(
        `${API_PATH}/Auth/register`,
        requestData
      );

      // After successful registration, navigate to activate account page
      if (response) {
        navigate("/activate-account", {
          state: {
            email: formData.email,
            password: formData.password,
          },
        });
      }
    } catch (err) {
      // Handle errors from the API
      if (err.response && err.response.data) {
        if (err.response.data.message) {
          setError(err.response.data.message);
        } else if (err.response.data.error) {
          setError(err.response.data.error);
        } else {
          setError("Registration failed. Please try again.");
        }
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle navigation to login page
  const goToLogin = () => {
    navigate("/login");
  };

  // Show/hide role-specific fields based on selected role  
  const roleValue = parseInt(formData.role);
  const showSpecialization = roleValue === 2; // Trainer

  return (
    <div className="min-h-screen  flex items-center justify-center bg-gray-100">
      <div
        className={`bg-white p-8 rounded-lg shadow-lg w-20 max-w-sm mx-auto max-h-screen overflow-y-auto transform transition-transform duration-500 ${
          isVisible ? "translate-y-0" : "translate-y-[-20px]"
        }`}
      >
        {/* Title */}
        <h2 className="text-2xl font-bold text-center text-red-500 mb-6">
          Create Account
        </h2>

        {/* Email */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            name="email"
            placeholder="Email"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          {/* Password */}
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-1">
              Password <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              name="password"
              placeholder="Password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              value={formData.password}
              onChange={handleChange}
              required
            />
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-1">
              Confirm <span className="text-red-500">*</span>
            </label>
            <input
              type="password"
              name="confirmPassword"
              placeholder="Confirm Password"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        {/* Name fields */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {/* First Name */}
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-1">
              First Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="firstName"
              placeholder="First Name"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              value={formData.firstName}
              onChange={handleChange}
              required
            />
          </div>

          {/* Last Name */}
          <div>
            <label className="block text-gray-700 text-sm font-bold mb-1">
              Last Name <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="lastName"
              placeholder="Last Name"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              value={formData.lastName}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        {/* Date of Birth */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-1">
            Date of Birth <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            name="dateOfBirth"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            value={formData.dateOfBirth}
            onChange={handleChange}
            required
          />
        </div>

        {/* Phone Number */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-1">
            Phone Number <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="phoneNumber"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            placeholder="Phone Number"
            value={formData.phoneNumber}
            onChange={handleChange}
            required
          />
        </div>

        {/* Role */}
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-1">
            Role <span className="text-red-500">*</span>
          </label>
          <select
            name="role"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
            value={formData.role}
            onChange={handleChange}
            required
          >
            <option value="">Select a role</option>
            <option value="2">Trainer</option>
            <option value="3">Member</option>
          </select>
        </div>

        {/* Specialization - only for Trainer */}
        {showSpecialization && (
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-1">
              Specialization <span className="text-red-500">*</span>
            </label>
            <select
              name="specialization"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
              value={formData.specialization}
              onChange={handleChange}
              required
            >
              <option value="">Select a specialization</option>
              <option value="1">Cardio</option>
              <option value="2">Strength</option>
              <option value="3">CrossFit</option>
              <option value="4">Yoga</option>
              <option value="5">Pilates</option>
              <option value="6">Boxing</option>
              <option value="7">Spinning</option>
              <option value="8">Functional</option>
              <option value="9">Dance</option>
              <option value="10">PersonalTraining</option>
              <option value="11">Recovery</option>
              <option value="12">Multipurpose</option>
            </select>
          </div>
        )}

        {/* Display error message */}
        {error && <div className="text-red-500 text-left mt-4">{error}</div>}

        {/* Register Button */}
        <button
          className={`w-full bg-red-500 text-white px-4 py-2 rounded-lg mt-4 hover:bg-red-600 transition duration-200 ${
            loading ? "opacity-70 cursor-not-allowed" : ""
          }`}
          onClick={handleRegister}
          disabled={loading}
        >
          {loading ? "Processing..." : "Create Account"}
        </button>

        {/* Login Link */}
        <p className="mt-4 text-center text-gray-600">
          Already have an account?{" "}
          <button
            onClick={goToLogin}
            className="text-red-500 font-semibold hover:underline"
          >
            Login
          </button>
        </p>
      </div>
    </div>
  );
};

export default Register;
