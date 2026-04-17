import { useState } from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'home', name: 'Home', icon: '🏠' },
    { id: 'prediction', name: 'Prediction', icon: '🔮' },
    { id: 'performance', name: 'Performance', icon: '📊' },
    { id: 'metrics', name: 'Metrics', icon: '📈' },
    { id: 'insights', name: 'Insights', icon: '💡' }
  ];

  return (
    <nav style={{
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '1rem 2rem',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          fontSize: '1.5rem',
          fontWeight: 'bold',
          color: 'white'
        }}>
          <span style={{ fontSize: '2rem' }}>🌍</span>
          <span>ClimateAI System</span>
        </div>

        <div style={{
          display: 'flex',
          gap: '0.5rem',
          flexWrap: 'wrap'
        }}>
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '0.6rem 1.2rem',
                background: activeTab === tab.id ? 'white' : 'rgba(255,255,255,0.2)',
                color: activeTab === tab.id ? '#667eea' : 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                transition: 'all 0.3s ease',
                backdropFilter: 'blur(10px)'
              }}
              onMouseEnter={(e) => {
                if (activeTab !== tab.id) {
                  e.target.style.background = 'rgba(255,255,255,0.3)';
                }
              }}
              onMouseLeave={(e) => {
                if (activeTab !== tab.id) {
                  e.target.style.background = 'rgba(255,255,255,0.2)';
                }
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.name}</span>
            </button>
          ))}
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          background: 'rgba(255,255,255,0.2)',
          padding: '0.4rem 1rem',
          borderRadius: '20px',
          color: 'white'
        }}>
          <span style={{
            width: '10px',
            height: '10px',
            background: '#2ecc71',
            borderRadius: '50%',
            animation: 'pulse 2s infinite'
          }}></span>
          <span style={{ fontSize: '0.9rem' }}>System Active</span>
        </div>
      </div>

      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}
      </style>
    </nav>
  );
}