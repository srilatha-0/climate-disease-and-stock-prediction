import { useState, useEffect } from 'react';
import '../styles/home.css';

export default function Home() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="home-container">

      {/* =========================
          HERO SECTION
      ========================= */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Dengue + Stock Prediction System

          </h1>

          <p className="hero-description">
            This system uses machine learning to predict dengue outbreak risk from climate data 
            and analyzes how those outbreaks influence healthcare stock movements.
          </p>
        </div>
      </div>

      {/* =========================
          FEATURES SECTION
      ========================= */}
      <div className="features-section">
        <h2 className="section-title">Key Features</h2>

        <div className="features-grid">

          <div className="feature-card">
            <div className="feature-icon">🦠</div>
            <h3>Dengue Prediction Model</h3>
            <p>
              Built using climate variables like temperature, rainfall, and humidity 
              with lag features and seasonal encoding to detect outbreak patterns.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📈</div>
            <h3>Stock Prediction Model</h3>
            <p>
              Weekly stock returns are predicted using dengue spikes and climate signals, 
              helping identify market reactions to health events.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Performance Analysis</h3>
            <p>
              Models are evaluated using accuracy, precision, recall, F1-score, AUC, 
              and confusion matrix for reliable comparison.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🧠</div>
            <h3>Explainable AI</h3>
            <p>
              Feature importance and SHAP values are used to understand which factors 
              influence predictions the most.
            </p>
          </div>

        </div>
      </div>

      {/* =========================
          INFO SECTION
      ========================= */}
      <div className="info-section">

        <div className="info-card">
          <h3>How It Works</h3>
          <ol>
            <li>Climate data is collected and converted into weekly format</li>
            <li>Dengue spikes are identified using rolling mean + standard deviation</li>
            <li>Monthly outbreak signals are mapped into weekly timelines</li>
            <li>Stock data is converted into weekly returns and aligned with dengue data</li>
            <li>Machine learning models learn relationships between climate, disease, and stock trends</li>
          </ol>
        </div>

        <div className="info-card">
          <h3>System Status</h3>

          <div className="current-time">
            <span>🕐</span>
            <span>{currentTime.toLocaleTimeString()}</span>
          </div>

          <div className="current-date">
            <span>📅</span>
            <span>{currentTime.toLocaleDateString()}</span>
          </div>

          <div className="system-status">
            <span>✅</span>
            <span>Model 1: Stock Prediction Active</span>
          </div>

          <div className="system-status">
            <span>✅</span>
            <span>Model 2: Dengue Risk Prediction Active</span>
          </div>
        </div>

      </div>

    </div>
  );
}