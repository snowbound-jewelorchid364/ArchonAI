interface PlanCardProps {
  name: string;
  price: string;
  features: string[];
  current?: boolean;
  onSelect?: () => void;
}

export function PlanCard({ name, price, features, current, onSelect }: PlanCardProps) {
  return (
    <div className={`rounded-lg border p-6 ${current ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'}`}>
      <h3 className="text-lg font-semibold">{name}</h3>
      <p className="mt-2 text-3xl font-bold">{price}<span className="text-sm font-normal text-gray-500">/month</span></p>
      <ul className="mt-4 space-y-2">
        {features.map((f, i) => (
          <li key={i} className="flex items-center gap-2 text-sm text-gray-600">
            <span className="text-green-500">&#10003;</span> {f}
          </li>
        ))}
      </ul>
      <button
        onClick={onSelect}
        disabled={current}
        className={`mt-6 w-full rounded-md px-4 py-2 text-sm font-medium ${
          current ? 'bg-gray-100 text-gray-400' : 'bg-blue-600 text-white hover:bg-blue-700'
        }`}
      >
        {current ? 'Current Plan' : 'Select Plan'}
      </button>
    </div>
  );
}
