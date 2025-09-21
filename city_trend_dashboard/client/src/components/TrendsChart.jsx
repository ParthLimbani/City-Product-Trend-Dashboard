import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const TrendsChart = () => {
  const [cities, setCities] = useState([]);
  const [products, setProducts] = useState([]);
  const [selectedCity, setSelectedCity] = useState('Mumbai');
  const [selectedProduct, setSelectedProduct] = useState('Mobile phones');
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [timeframes, setTimeframes] = useState([]);
  const [selectedTimeframe, setSelectedTimeframe] = useState('now 7-d');


  // Fetch cities, products, timeframes, and initial trends on mount
  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/cities').then(res => setCities(res.data));
    axios.get('http://127.0.0.1:8000/api/products').then(res => setProducts(res.data));
    axios.get('http://127.0.0.1:8000/api/timeframes').then(res => setTimeframes(res.data));
    // Fetch default preview
    // setLoading(true);
    // setError(null);
    // axios.get(`http://127.0.0.1:8000/api?city=Mumbai&product=Mobile%20phones&timeframe=now%207-d`)
    //   .then(res => {
    //     setTrends(res.data);
    //     setLoading(false);
    //   })
    //   .catch(() => {
    //     setError('Failed to fetch trends');
    //     setLoading(false);
    //   });
  }, []);

  // API call only on button click
  const handleSeeTrends = () => {
    if (selectedCity && selectedProduct && selectedTimeframe) {
        setLoading(true);
        setError(null);
        axios.get(`http://127.0.0.1:8000/api?city=${encodeURIComponent(selectedCity)}&product=${encodeURIComponent(selectedProduct)}&timeframe=${encodeURIComponent(selectedTimeframe)}`)
        .then(res => {
            setTrends(res.data);
            setLoading(false);
        })
        .catch(() => {
            setError('Failed to fetch trends');
            setLoading(false);
        });
    }
    };

  const hasChartData = Array.isArray(trends) && trends.length > 0;
  const chartLabels = hasChartData ? trends.map(item => item.date) : [];
  const chartDataPoints = hasChartData ? trends.map(item => item.trend_score) : [];

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <label>
          City:&nbsp;
          <select value={selectedCity} onChange={e => setSelectedCity(e.target.value)}>
            <option value="">Select City</option>
            {cities.map(city => <option key={city} value={city}>{city}</option>)}
          </select>
        </label>
        &nbsp;&nbsp;
        <label>
          Product:&nbsp;
          <select value={selectedProduct} onChange={e => setSelectedProduct(e.target.value)}>
            <option value="">Select Product</option>
            {products.map(product => <option key={product} value={product}>{product}</option>)}
          </select>
        </label>
        <label>
            Timeframe:&nbsp;
            <select value={selectedTimeframe} onChange={e => setSelectedTimeframe(e.target.value)}>
                {timeframes.map(tf => <option key={tf.value} value={tf.value}>{tf.label}</option>)}
            </select>
        </label>
        &nbsp;&nbsp;
        <button onClick={handleSeeTrends} disabled={!selectedCity || !selectedProduct || loading}>
          See Trends
        </button>
      </div>
      {loading && <div>Loading trends...</div>}
      {error && <div>{error}</div>}
      {hasChartData ? (
        <>
          <h3>Trends Chart</h3>
          <Line
            data={{
              labels: chartLabels,
              datasets: [
                {
                  label: 'Trend Score',
                  data: chartDataPoints,
                  fill: false,
                  borderColor: 'rgb(75, 192, 192)',
                  tension: 0.1,
                },
              ],
            }}
            options={{
              responsive: true,
              plugins: {
                legend: { position: 'top' },
                title: { display: true, text: 'City Trends Over Time' },
              },
              scales: {
                x: {
                  title: { display: true, text: 'Date & Time' },
                  ticks: { maxTicksLimit: 10 },
                },
                y: {
                  title: { display: true, text: 'Trend Score' },
                },
              },
            }}
          />
        </>
      ) : (
        <div>No trends data available for chart.</div>
      )}
      {/* <h3>Trends Data (JSON)</h3> */}
      {/* <pre>{JSON.stringify(trends, null, 2)}</pre> */}
      
    </div>
  );
};

export default TrendsChart;