export type SmishingResultRiskLevel = "safe" | "low" | "medium" | "high" | "critical";

export interface SmishingAnalyzeBody {
  message: string;
  url?: string;
}

export interface SmishingResult {
  id: number;
  message: string;
  url?: string;
  riskScore: number;
  riskLevel: SmishingResultRiskLevel;
  reasons: string[];
  analyzedAt: string;
  messagePreview: string;
  categoryScores?: Record<string, number>;
  weights?: Record<string, number>;
  weightedContributions?: Record<string, number>;
  weightedSum?: number;
  biases?: Record<string, number>;
  finalBias?: number;
  categoryDescriptions?: Record<string, string>;
  analysisTime?: number;
}

export interface SmishingHistoryItem {
  id: number;
  messagePreview: string;
  riskScore: number;
  riskLevel: SmishingResultRiskLevel;
  analyzedAt: string;
  url?: string;
}

export interface SmishingStats {
  totalAnalyzed: number;
  safeCount: number;
  lowCount: number;
  mediumCount: number;
  highCount: number;
  criticalCount: number;
  recentTrend: string;
}
