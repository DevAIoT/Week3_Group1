import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

export const getRatings = (params = {}) => {
  return api.get('/api/ratings', { params });
};

export const getSummary = () => {
  return api.get('/api/ratings/summary');
};

export const getTimeline = (period = 'hour') => {
  return api.get('/api/ratings/timeline', { params: { period } });
};

export const createRating = (rating) => {
  return api.post('/api/ratings', { rating });
};

export default {
  getRatings,
  getSummary,
  getTimeline,
  createRating,
};
