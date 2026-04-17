import { useState } from "react";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Prediction from "./pages/Prediction";
import Metrics from "./pages/Metrics";
import Insights from "./pages/Insights";
import Performance from "./pages/Performance"; // Fixed import (was pointing to Prediction)
import "./styles/global.css";

export default function App() {
  const [tab, setTab] = useState("home");

  return (
    <>
      <Navbar activeTab={tab} setActiveTab={setTab} /> {/* Pass props to Navbar */}
      
      <div className="content">
        {tab === "home" && <Home />}
        {tab === "prediction" && <Prediction />}
        {tab === "metrics" && <Metrics />}
        {tab === "insights" && <Insights />}
        {tab === "performance" && <Performance />}
      </div>
    </>
  );
}