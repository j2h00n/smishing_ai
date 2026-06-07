import axios from "axios";
import type { SmishingAnalyzeBody, SmishingResult, SmishingHistoryItem, SmishingStats } from "./api.schemas";

const BASE_URL = import.meta.env?.VITE_API_URL || "";

const client = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function analyzeSmishing(data: SmishingAnalyzeBody): Promise<SmishingResult> {
  const response = await client.post<SmishingResult>("/api/smishing/analyze", data);
  return response.data;
}

export async function getSmishingHistory(): Promise<SmishingHistoryItem[]> {
  const response = await client.get<SmishingHistoryItem[]>("/api/smishing/history");
  return response.data;
}

export async function getSmishingStats(): Promise<SmishingStats> {
  const response = await client.get<SmishingStats>("/api/smishing/stats");
  return response.data;
}
