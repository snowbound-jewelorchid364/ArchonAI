'use client';

import { useParams } from 'next/navigation';
import { useSSE } from '@/hooks/useSSE';
import { AgentProgressPanel } from '@/components/review/AgentProgressPanel';

export default function ProgressPage() {
  const { id } = useParams<{ id: string }>();
  const { agents, isConnected } = useSSE(id);

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center gap-3">
        <h1 className="text-2xl font-bold">Review Progress</h1>
        <span className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
      </div>
      <AgentProgressPanel agents={agents} />
    </div>
  );
}
