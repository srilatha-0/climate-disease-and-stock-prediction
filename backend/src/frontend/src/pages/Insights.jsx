import { useState } from 'react';
import '../styles/insights.css';

export default function Insights() {
  const [selectedRegion, setSelectedRegion] = useState('global');
  
  const insights = {
    global: {
      trends: ['Temperature increasing by 0.5°C annually', 'Humidity levels rising in tropical zones', 'Rainfall patterns becoming unpredictable'],
      recommendations: ['Implement early warning systems', 'Adopt climate-resilient crops', 'Invest in water conservation'],
      riskZones: ['Southeast Asia', 'Central America', 'East Africa']
    }
  };

  return (
    <div className="insights-page">
      <div className="insights-header">
        <h1>Climate Insights & Analytics</h1>
        <p>Data-driven recommendations and trend analysis</p>
      </div>

      <div className="region-selector">
        <button className={selectedRegion === 'global' ? 'active' : ''} onClick={() => setSelectedRegion('global')}>Global</button>
        <button className={selectedRegion === 'asia' ? 'active' : ''} onClick={() => setSelectedRegion('asia')}>Asia Pacific</button>
        <button className={selectedRegion === 'europe' ? 'active' : ''} onClick={() => setSelectedRegion('europe')}>Europe</button>
        <button className={selectedRegion === 'americas' ? 'active' : ''} onClick={() => setSelectedRegion('americas')}>Americas</button>
      </div>

      <div className="insights-grid">
        <div className="insight-card">
          <div className="insight-icon">📈</div>
          <h3>Key Trends</h3>
          <ul>
            {insights.global.trends.map((trend, i) => (
              <li key={i}>{trend}</li>
            ))}
          </ul>
        </div>

        <div className="insight-card">
          <div className="insight-icon">💡</div>
          <h3>Recommendations</h3>
          <ul>
            {insights.global.recommendations.map((rec, i) => (
              <li key={i}>{rec}</li>
            ))}
          </ul>
        </div>

        <div className="insight-card">
          <div className="insight-icon">⚠️</div>
          <h3>High Risk Zones</h3>
          <ul>
            {insights.global.riskZones.map((zone, i) => (
              <li key={i}>{zone}</li>
            ))}
          </ul>
        </div>

        <div className="insight-card">
          <div className="insight-icon">📊</div>
          <h3>Market Impact</h3>
          <ul>
            <li>Agriculture stocks: ↓ 5%</li>
            <li>Renewable energy: ↑ 12%</li>
            <li>Insurance sector: ↓ 3%</li>
            <li>Water utilities: ↑ 8%</li>
          </ul>
        </div>
      </div>

      <div className="alert-section">
        <h2>Critical Alerts</h2>
        <div className="alert-list">
          <div className="alert critical">
            <span className="alert-icon">🚨</span>
            <div className="alert-content">
              <strong>High Flood Risk</strong>
              <p>Southeast Asia region expected to experience above-average rainfall</p>
            </div>
          </div>
          <div className="alert warning">
            <span className="alert-icon">⚠️</span>
            <div className="alert-content">
              <strong>Drought Warning</strong>
              <p>Water levels dropping below critical threshold in Central America</p>
            </div>
          </div>
          <div className="alert info">
            <span className="alert-icon">ℹ️</span>
            <div className="alert-content">
              <strong>Temperature Alert</strong>
              <p>Record high temperatures expected in Southern Europe next week</p>
            </div>
          </div>
        </div>
      </div>

      <div className="forecast-section">
        <h2>7-Day Forecast Summary</h2>
        <div className="forecast-grid">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, i) => (
            <div key={i} className="forecast-card">
              <div className="forecast-day">{day}</div>
              <div className="forecast-temp">{(22 + Math.random() * 10).toFixed(0)}°C</div>
              <div className="forecast-condition">
                {Math.random() > 0.7 ? '☀️' : Math.random() > 0.4 ? '⛅' : '🌧️'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}