import RelatedQueriesTopics from './RelatedQueriesTopics';
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const TrendAnalysisChart = () => {
  const [cities, setCities] = useState([]);
  const [products, setProducts] = useState([]);
  const [city, setCity] = useState('Mumbai');
  const [product, setProduct] = useState('Mobile phones');
  // Fetch cities and products on mount
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/cities').then(res => setCities(res.data));
    axios.get('http://127.0.0.1:8000/api/products').then(res => setProducts(res.data));
  }, []);
  const [window, setWindow] = useState(7);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(`http://127.0.0.1:8000/api/trend-analysis/90days?city=${encodeURIComponent(city)}&product=${encodeURIComponent(product)}&window=${window}`);
      setData(res.data);
    } catch (e) {
      setError('Failed to fetch analysis');
    }
    setLoading(false);
  };

  const hasData = Array.isArray(data) && data.length > 0;
  const labels = hasData ? data.map(d => d.date) : [];
//   const trendScores = hasData ? data.map(d => d.trend_score) : [];
  const movingAvg = hasData ? data.map(d => d.moving_average) : [];
  const arimaPred = hasData ? data.map(d => d.arima_pred) : [];
  const sarimaPred = hasData ? data.map(d => d.sarima_pred) : [];

  console.log(arimaPred, sarimaPred);

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3>90 Days Trend Analysis</h3>
      <div style={{ marginBottom: '1rem' }}>
        <label>
          City:&nbsp;
          <select value={city} onChange={e => setCity(e.target.value)}>
            <option value="">Select City</option>
            {cities.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
        &nbsp;&nbsp;
        <label>
          Product:&nbsp;
          <select value={product} onChange={e => setProduct(e.target.value)}>
            <option value="">Select Product</option>
            {products.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </label>
        &nbsp;&nbsp;
        <label>
          Moving Avg Window:&nbsp;
          <input type="number" min={1} max={30} value={window} onChange={e => setWindow(Number(e.target.value))} />
        </label>
        &nbsp;&nbsp;
        <button onClick={fetchAnalysis} disabled={loading || !city || !product}>See Analysis</button>
      </div>
      {loading && <div>Loading analysis...</div>}
      {error && <div>{error}</div>}
      {hasData ? (
        <Line
          data={{
            labels,
            datasets: [
            //   {
            //     label: 'Trend Score',
            //     data: trendScores,
            //     borderColor: 'rgb(75, 192, 192)',
            //     fill: false,
            //     tension: 0.1,
            //   },
              {
                label: `Moving Avg (${window})`,
                data: movingAvg,
                borderColor: 'rgb(255, 99, 132)',
                fill: false,
                tension: 0.1,
              },
              {
                label: 'ARIMA Prediction',
                data: arimaPred,
                borderColor: 'rgb(54, 162, 235)',
                borderDash: [5, 5],
                fill: false,
                tension: 0.1,
              },
              {
                label: 'SARIMA Prediction',
                data: sarimaPred,
                borderColor: 'rgb(255, 206, 86)',
                borderDash: [2, 2],
                fill: false,
                tension: 0.1,
              },
            ],
          }}
          options={{
            responsive: true,
            plugins: {
              legend: { position: 'top' },
              title: { display: true, text: '90 Days Trend Analysis' },
            },
            scales: {
              x: { title: { display: true, text: 'Date' }, ticks: { maxTicksLimit: 10 } },
              y: { title: { display: true, text: 'Score' } },
            },
          }}
        />
      ) : (
        <div>No analysis data available.</div>
      )}

      {/* Related Queries & Topics Visualization */}
      <RelatedQueriesTopics city={city} product={product} />

  {/* Interest by Region Visualization removed as requested */}
    </div>
  );
};

export default TrendAnalysisChart;
