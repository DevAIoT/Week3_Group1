export function ConnectionStatus({ isConnected }) {
  return (
    <div className={`flex items-center space-x-2 ${isConnected ? 'text-green-600' : 'text-yellow-600'}`}>
      <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-600 animate-pulse' : 'bg-yellow-600'}`} />
      <span className="text-sm font-medium">
        {isConnected ? 'Live (WebSocket)' : 'Polling Mode'}
      </span>
    </div>
  );
}
