import { useState, useEffect } from "react";
import { apiClient } from "@/lib/api";
import type { Review, ReviewPackage } from "@/types";

export function useReview(reviewId: string) {
  const [review, setReview] = useState<Review | null>(null);
  const [pkg, setPkg] = useState<ReviewPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reviewId) return;

    async function fetch() {
      try {
        const data = await apiClient.get<Review>(/reviews/);
        setReview(data);
        if (data.status === "completed") {
          const pkgData = await apiClient.get<ReviewPackage>(/reviews//package);
          setPkg(pkgData);
        }
      } catch (e: any) {
        setError(e.message || "Failed to load review");
      } finally {
        setLoading(false);
      }
    }

    fetch();
  }, [reviewId]);

  return { review, pkg, loading, error };
}
