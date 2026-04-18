import { useState } from "react";
import "../styles/prediction.css";

export default function Prediction() {

  // =========================
  // 🌍 DISEASE MODEL
  // =========================
  const [formData, setFormData] = useState({
    temp: 30,
    rain: 80,
    humidity: 70,
    month: 4,
    dengue_cases: 120
  });

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  // =========================
  // 📈 STOCK MODEL
  // =========================
  const [stockData, setStockData] = useState({
    stock: "AALR3",
    temp: 30,
    rain: 80,
    humidity: 70,
    month: 4,
    dengue_cases: 120
  });

  const [stockResult, setStockResult] = useState(null);
  const [stockLoading, setStockLoading] = useState(false);

  // =========================
  // INPUT CHANGE (DISEASE)
  // =========================
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: Number(value)
    }));
  };

  // =========================
  // INPUT CHANGE (STOCK)
  // =========================
  const handleStockChange = (e) => {
    const { name, value } = e.target;

    setStockData((prev) => ({
      ...prev,
      [name]: name === "stock" ? value : Number(value)
    }));
  };

  // =========================
  // DISEASE PREDICT
  // =========================
  const handlePredict = async () => {
    setLoading(true);
    setData(null);

    try {
      const res = await fetch("http://127.0.0.1:5000/predict-global", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      const result = await res.json();
      setData(result);

    } catch {
      setData({ error: "Backend error" });
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // STOCK PREDICT
  // =========================
  const handleStockPredict = async () => {
    setStockLoading(true);
    setStockResult(null);

    try {
      const res = await fetch("http://127.0.0.1:5000/predict-stock", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(stockData),
      });

      const result = await res.json();
      setStockResult(result);

    } catch {
      setStockResult({ error: "Stock API error" });
    } finally {
      setStockLoading(false);
    }
  };

  // =========================
  // ✅ FIXED INPUT COMPONENT
  // =========================
  const InputControl = ({ label, name, min, max, data, onChange }) => (
    <div className="control-box">
      <div className="label-row">
        <span>{label}</span>

        <input
          type="number"
          className="number-input"
          name={name}
          value={data[name]}
          onChange={onChange}
        />
      </div>

      <input
        type="range"
        name={name}
        min={min}
        max={max}
        value={data[name]}
        onChange={onChange}
      />
    </div>
  );

  return (
    <div className="dashboard">

      <h1>🌍 Dengue prediction model</h1>
      <p>AI-powered disease outbreak + stock prediction dashboard</p>

      {/* =========================
          🌍 DISEASE SECTION
      ========================= */}
      <div className="input-box">

        <InputControl label="Temperature" name="temp" min={0} max={50} data={formData} onChange={handleChange} />
        <InputControl label="Rainfall" name="rain" min={0} max={300} data={formData} onChange={handleChange} />
        <InputControl label="Humidity" name="humidity" min={0} max={100} data={formData} onChange={handleChange} />
        <InputControl label="Month" name="month" min={1} max={12} data={formData} onChange={handleChange} />

      </div>

      <button onClick={handlePredict} disabled={loading}>
        {loading ? "Running..." : "Predict Outbreak"}
      </button>

      {/* DISEASE RESULT */}
      {data && !data.error && (
        <div className="results">

          <div className="card highlight">
            <h2>🌍 Dengue Outbreak Prediction</h2>

            <h1>
              {((data.prediction || 0) * 100).toFixed(2)}%
            </h1>

            <h3>
              {data.risk_level === "High"
                ? "🚨 High Risk"
                : data.risk_level === "Medium"
                  ? "⚠️ Medium Risk"
                  : "✅ Low Risk"}
            </h3>
          </div>

          <div className="card">
            <h2>📊 Key Factors</h2>

            {data.feature_importance &&
              Object.entries(data.feature_importance)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 5)
                .map(([key, value]) => (
                  <div className="bar-row" key={key}>
                    <span>{key}</span>
                    <div className="bar">
                      <div className="fill" style={{ width: `${value * 100}%` }} />
                    </div>
                    <span>{(value * 100).toFixed(1)}%</span>
                  </div>
                ))}
          </div>

          <div className="card">
            <h2>📅 Seasonal Pattern</h2>

            {data.seasonality &&
              Object.entries(data.seasonality).map(([month, value]) => (
                <div className="bar-row" key={month}>
                  <span>{month}</span>
                  <div className="bar">
                    <div className="fill season" style={{ width: `${value * 100}%` }} />
                  </div>
                  <span>{(value * 100).toFixed(1)}%</span>
                </div>
              ))}
          </div>

        </div>
      )}

      {data?.error && (
        <p style={{ color: "red", textAlign: "center" }}>{data.error}</p>
      )}

      {/* =========================
          📈 STOCK SECTION
      ========================= */}
      <br /><br /><br />
      <h1>📈 Stock prediction model</h1>

      <div className="input-box" style={{ marginTop: "40px" }}>

        <div className="control-box">
          <div className="label-row">
            <span>Stock</span>
            <select name="stock" value={stockData.stock} onChange={handleStockChange}>
              <option value="AALR3">AALR3</option>
              <option value="FLRY3">FLRY3</option>
              <option value="HYPE3">HYPE3</option>
              <option value="ODPV3">ODPV3</option>
              <option value="RADL3">RADL3</option>
            </select>
          </div>
        </div>

        <InputControl label="Temp" name="temp" min={0} max={50} data={stockData} onChange={handleStockChange} />
        <InputControl label="Rain" name="rain" min={0} max={300} data={stockData} onChange={handleStockChange} />
        <InputControl label="Humidity" name="humidity" min={0} max={100} data={stockData} onChange={handleStockChange} />
        <InputControl label="Month" name="month" min={1} max={12} data={stockData} onChange={handleStockChange} />

      </div>

      <button onClick={handleStockPredict} disabled={stockLoading}>
        {stockLoading ? "Predicting..." : "Predict Stock"}
      </button>

      {/* STOCK RESULT */}
      {stockResult && !stockResult.error && (
        <div className="results">
          <div className="card highlight">
            <h2>📈 {stockResult.stock}</h2>
            <h1>{(stockResult.probability * 100).toFixed(2)}%</h1>
            <h3>{stockResult.prediction === 1 ? "📈 UP" : "📉 DOWN"}</h3>
          </div>
        </div>
      )}

      {stockResult?.error && (
        <p style={{ color: "red", textAlign: "center" }}>
          {stockResult.error}
        </p>
      )}

    </div>
  );
}