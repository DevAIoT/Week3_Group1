import { useState, useEffect, useCallback } from 'react';
import socketService from '../services/socket';
import api from '../services/api';

const POLLING_INTERVAL = 10000; // 10 seconds

export function useRatings() {
  const [ratings, setRatings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch data from API
  const fetchData = useCallback(async () => {
    try {
      const [ratingsRes, summaryRes, timelineRes] = await Promise.all([
        api.getRatings({ limit: 20 }),
        api.getSummary(),
        api.getTimeline('hour'),
      ]);
      setRatings(ratingsRes.data);
      setSummary(summaryRes.data);
      setTimeline(timelineRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  }, []);

  useEffect(() => {
    // Initial data fetch
    fetchData();

    // Setup WebSocket
    socketService.connect();

    // Listen for WebSocket connection status
    const checkConnection = setInterval(() => {
      setIsConnected(socketService.isConnected());
    }, 1000);

    // Listen for new ratings via WebSocket
    socketService.on('rating_update', (newRating) => {
      console.log('New rating via WebSocket:', newRating);
      setRatings(prev => [newRating, ...prev].slice(0, 20));
      fetchData(); // Refresh summary stats and timeline
    });

    // Setup polling fallback
    const pollingInterval = setInterval(() => {
      if (!socketService.isConnected()) {
        console.log('Polling for updates...');
        fetchData();
      }
    }, POLLING_INTERVAL);

    // Cleanup
    return () => {
      clearInterval(checkConnection);
      clearInterval(pollingInterval);
      socketService.disconnect();
    };
  }, [fetchData]);

  return { ratings, summary, timeline, loading, isConnected, refetch: fetchData };
}
