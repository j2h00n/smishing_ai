import { type SmishingResultRiskLevel } from "@workspace/api-client-react/src/generated/api.schemas";

export function getRiskColor(level: SmishingResultRiskLevel): string {
  switch (level) {
    case "safe": return "#22c55e";
    case "low": return "#3b82f6";
    case "medium": return "#f59e0b";
    case "high": return "#f97316";
    case "critical": return "#ef4444";
    default: return "#94a3b8";
  }
}

export function getRiskBgClass(level: SmishingResultRiskLevel): string {
  switch (level) {
    case "safe": return "bg-green-50 border-green-200 dark:bg-green-950/30 dark:border-green-800";
    case "low": return "bg-blue-50 border-blue-200 dark:bg-blue-950/30 dark:border-blue-800";
    case "medium": return "bg-amber-50 border-amber-200 dark:bg-amber-950/30 dark:border-amber-800";
    case "high": return "bg-orange-50 border-orange-200 dark:bg-orange-950/30 dark:border-orange-800";
    case "critical": return "bg-red-50 border-red-200 dark:bg-red-950/30 dark:border-red-800";
    default: return "bg-muted border-border";
  }
}

export function getRiskTextClass(level: SmishingResultRiskLevel): string {
  switch (level) {
    case "safe": return "text-green-700 dark:text-green-400";
    case "low": return "text-blue-700 dark:text-blue-400";
    case "medium": return "text-amber-700 dark:text-amber-400";
    case "high": return "text-orange-700 dark:text-orange-400";
    case "critical": return "text-red-700 dark:text-red-400";
    default: return "text-muted-foreground";
  }
}

export function getRiskLabel(level: SmishingResultRiskLevel): string {
  switch (level) {
    case "safe": return "안전";
    case "low": return "주의";
    case "medium": return "경고";
    case "high": return "위험";
    case "critical": return "매우 위험";
    default: return "알 수 없음";
  }
}

export function getRiskSummary(level: SmishingResultRiskLevel, score: number): string {
  switch (level) {
    case "safe": return "이 문자는 스미싱 특징이 거의 보이지 않습니다. 안전한 것으로 판단됩니다.";
    case "low": return `위험 점수 ${score}점 — 일부 경미한 의심 표현이 있지만 전형적인 스미싱 패턴은 아닙니다. 계속 주의하세요.`;
    case "medium": return `위험 점수 ${score}점 — 스미싱에 자주 사용되는 패턴이 포함되어 있습니다. 링크를 누르거나 정보를 입력하지 마세요.`;
    case "high": return `위험 점수 ${score}점 — 여러 개의 스미싱 신호가 발견되었습니다. 사기일 가능성이 높으니 바로 삭제하는 것이 좋습니다.`;
    case "critical": return `위험 점수 ${score}점 — 매우 강한 스미싱 신호가 다수 감지되었습니다. 거의 확실히 사기이므로 즉시 삭제하고 차단하세요.`;
    default: return "";
  }
}

export function getCategoryIcon(reason: string): string {
  if (reason.includes("[개인정보") || reason.includes("[인증번호")) return "shield-off";
  if (reason.includes("[긴박감")) return "clock";
  if (reason.includes("[미끼") || reason.includes("[유인")) return "gift";
  if (reason.includes("[사칭") || reason.includes("[공공기관") || reason.includes("[유명 서비스") || reason.includes("[택배")) return "user-x";
  if (reason.includes("[금융")) return "banknote";
  if (reason.includes("[악성 앱") || reason.includes("[악성앱")) return "smartphone";
  if (reason.includes("[단축 URL") || reason.includes("[IP 주소") || reason.includes("[위험 도메인") || reason.includes("[비암호화") || reason.includes("[의심 도메인") || reason.includes("[유명 기관 사칭")) return "link";
  if (reason.includes("[링크 클릭")) return "mouse-pointer-click";
  if (reason.includes("[위협") || reason.includes("[경고")) return "alert-triangle";
  if (reason.includes("[복수 URL") || reason.includes("[전형적")) return "layers";
  return "alert-circle";
}

export function extractUrlFromText(text: string): string {
  const match = text.match(/https?:\/\/[^\s\)\]>]+/);
  return match ? match[0] : "";
}
