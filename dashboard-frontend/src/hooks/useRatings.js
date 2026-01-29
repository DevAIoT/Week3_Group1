import { useState, useEffect, useCallback } from 'react';
import socketService from '../services/socket';
import api from '../services/api';

const POLLING_INTERVAL = 10000;

export function useRatings() {
  const [ratings, setRatings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [timelinePeriod, setTimelinePeriod] = useState('hour');
  const [distribution, setDistribution] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [ratingsRes, summaryRes, timelineRes, distRes] = await Promise.all([
        api.getRatings({ limit: 200 }),
        api.getSummary(),
        api.getTimeline(timelinePeriod),
        api.getDistribution(),
      ]);
      setRatings(ratingsRes.data);
      setSummary(summaryRes.data);
      setTimeline(timelineRes.data);
      setDistribution(distRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      setLoading(false);
    }
  }, [timelinePeriod]);

  const fetchTimeline = useCallback(async (period) => {
    setTimelinePeriod(period);
    try {
      const res = await api.getTimeline(period);
      setTimeline(res.data);
    } catch (error) {
      console.error('Failed to fetch timeline:', error);
    }
  }, []);

  useEffect(() => {
    fetchData();

    socketService.connect();

    const checkConnection = setInterval(() => {
      setIsConnected(socketService.isConnected());
    }, 1000);

    socketService.on('rating_update', (newRating) => {
      setRatings(prev => [newRating, ...prev].slice(0, 200));
      fetchData();
    });

    const pollingInterval = setInterval(() => {
      if (!socketService.isConnected()) {
        fetchData();
      }
    }, POLLING_INTERVAL);

    return () => {
      clearInterval(checkConnection);
      clearInterval(pollingInterval);
      socketService.disconnect();
    };
  }, [fetchData]);

  return {
    ratings,
    summary,
    timeline,
    timelinePeriod,
    distribution,
    loading,
    isConnected,
    refetch: fetchData,
    fetchTimeline,
  };
}
