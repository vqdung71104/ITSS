import { Link } from "react-router-dom";
import logo from "../../assets/icon.png";
import { useState } from "react";
import Login from "./Login"; // Import the Login component

const Navbar = () => {
  const [menu, setMenu] = useState("Home");
  const [showLogin, setShowLogin] = useState(false); 

  const scrollToSection = (sectionId : any) => {
    const section = document.getElementById(sectionId);
    if (section) {
      section.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <>
      <nav className="bg-blue-400 text-white py-4 px-6 flex justify-between items-center shadow-lg sticky top-0 z-10">
        {/* Logo */}
        <Link to="/">
          <img src={logo} alt="logo" className="h-10 w-auto scale-200" /> 
        </Link>

        {/* Menu Items */}
        <ul className="flex space-x-6 text-lg font-semibold">
          {["Home", "Lecturer", "Group", "AboutUs"].map((item) => (
            <li key={item}>
              <Link
                to={item === "Home" ? "/" : `#${item}`}
                className={`hover:text-gray-200 transition duration-200 relative ${
                  menu === item ? "text-gray-200" : ""
                }`}
                onClick={() => {
                  setMenu(item);
                  scrollToSection(item);
                }}
              >
                {item === "AboutUs" ? "About Us" : item}

                {menu === item && (
                  <span className="absolute left-0 bottom-[-4px] w-full h-1 bg-white rounded-lg"></span>
                )}
              </Link>
            </li>
          ))}
        </ul>

        {/* Login Button */}
        <div>
          <button
            onClick={() => setShowLogin(true)}
            className="bg-white text-blue-500 px-4 py-2 rounded-lg font-semibold hover:bg-gray-100 transition duration-200"
          >
            Login
          </button>
        </div>
      </nav>

      {/* Hiển thị Login Component khi click vào nút Login */}
      {showLogin && <Login onClose={() => setShowLogin(false)} />}
    </>
  );
};

export default Navbar;
