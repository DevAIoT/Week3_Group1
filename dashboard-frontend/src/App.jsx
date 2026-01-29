import { useRatings } from './hooks/useRatings';
import { SummaryStats } from './components/SummaryStats';
import { TimelineChart } from './components/TimelineChart';
import { RecentActivity } from './components/RecentActivity';
import { ConnectionStatus } from './components/ConnectionStatus';

function App() {
  const { ratings, summary, timeline, loading, isConnected, refetch } = useRatings();

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">
              GestureRating Dashboard
            </h1>
            <div className="flex items-center space-x-4">
              <ConnectionStatus isConnected={isConnected} />
              <button
                onClick={refetch}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
              >
                Refresh
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        ) : (
          <>
            <SummaryStats summary={summary} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                {timeline.length > 0 ? (
                  <TimelineChart data={timeline} />
                ) : (
                  <div className="h-64 flex items-center justify-center text-gray-500">
                    No timeline data available
                  </div>
                )}
              </div>
              <div>
                <RecentActivity ratings={ratings} />
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
