import React from "react";
import Card from "./Card"; // Import the Card component 
import antony from "../../assets/antony.jpg"; // Import the image for the card
const AboutUs = () => {
  return (
    <div id="AboutUs" className="py-16 bg-gray-100 text-center">
      <h2 className="text-4xl font-bold text-blue-500 mb-6">About Us</h2>
      <p className="text-gray-600 max-w-2xl mx-auto mb-10">
        AntoniITSS
      </p>

      <div className="grid grid-cols-5 gap-6 max-w-7xl mx-auto">
        <Card image={antony} name="Nguyễn Đăng Bảo Lâm" role="BE Dev" description="Specialist in backend architecture and API development." />
        <Card image={antony} name="Nguyễn Ngọc Quân" role="BE Dev" description="Focused on security, performance, and scalability." />
        <Card image={antony} name="Vũ Quang Dũng" role="BE Dev" description="Expert in UI/UX and front-end frameworks." />
        <Card image={antony} name="Bùi Ngọc Hợp" role="FE Dev" description="Dedicated to modern web technologies and performance optimization." />
        <Card image={antony} name="Phạm Gia Khiêm" role="FE Dev" description="Passionate about responsive design and user experience." />
      </div>
    </div>
  );
};

export default AboutUs;
