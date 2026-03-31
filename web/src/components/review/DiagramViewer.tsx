'use client';

import { useEffect, useRef } from 'react';

interface Props {
  content: string;
  title: string;
}

export function DiagramViewer({ content, title }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function render() {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({ startOnLoad: false, theme: 'default' });
        if (containerRef.current) {
          const { svg } = await mermaid.render(`diagram-${title.replace(/\s/g, '-')}`, content);
          containerRef.current.innerHTML = svg;
        }
      } catch {
        if (containerRef.current) {
          containerRef.current.innerHTML = `<pre class="text-xs p-4 bg-muted rounded overflow-auto">${content}</pre>`;
        }
      }
    }
    render();
  }, [content, title]);

  return (
    <div className="border rounded-lg p-4">
      <h3 className="font-medium mb-3">{title}</h3>
      <div ref={containerRef} className="overflow-auto" />
    </div>
  );
}
