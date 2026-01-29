export function SummaryStats({ summary }) {
  if (!summary) return <div>Loading...</div>;

  const stats = [
    { label: 'Total Ratings', value: summary.count, icon: '📊' },
    { label: 'Average', value: summary.average?.toFixed(2) || 'N/A', icon: '⭐' },
    { label: 'Highest', value: summary.max || 'N/A', icon: '🔝' },
    { label: 'Lowest', value: summary.min || 'N/A', icon: '🔻' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {stats.map((stat, idx) => (
        <div key={idx} className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
            <div className="text-4xl">{stat.icon}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
