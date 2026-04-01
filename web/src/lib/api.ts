const API_BASE = `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1`;

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API request failed");
  }
  return res.json();
}

export async function createReview(repoUrl: string, mode: string, token: string) {
  return fetchAPI<{ job_id: string; status: string }>("/reviews", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ repo_url: repoUrl, mode }),
  });
}

export async function getReview(reviewId: string, token: string) {
  return fetchAPI<import("@/types").ReviewPackage>(`/reviews/${reviewId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getReviews(token: string) {
  return fetchAPI<import("@/types").ReviewListItem[]>("/reviews", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function downloadPackage(packageId: string, token: string) {
  const res = await fetch(`${API_BASE}/packages/${packageId}/download`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Download failed");
  return res.blob();
}

async function getClerkToken(): Promise<string> {
  if (typeof window !== "undefined" && (window as any).Clerk?.session) {
    return (await (window as any).Clerk.session.getToken()) ?? "";
  }
  return "";
}

export const apiClient = {
  async get<T>(path: string, token?: string): Promise<T> {
    const authToken = token ?? (await getClerkToken());
    return fetchAPI<T>(path, {
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    });
  },
  async post<T = void>(path: string, body: unknown, token?: string): Promise<T> {
    const authToken = token ?? (await getClerkToken());
    return fetchAPI<T>(path, {
      method: "POST",
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
      body: JSON.stringify(body),
    });
  },
  async delete<T = void>(path: string, token?: string): Promise<T> {
    const authToken = token ?? (await getClerkToken());
    return fetchAPI<T>(path, {
      method: "DELETE",
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    });
  },
  async listReviews(): Promise<import("@/types").ReviewListItem[]> {
    return this.get<import("@/types").ReviewListItem[]>("/reviews");
  },
  async createReview(repoUrl: string, mode: string): Promise<{ review_id: string; job_id: string }> {
    return this.post<{ review_id: string; job_id: string }>("/reviews", { repo_url: repoUrl, mode });
  },
};

export const api = apiClient;
