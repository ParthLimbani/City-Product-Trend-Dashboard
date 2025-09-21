import React from 'react';
import TrendsChart from '../components/TrendsChart';
import TrendAnalysisChart from '../components/TrendAnalysisChart';

const Dashboard = () => {
  return (
    <div>
      <h1>City Trend Dashboard</h1>
  <TrendsChart />
  <TrendAnalysisChart />
    </div>
  );
};

export default Dashboard;