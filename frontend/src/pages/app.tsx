import Header from "../components/home/Header"
import Navbar from "../components/home/Navbar"
import Footer from "../components/home/Footer"
import Aboutus from "../components/home/Aboutus"
import Lecturer from "../components/home/Lecturer"
export function App() {
  return <>
    <Navbar></Navbar>
    <Header></Header>
    <Lecturer></Lecturer>
    <Aboutus></Aboutus>
    <Footer></Footer>
  </>
}