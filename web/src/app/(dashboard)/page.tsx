export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-500 mt-1">Welcome back to ARCHON</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {['Total Reviews', 'Completed', 'Critical Findings', 'Avg Confidence'].map((title) => (
          <div key={title} className="bg-white border rounded-lg p-6 shadow-sm">
            <p className="text-sm text-gray-500">{title}</p>
            <p className="text-2xl font-bold mt-1">--</p>
          </div>
        ))}
      </div>
      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Reviews</h2>
        <p className="text-gray-500">
          No reviews yet. <a href="/reviews/new" className="text-blue-600 underline">Start your first review</a>
        </p>
      </div>
    </div>
  );
}