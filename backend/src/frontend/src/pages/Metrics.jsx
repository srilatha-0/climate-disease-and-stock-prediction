import { useState } from 'react';
import '../styles/metrics.css';

export default function Metrics() {
  const [timeRange, setTimeRange] = useState('week');
  
  const metricsData = {
    daily: {
      predictions: [145, 162, 158, 175, 189, 201, 198],
      accuracy: [84.2, 85.1, 86.3, 85.9, 86.7, 87.1, 86.8],
      responseTime: [1.2, 1.1, 1.3, 1.0, 1.1, 0.9, 1.0]
    }
  };

  return (
    <div className="metrics-page">
      <div className="metrics-header">
        <h1>System Metrics</h1>
        <div className="time-selector">
          <button className={timeRange === 'day' ? 'active' : ''} onClick={() => setTimeRange('day')}>Day</button>
          <button className={timeRange === 'week' ? 'active' : ''} onClick={() => setTimeRange('week')}>Week</button>
          <button className={timeRange === 'month' ? 'active' : ''} onClick={() => setTimeRange('month')}>Month</button>
        </div>
      </div>

      <div className="metrics-summary">
        <div className="summary-card">
          <div className="summary-icon">📊</div>
          <div className="summary-value">1,247</div>
          <div className="summary-label">Total Predictions</div>
          <div className="summary-trend">↑ +12%</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">🎯</div>
          <div className="summary-value">86.3%</div>
          <div className="summary-label">Avg Accuracy</div>
          <div className="summary-trend">↑ +2.1%</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">⚡</div>
          <div className="summary-value">1.2s</div>
          <div className="summary-label">Response Time</div>
          <div className="summary-trend">↓ -0.3s</div>
        </div>
        <div className="summary-card">
          <div className="summary-icon">✅</div>
          <div className="summary-value">99.8%</div>
          <div className="summary-label">Uptime</div>
          <div className="summary-trend">↑ +0.1%</div>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-chart">
          <h3>Daily Predictions</h3>
          <div className="chart-bars">
            {metricsData.daily.predictions.map((value, i) => (
              <div key={i} className="chart-bar-container">
                <div className="chart-bar" style={{ height: `${(value / 250) * 100}%` }}>
                  <span className="chart-value">{value}</span>
                </div>
                <div className="chart-label">Day {i + 1}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="metric-chart">
          <h3>Accuracy Trend</h3>
          <div className="chart-bars">
            {metricsData.daily.accuracy.map((value, i) => (
              <div key={i} className="chart-bar-container">
                <div className="chart-bar accuracy" style={{ height: `${value}%` }}>
                  <span className="chart-value">{value}%</span>
                </div>
                <div className="chart-label">Day {i + 1}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="metric-chart">
          <h3>Response Time (seconds)</h3>
          <div className="chart-bars">
            {metricsData.daily.responseTime.map((value, i) => (
              <div key={i} className="chart-bar-container">
                <div className="chart-bar response" style={{ height: `${(value / 2) * 100}%` }}>
                  <span className="chart-value">{value}s</span>
                </div>
                <div className="chart-label">Day {i + 1}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="metrics-table">
        <h3>Detailed Performance Log</h3>
        <table>
          <thead>
            <tr><th>Date</th><th>Predictions</th><th>Accuracy</th><th>Avg Response</th><th>Status</th></tr>
          </thead>
          <tbody>
            <tr><td>2024-01-15</td><td>198</td><td>86.8%</td><td>1.0s</td><td className="status-success">Optimal</td></tr>
            <tr><td>2024-01-14</td><td>201</td><td>87.1%</td><td>0.9s</td><td className="status-success">Optimal</td></tr>
            <tr><td>2024-01-13</td><td>189</td><td>86.7%</td><td>1.1s</td><td className="status-success">Optimal</td></tr>
            <tr><td>2024-01-12</td><td>175</td><td>85.9%</td><td>1.0s</td><td className="status-warning">Degraded</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}