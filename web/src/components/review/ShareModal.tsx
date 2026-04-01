'use client';

import { useState } from 'react';
import { apiClient } from '@/lib/api';

interface Props {
  reviewId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function ShareModal({ reviewId, isOpen, onClose }: Props) {
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [expiryDays, setExpiryDays] = useState(30);

  if (!isOpen) return null;

  async function handleCreate() {
    setLoading(true);
    try {
      const data = await apiClient.post<{ url: string; token: string }>(
        '/share',
        { review_id: reviewId, expires_in_days: expiryDays }
      );
      setShareUrl(`${window.location.origin}${data.url}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    if (shareUrl) {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-semibold mb-4">Share Review</h2>

        {!shareUrl ? (
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Link expires in</label>
              <select
                value={expiryDays}
                onChange={e => setExpiryDays(Number(e.target.value))}
                className="mt-1 block w-full rounded-md border px-3 py-2 text-sm"
              >
                <option value={7}>7 days</option>
                <option value={30}>30 days</option>
                <option value={90}>90 days</option>
              </select>
            </div>
            <button
              onClick={handleCreate}
              disabled={loading}
              className="w-full bg-black text-white rounded-lg py-2 text-sm font-medium hover:bg-gray-800 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Share Link'}
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <input readOnly value={shareUrl} className="flex-1 rounded-md border px-3 py-2 text-sm bg-muted" />
              <button onClick={handleCopy} className="px-3 py-2 rounded-md border text-sm font-medium hover:bg-muted">
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
            <p className="text-xs text-muted-foreground">Anyone with this link can view the review findings.</p>
          </div>
        )}

        <button onClick={onClose} className="mt-4 text-sm text-muted-foreground hover:text-foreground">
          Close
        </button>
      </div>
    </div>
  );
}
