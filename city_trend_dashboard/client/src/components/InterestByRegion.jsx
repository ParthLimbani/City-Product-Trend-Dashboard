import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const InterestByRegion = ({ city, product }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!city || !product) return;
    setLoading(true);
    setError(null);
    axios.get(`http://127.0.0.1:8000/api/interest-by-region?city=${encodeURIComponent(city)}&product=${encodeURIComponent(product)}`)
      .then(res => setData(res.data))
      .catch(() => setError('Failed to fetch interest by region'))
      .finally(() => setLoading(false));
  }, [city, product]);

  const hasData = Array.isArray(data) && data.length > 0;
  const chartData = hasData ? {
    labels: data.map(d => d.region),
    datasets: [
      {
        label: 'Trend Score',
        data: data.map(d => d.trend_score),
        backgroundColor: 'rgba(25, 118, 210, 0.7)',
      },
    ],
  } : null;

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3 style={{ color: '#1976d2', marginBottom: '1rem' }}>Interest by Region</h3>
      {loading && <div>Loading...</div>}
      {error && <div>{error}</div>}
      {hasData ? (
        <Bar
          data={chartData}
          options={{
            responsive: true,
            plugins: {
              legend: { display: false },
              title: { display: true, text: 'Interest by Region' },
            },
            scales: {
              x: { title: { display: true, text: 'Region' } },
              y: { title: { display: true, text: 'Trend Score' } },
            },
          }}
        />
      ) : (
        <div>No region data available.</div>
      )}
    </div>
  );
};

export default InterestByRegion;
