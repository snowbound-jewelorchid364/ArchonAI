'use client';

import { Finding } from '@/types';
import { SeverityBadge } from './SeverityBadge';

interface Props {
  finding: Finding;
}

export function FindingCard({ finding }: Props) {
  return (
    <div className="border rounded-lg p-4 hover:shadow-sm transition-shadow">
      <div className="flex items-start gap-3">
        <SeverityBadge severity={finding.severity} />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-sm">{finding.title}</h3>
            <span className="text-xs text-muted-foreground ml-auto shrink-0">
              {Math.round(finding.confidence * 100)}% confidence
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">{finding.description}</p>
          <div className="mt-2 p-2 bg-muted/50 rounded text-sm">
            <strong>Recommendation:</strong> {finding.recommendation}
          </div>
          <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
            {finding.file_path && <span>File: {finding.file_path}{finding.line_number ? `:${finding.line_number}` : ''}</span>}
            <span className="capitalize">{finding.domain.replace(/_/g, ' ')}</span>
            {finding.from_codebase ? (
              <span className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded">Code</span>
            ) : (
              <span className="bg-purple-50 text-purple-700 px-1.5 py-0.5 rounded">Best Practice</span>
            )}
          </div>
          {finding.citations.length > 0 && (
            <div className="mt-2 space-y-1">
              {finding.citations.map((c, i) => (
                <a key={i} href={c.url} target="_blank" rel="noopener noreferrer"
                  className="block text-xs text-blue-600 hover:underline truncate">
                  {c.title}
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
