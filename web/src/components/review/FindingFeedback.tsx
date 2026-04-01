"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api";

interface Props {
  reviewId: string;
  findingId: string;
}

export function FindingFeedback({ reviewId, findingId }: Props) {
  const [status, setStatus] = useState<"idle" | "helpful" | "unhelpful">("idle");
  const [comment, setComment] = useState("");
  const [showComment, setShowComment] = useState(false);

  async function submit(helpful: boolean) {
    setStatus(helpful ? "helpful" : "unhelpful");
    setShowComment(true);
    await apiClient.post(`/reviews/${reviewId}/feedback`, { finding_id: findingId, helpful, comment });
  }

  async function submitComment() {
    await apiClient.post(`/reviews/${reviewId}/feedback`, {
      finding_id: findingId,
      helpful: status === "helpful",
      comment,
    });
    setShowComment(false);
  }

  return (
    <div className="flex items-center gap-2 mt-2">
      <span className="text-sm text-gray-500">Helpful?</span>
      <button onClick={() => submit(true)} className="p-1 rounded hover:bg-gray-100">
        &#x1F44D;
      </button>
      <button onClick={() => submit(false)} className="p-1 rounded hover:bg-gray-100">
        &#x1F44E;
      </button>
      {showComment && (
        <div className="flex gap-2 ml-2">
          <input
            type="text"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Optional feedback..."
            className="text-sm border rounded px-2 py-1 w-48"
          />
          <button
            onClick={submitComment}
            className="text-sm bg-indigo-600 text-white px-2 py-1 rounded"
          >
            Send
          </button>
        </div>
      )}
    </div>
  );
}
