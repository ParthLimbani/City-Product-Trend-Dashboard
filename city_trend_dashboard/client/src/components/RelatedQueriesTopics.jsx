import React, { useState } from 'react';
import axios from 'axios';

const RelatedQueriesTopics = ({ city, product }) => {
  const [relatedQueries, setRelatedQueries] = useState(null);
  const [relatedTopics, setRelatedTopics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [queriesRes, topicsRes] = await Promise.all([
        axios.get(`http://127.0.0.1:8000/api/related-queries?city=${encodeURIComponent(city)}&product=${encodeURIComponent(product)}`),
        axios.get(`http://127.0.0.1:8000/api/related-topics?city=${encodeURIComponent(city)}&product=${encodeURIComponent(product)}`),
      ]);
      setRelatedQueries(queriesRes.data);
      setRelatedTopics(topicsRes.data);
    } catch (e) {
      setError('Failed to fetch related queries/topics');
    }
    setLoading(false);
  };

  React.useEffect(() => {
    if (city && product) fetchData();
    // eslint-disable-next-line
  }, [city, product]);

  return (
    <div style={{ marginTop: '2rem' }}>
      <h3 style={{ color: '#1976d2', marginBottom: '1rem' }}>Related Queries & Topics</h3>
      {loading && <div>Loading...</div>}
      {error && <div>{error}</div>}
      {relatedQueries && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4>Top Related Queries</h4>
          {relatedQueries.top.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr><th>Query</th><th>Value</th></tr></thead>
              <tbody>
                {relatedQueries.top.map((q, i) => (
                  <tr key={i}><td>{q.query}</td><td>{q.value}</td></tr>
                ))}
              </tbody>
            </table>
          ) : <div>No data</div>}
          <h4>Rising Related Queries</h4>
          {relatedQueries.rising.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr><th>Query</th><th>Value</th></tr></thead>
              <tbody>
                {relatedQueries.rising.map((q, i) => (
                  <tr key={i}><td>{q.query}</td><td>{q.value}</td></tr>
                ))}
              </tbody>
            </table>
          ) : <div>No data</div>}
        </div>
      )}
      {relatedTopics && (
        <div>
          <h4>Top Related Topics</h4>
          {relatedTopics.top.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr><th>Topic</th><th>Value</th></tr></thead>
              <tbody>
                {relatedTopics.top.map((t, i) => (
                  <tr key={i}><td>{t.topic_title || t.topic_mid}</td><td>{t.value}</td></tr>
                ))}
              </tbody>
            </table>
          ) : <div>No data</div>}
          <h4>Rising Related Topics</h4>
          {relatedTopics.rising.length > 0 ? (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead><tr><th>Topic</th><th>Value</th></tr></thead>
              <tbody>
                {relatedTopics.rising.map((t, i) => (
                  <tr key={i}><td>{t.topic_title || t.topic_mid}</td><td>{t.value}</td></tr>
                ))}
              </tbody>
            </table>
          ) : <div>No data</div>}
        </div>
      )}
    </div>
  );
};

export default RelatedQueriesTopics;
