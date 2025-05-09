const Slidebar = () => {
  return (
    <div className="fixed top-0 left-0 w-64 h-full bg-blue-800 text-white">
      <div className="flex items-center justify-center h-16">
        <h1 className="text-2xl font-bold">Slidebar</h1>
      </div>
      <nav className="mt-10">
        <ul>
          <li className="px-4 py-2 hover:bg-blue-700">
            <a href="#">Dashboard</a>
          </li>
          <li className="px-4 py-2 hover:bg-blue-700">
            <a href="#">Settings</a>
          </li>
          <li className="px-4 py-2 hover:bg-blue-700">
            <a href="#">Profile</a>
          </li>
        </ul>
      </nav>
    </div>
  );
};
export default Slidebar;
