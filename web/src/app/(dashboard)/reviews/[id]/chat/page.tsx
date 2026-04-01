import { ChatWindow } from '@/components/chat/ChatWindow';

interface Props {
  params: { id: string };
}

export default function ReviewChatPage({ params }: Props) {
  return (
    <div className="flex h-[calc(100vh-4rem)] flex-col">
      <div className="border-b px-6 py-4">
        <h1 className="text-lg font-semibold">Architecture Advisor</h1>
        <p className="text-sm text-gray-500">
          Ask questions grounded in this review&apos;s findings and recommendations.
        </p>
      </div>
      <div className="flex-1 overflow-hidden">
        <ChatWindow reviewId={params.id} />
      </div>
    </div>
  );
}
