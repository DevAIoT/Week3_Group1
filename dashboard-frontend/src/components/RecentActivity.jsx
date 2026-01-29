import { formatTimeAgo } from '../utils/dateHelpers';

export function RecentActivity({ ratings }) {
  const renderStars = (rating) => '⭐'.repeat(rating);

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b">
        <h3 className="text-lg font-semibold">Recent Activity</h3>
      </div>
      <div className="divide-y max-h-96 overflow-y-auto">
        {ratings.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No ratings yet
          </div>
        ) : (
          ratings.map((rating) => (
            <div key={rating.id} className="px-6 py-4 flex items-center justify-between hover:bg-gray-50">
              <div className="flex items-center space-x-4">
                <span className="text-2xl">{renderStars(rating.rating)}</span>
                <div>
                  <p className="font-semibold text-gray-900">{rating.rating} Stars</p>
                  <p className="text-sm text-gray-500">{rating.source}</p>
                </div>
              </div>
              <span className="text-sm text-gray-500">
                {formatTimeAgo(rating.timestamp)}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
