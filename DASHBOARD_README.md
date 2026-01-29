# GestureRating Dashboard

Web-based dashboard for visualizing gesture detection ratings in real-time.

## Features

- **Real-time Updates**: WebSocket-based live updates with automatic polling fallback
- **Summary Statistics**: Total ratings, average, highest, and lowest ratings
- **Timeline Chart**: Visual representation of rating activity over the last 24 hours
- **Recent Activity Feed**: List of the 20 most recent ratings
- **Connection Status**: Visual indicator showing WebSocket or polling mode

## Architecture

```
[Gesture Detection + API :5000] ← WebSocket/HTTP → [Dashboard Server :5001] → [React Frontend]
         ↓
    [SQLite DB]
```

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- flask-socketio
- flask-cors
- python-socketio

### 2. Install Node.js Dependencies (if rebuilding frontend)

```bash
cd dashboard-frontend
npm install
```

## Usage

### Running the Dashboard

The dashboard requires two servers to be running:

#### Terminal 1 - Main Gesture Detection API with WebSocket

```bash
python main.py
```

This starts:
- Gesture detection system
- REST API on port 5000
- WebSocket server for real-time updates

#### Terminal 2 - Dashboard Server

```bash
python dashboard_app.py
```

This starts:
- Dashboard web server on port 5001
- Serves the React frontend

### Accessing the Dashboard

Open your browser and navigate to:

```
http://localhost:5001
```

Or from another device on the same network:

```
http://<raspberry-pi-ip>:5001
```

## Development

### Rebuilding the Frontend

If you make changes to the React frontend:

```bash
cd dashboard-frontend
npm run dev          # Development server with hot reload
npm run build        # Production build
```

### Frontend Structure

```
dashboard-frontend/
├── src/
│   ├── components/          # React components
│   │   ├── SummaryStats.jsx
│   │   ├── TimelineChart.jsx
│   │   ├── RecentActivity.jsx
│   │   └── ConnectionStatus.jsx
│   ├── hooks/              # Custom React hooks
│   │   └── useRatings.js   # Manages WebSocket + polling
│   ├── services/           # API and WebSocket clients
│   │   ├── api.js
│   │   └── socket.js
│   ├── utils/              # Helper functions
│   │   └── dateHelpers.js
│   ├── App.jsx             # Main app component
│   └── main.jsx            # Entry point
└── dist/                   # Built files (served by Flask)
```

## API Endpoints

The dashboard consumes the following API endpoints:

### GET /api/ratings
Get list of ratings
- Query params: `limit` (default: 100), `offset` (default: 0)
- Returns: Array of rating objects

### GET /api/ratings/summary
Get aggregate statistics
- Returns: `{ count, average, min, max }`

### GET /api/ratings/timeline
Get ratings grouped by time period
- Query params: `period` (hour, day, week)
- Returns: Array of `{ timestamp, count, average }`

### WebSocket Events

**Event: `new_rating`**
Emitted when a new rating is inserted into the database
```javascript
{
  id: 123,
  rating: 5,
  timestamp: "2026-01-29T12:34:56.789Z",
  source: "gesture"
}
```

## Configuration

### Backend Configuration

Edit `dashboard/config.py`:

```python
API_BASE_URL = "http://localhost:5000"
API_WS_URL = "ws://localhost:5000"
DASHBOARD_PORT = 5001
DASHBOARD_HOST = "0.0.0.0"
POLLING_INTERVAL = 10  # seconds
```

### Frontend Configuration

Edit `dashboard-frontend/src/services/api.js`:

```javascript
const API_BASE_URL = 'http://localhost:5000';
```

Edit `dashboard-frontend/src/services/socket.js`:

```javascript
export default new SocketService('http://localhost:5000');
```

## Troubleshooting

### Dashboard shows "Polling Mode" instead of "Live"

This means WebSocket connection failed. Check:
1. Is `main.py` running?
2. Is Flask-SocketIO installed? (`pip install flask-socketio`)
3. Check browser console for connection errors
4. Verify CORS settings in `ratings/api.py`

### "React build not found" error

Run the build command:
```bash
cd dashboard-frontend
npm run build
```

### API requests failing

1. Check that `main.py` is running on port 5000
2. Verify CORS is enabled in `ratings/api.py`
3. Check browser console for CORS errors
4. Ensure firewall allows connections on port 5000

### No data showing

1. Generate some ratings by performing hand gestures
2. Or use the API to insert test data:
```bash
curl -X POST http://localhost:5000/api/ratings \
  -H "Content-Type: application/json" \
  -d '{"rating": 5}'
```

## Technology Stack

### Backend
- **Flask**: Web framework
- **Flask-SocketIO**: WebSocket support
- **Flask-CORS**: Cross-origin request handling
- **SQLite**: Database

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool
- **Chart.js + react-chartjs-2**: Data visualization
- **Socket.IO Client**: WebSocket client with fallback
- **Axios**: HTTP client
- **Tailwind CSS**: Styling

## Performance Notes

- WebSocket provides instant updates with minimal overhead
- Polling fallback activates automatically if WebSocket fails
- Dashboard polls every 10 seconds when WebSocket is unavailable
- Timeline data is grouped by hour to reduce payload size
- Recent activity is limited to 20 most recent ratings

## Security Notes

For production deployment:
1. Enable authentication (add HTTP basic auth or JWT)
2. Use HTTPS/WSS instead of HTTP/WS
3. Restrict CORS to specific domains
4. Add rate limiting to API endpoints
5. Use environment variables for configuration

## License

Part of the GestureRating project.
