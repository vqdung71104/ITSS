import React from "react";

const Card = ({ image , name, role, description } : any) => {
  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden transform transition duration-300 hover:scale-105 hover:shadow-2xl">
      <img src={image} alt={name} className="w-full h-40 object-cover" />
      <div className="p-4 text-center">
        <h3 className="text-lg font-bold text-gray-900">{name}</h3>
        <p className="text-blue-500 font-medium">{role}</p>
        <p className="text-gray-600 mt-2 text-sm">{description}</p>
      </div>
    </div>
  );
};

export default Card;
