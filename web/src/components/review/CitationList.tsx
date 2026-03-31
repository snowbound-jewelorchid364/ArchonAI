'use client';

import { Citation } from '@/types';

interface Props {
  citations: Citation[];
}

export function CitationList({ citations }: Props) {
  if (!citations.length) return <p className="text-muted-foreground text-sm">No citations available.</p>;

  return (
    <div className="space-y-3">
      {citations.map((c, i) => (
        <div key={i} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
          <div className="flex items-start justify-between gap-2">
            <a
              href={c.url}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium text-blue-600 hover:underline text-sm"
            >
              {c.title}
            </a>
            <CredibilityBadge score={c.credibility_score} />
          </div>
          <p className="text-muted-foreground text-xs mt-1 line-clamp-2">{c.excerpt}</p>
          {c.published_date && (
            <span className="text-xs text-muted-foreground mt-1 block">{c.published_date}</span>
          )}
        </div>
      ))}
    </div>
  );
}

function CredibilityBadge({ score }: { score: number }) {
  const color = score >= 0.8 ? 'bg-green-100 text-green-800' :
                score >= 0.5 ? 'bg-yellow-100 text-yellow-800' :
                'bg-red-100 text-red-800';
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${color}`}>
      {(score * 100).toFixed(0)}%
    </span>
  );
}
