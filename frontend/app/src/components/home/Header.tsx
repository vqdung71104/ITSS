import React from "react";
import headerImage from "../../assets/Header.png";

const Header = () => {
  return (
    <div
      className="relative w-full h-screen bg-cover bg-center flex items-center justify-center text-white"
      style={{ backgroundImage: `url(${headerImage})`, opacity: 0.8 }}
    >
      <div className="absolute inset-0 bg-gradient-to-b from-black/50 to-transparent"></div>

      <div className="relative text-center max-w-2xl px-6">
        <h2 className="text-5xl md:text-7xl font-bold uppercase tracking-wide text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.2)]">
          ITSS
        </h2>
        <h2 className="text-4xl md:text-6xl font-bold mt-4 text-white drop-shadow-[0_2px_4px_rgba(0,0,0,0.2)]">
          Hệ Thống Quản lý Nhóm Bài Tập Lớn trong Môn Học
        </h2>

        <button className="mt-8 px-8 py-4 bg-blue-500 rounded-full text-xl font-semibold hover:bg-red-600 transition duration-300 shadow-lg">
          Learn More
        </button>
      </div>
    </div>
  );
};

export default Header;
