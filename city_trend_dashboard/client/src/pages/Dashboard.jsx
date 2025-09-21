import React from 'react';
import TrendsChart from '../components/TrendsChart';
import TrendAnalysisChart from '../components/TrendAnalysisChart';


const cardStyle = {
  background: '#fff',
  borderRadius: '16px',
  boxShadow: '0 4px 24px rgba(0,0,0,0.08)',
  padding: '2rem',
  margin: '2rem 0',
  maxWidth: '900px',
  width: '100%',
};

const Dashboard = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(120deg, #e0eafc 0%, #cfdef3 100%)', padding: '2rem 0' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '0 1rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, letterSpacing: '-1px', color: '#222', marginBottom: 0 }}>City Trend Dashboard</h1>
        <div style={{ color: '#555', fontSize: '1.2rem', marginBottom: '2.5rem' }}>
          Visualize and analyze Google Trends data for top Indian cities and products.<br/>
          <span style={{ color: '#1976d2', fontWeight: 500 }}>Powered by Google Trends, ARIMA, and SARIMA models.</span>
        </div>
        <div style={cardStyle}>
          <h2 style={{ fontWeight: 600, fontSize: '1.4rem', marginBottom: '1.5rem', color: '#1976d2' }}>Live Trends Chart</h2>
          <TrendsChart />
        </div>
        <div style={cardStyle}>
          <h2 style={{ fontWeight: 600, fontSize: '1.4rem', marginBottom: '1.5rem', color: '#1976d2' }}>Time Series Analysis (ARIMA & SARIMA)</h2>
          <TrendAnalysisChart />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;