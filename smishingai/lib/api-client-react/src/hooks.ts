import { useMutation, useQuery } from "@tanstack/react-query";
import { analyzeSmishing, getSmishingHistory, getSmishingStats } from "./generated/api";
import type { SmishingAnalyzeBody } from "./generated/api.schemas";

export const SMISHING_HISTORY_KEY = ["smishing", "history"];
export const SMISHING_STATS_KEY = ["smishing", "stats"];

export function getGetSmishingHistoryQueryKey() {
  return SMISHING_HISTORY_KEY;
}

export function getGetSmishingStatsQueryKey() {
  return SMISHING_STATS_KEY;
}

export function useAnalyzeSmishing() {
  return useMutation({
    mutationFn: ({ data }: { data: SmishingAnalyzeBody }) => analyzeSmishing(data),
  });
}

export function useGetSmishingHistory() {
  return useQuery({
    queryKey: SMISHING_HISTORY_KEY,
    queryFn: getSmishingHistory,
  });
}

export function useGetSmishingStats() {
  return useQuery({
    queryKey: SMISHING_STATS_KEY,
    queryFn: getSmishingStats,
  });
}
