import { motion } from "framer-motion";
import antony from "../../assets/antony.jpg";

const Lecturer = () => {
  const lectuer = [antony]; // Replace with actual course images

  return (
    <div className="py-16 text-center bg-gray-100" id="Lecturer">
      <h2 className="text-4xl font-bold text-blue-500 mb-6">Lecturer</h2>
      <p className="text-gray-600 max-w-2xl mx-auto mb-10">
        Nguyen Manh Tuan
      </p>

      <div className="flex gap-6 justify-center flex-wrap">
        {lectuer.map((course, index) => (
          <motion.div
            key={index}
            className="relative w-60 h-60 rounded-lg overflow-hidden shadow-lg"
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.2 }}
            viewport={{ once: false }}
          >
            <img
              src={course}
              alt={`Course ${index + 1}`}
              className="w-full h-full object-cover transition hover:brightness-110"
            />
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default Lecturer;
