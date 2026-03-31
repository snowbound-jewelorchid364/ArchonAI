"use client";
import { useState, useEffect, useCallback, useRef } from "react";
import type { AgentProgress } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useSSE(jobId: string | null, token: string | null) {
  const [agents, setAgents] = useState<AgentProgress[]>([]);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!jobId || !token) return;

    const url = `${API_BASE}/jobs/${jobId}/stream?token=${encodeURIComponent(token)}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onmessage = (event) => {
      try {
        const data: AgentProgress = JSON.parse(event.data);
        if (data.status === "COMPLETED" || data.status === "FAILED") {
          setAgents((prev) => {
            const existing = prev.findIndex((a) => a.agent === data.agent);
            if (existing >= 0) {
              const updated = [...prev];
              updated[existing] = data;
              return updated;
            }
            return [...prev, data];
          });
        } else {
          setAgents((prev) => {
            const existing = prev.findIndex((a) => a.agent === data.agent);
            if (existing >= 0) {
              const updated = [...prev];
              updated[existing] = data;
              return updated;
            }
            return [...prev, data];
          });
        }
      } catch {
        // ignore parse errors
      }
    };

    es.addEventListener("done", () => {
      setDone(true);
      es.close();
    });

    es.onerror = () => {
      setError("Connection lost. Refresh to reconnect.");
      es.close();
    };
  }, [jobId, token]);

  useEffect(() => {
    connect();
    return () => {
      eventSourceRef.current?.close();
    };
  }, [connect]);

  return { agents, done, error };
}
