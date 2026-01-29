import { io } from 'socket.io-client';

class SocketService {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.connected = false;
    this.listeners = new Map();
  }

  connect() {
    this.socket = io(this.url, {
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      this.connected = true;
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      this.connected = false;
      console.log('WebSocket disconnected - falling back to polling');
    });

    this.socket.on('new_rating', (data) => {
      this.emit('rating_update', data);
    });
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  emit(event, data) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(cb => cb(data));
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
    }
  }

  isConnected() {
    return this.connected;
  }
}

export default new SocketService('http://localhost:5000');
