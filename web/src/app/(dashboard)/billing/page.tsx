"use client";

export default function BillingPage() {
  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Billing</h1>

      <div className="border border-gray-800 rounded-lg p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold">Starter Plan</h2>
            <p className="text-gray-400 text-sm">3 reviews per month</p>
          </div>
          <span className="text-2xl font-bold">$49/mo</span>
        </div>
        <div className="bg-gray-900 rounded-full h-2 mb-2">
          <div className="bg-white rounded-full h-2 w-0" />
        </div>
        <p className="text-xs text-gray-500">0 of 3 reviews used this month</p>
      </div>

      <button className="w-full border border-gray-700 py-3 rounded-lg text-sm font-medium hover:border-white transition">
        Upgrade to Pro ($199/mo)
      </button>
    </div>
  );
}
