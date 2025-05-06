import React from "react";
import { FaFacebookF, FaInstagram, FaTwitter, FaYoutube } from "react-icons/fa";

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-6 px-6">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center">
        <div className="text-center md:text-left mb-6 md:mb-0">
          <h2 className="text-3xl font-bold text-red-500">Bao Lam</h2>
          <p className="text-gray-400 mt-2">
            may thang ngu ba bay 
          </p>
        </div>

        <div className="flex space-x-6 text-gray-300 text-sm">
          <a href="/" className="hover:text-red-500 transition duration-200">
            Home
          </a>
          <a href="#AboutUs" className="hover:text-red-500 transition duration-200">
            About Us
          </a>
          <a href="#services" className="hover:text-red-500 transition duration-200">
            Services
          </a>
          <a href="#contact" className="hover:text-red-500 transition duration-200">
            Contact
          </a>
        </div>

        <div className="flex space-x-4 mt-6 md:mt-0">
          <a href="#" className="text-gray-400 hover:text-red-500 transition duration-200">
            <FaFacebookF size={20} />
          </a>
          <a href="#" className="text-gray-400 hover:text-red-500 transition duration-200">
            <FaInstagram size={20} />
          </a>
          <a href="#" className="text-gray-400 hover:text-red-500 transition duration-200">
            <FaTwitter size={20} />
          </a>
          <a href="#" className="text-gray-400 hover:text-red-500 transition duration-200">
            <FaYoutube size={20} />
          </a>
        </div>
      </div>

      <div className="text-center text-gray-500 text-sm mt-8">
        &copy; {new Date().getFullYear()} Bao Lam Ngu. All rights reserved.
      </div>
    </footer>
  );
};

export default Footer;
