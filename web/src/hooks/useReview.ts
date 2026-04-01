import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import type { Review, ReviewPackage } from "@/types";

export function useReview(reviewId: string) {
  const [review, setReview] = useState<Review | null>(null);
  const [pkg, setPkg] = useState<ReviewPackage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reviewId) return;

    async function load() {
      try {
        const data = await apiClient.get<Review>(`/reviews/${reviewId}`);
        setReview(data);
        if (data.status === "completed") {
          const pkgData = await apiClient.get<ReviewPackage>(`/reviews/${reviewId}/package`);
          setPkg(pkgData);
        }
      } catch (e: any) {
        setError(e.message || "Failed to load review");
      } finally {
        setIsLoading(false);
      }
    }

    load();
  }, [reviewId]);

  return { review, pkg, isLoading, error };
}
