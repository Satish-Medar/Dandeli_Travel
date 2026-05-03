import Navbar from "../../components/Navbar";
import Footer from "../../components/Footer";

export default function MarketingLayout({ children }) {
  return (
    <div className="marketing-layout">
      <Navbar />
      <main className="marketing-main">
        {children}
      </main>
      <Footer />
    </div>
  );
}
