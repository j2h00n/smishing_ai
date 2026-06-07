import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQueryClient } from "@tanstack/react-query";
import {
  Brain, Search, RotateCcw, Download,
  AlertTriangle, CheckCircle2, ShieldCheck, ShieldX,
  Globe, User, MessageSquare, Tag, Network, Loader2, Lightbulb,
  Clock,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { useAnalyzeSmishing, getGetSmishingHistoryQueryKey, getGetSmishingStatsQueryKey, type SmishingResult } from "@workspace/api-client-react";
import { getRiskColor } from "@/lib/utils-risk";
import { useToast } from "@/hooks/use-toast";

const MAX_LEN = 500;

const formSchema = z.object({
  message: z.string().min(1, "분석할 문자 내용을 입력해주세요.").max(MAX_LEN, `${MAX_LEN}자 이내로 입력해주세요.`),
});
type FormValues = z.infer<typeof formSchema>;

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  "URL 위험도": Globe,
  "발신자 신뢰도": User,
  "문자 내용 위험도": MessageSquare,
  "키워드 탐지": Tag,
  "URL 구조 분석": Network,
};

function getRiskVerdict(level: SmishingResult["riskLevel"]): { label: string; desc: string } {
  switch (level) {
    case "critical": return { label: "스미싱 의심", desc: "해당 문자는 스미싱으로 판단됩니다." };
    case "high": return { label: "위험", desc: "스미싱 가능성이 높습니다." };
    case "medium": return { label: "주의", desc: "의심스러운 요소가 포함되어 있습니다." };
    case "low": return { label: "낮은 위험", desc: "대부분 정상이지만 주의가 필요합니다." };
    case "safe": return { label: "정상", desc: "스미싱 가능성이 낮습니다." };
  }
}

function getRiskBg(level: SmishingResult["riskLevel"]): string {
  switch (level) {
    case "critical": return "bg-red-50 border-red-200";
    case "high": return "bg-orange-50 border-orange-200";
    case "medium": return "bg-yellow-50 border-yellow-200";
    case "low": return "bg-blue-50 border-blue-200";
    case "safe": return "bg-green-50 border-green-200";
  }
}

function downloadResult(result: SmishingResult) {
  const lines = [
    "=== SmishGuard 스미싱 분석 결과 ===",
    `분석 시간: ${result.analyzedAt}`,
    `위험 점수: ${result.riskScore} / 100`,
    `위험 등급: ${result.riskLevel}`,
    "",
    "=== 감지된 위험 요소 ===",
    ...(result.reasons ?? []),
    "",
    "=== 카테고리별 분석 ===",
    ...Object.entries(result.categoryScores ?? {}).map(([cat, score]) => {
      const w = result.weights?.[cat] ?? 0;
      const contrib = result.weightedContributions?.[cat] ?? 0;
      const bias = result.biases?.[cat] ?? 0;
      return `${cat}: 점수=${score.toFixed(1)} 가중치=${w.toFixed(1)}% 편향=${bias.toFixed(4)} 기여=${contrib.toFixed(1)}`;
    }),
    `가중합: ${(result.weightedSum ?? 0).toFixed(1)}`,
    `최종편향(finalBias): ${(result.finalBias ?? 0).toFixed(4)}`,
    "",
    "=== 분석 문자 내용 ===",
    result.message,
  ];
  const blob = new Blob([lines.join("\n")], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `smishguard_${Date.now()}.txt`;
  a.click();
}

export default function Home() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [result, setResult] = useState<SmishingResult | null>(null);
  const [charCount, setCharCount] = useState(0);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { message: "" },
  });

  const analyzeMutation = useAnalyzeSmishing();

  function onSubmit(values: FormValues) {
    setResult(null);
    analyzeMutation.mutate(
      { data: values },
      {
        onSuccess: (data: SmishingResult) => {
          setResult(data);
          queryClient.invalidateQueries({ queryKey: getGetSmishingHistoryQueryKey() });
          queryClient.invalidateQueries({ queryKey: getGetSmishingStatsQueryKey() });
        },
        onError: () => {
          toast({ title: "오류 발생", description: "스미싱 분석 중 오류가 발생했습니다.", variant: "destructive" });
        },
      }
    );
  }

  function handleReset() {
    setResult(null);
    form.reset({ message: "" });
    setCharCount(0);
  }

  const riskColor = result ? getRiskColor(result.riskLevel) : "#94a3b8";
  const verdict = result ? getRiskVerdict(result.riskLevel) : null;
  const categories = result?.categoryScores ? Object.keys(result.categoryScores) : [];

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_1.3fr] items-start">
      {/* ── 왼쪽: 문자 입력 ── */}
      <div className="flex flex-col gap-4">
        <Card className="shadow-sm">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <MessageSquare className="h-4 w-4 text-primary" />
                문자 입력
              </CardTitle>
              <span className="text-xs text-muted-foreground font-mono">{charCount} / {MAX_LEN}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">검사할 문자 내용을 입력해주세요.</p>
          </CardHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)}>
              <CardContent className="space-y-4 pt-0">
                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Textarea
                          data-testid="input-message"
                          placeholder={"[국제발신]\n우체국 배송지연 확인해주세요\nhttp://example.com"}
                          className="min-h-[180px] resize-none text-sm leading-relaxed font-mono"
                          maxLength={MAX_LEN}
                          {...field}
                          onChange={(e) => {
                            field.onChange(e);
                            setCharCount(e.target.value.length);
                          }}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <Button
                  data-testid="button-analyze"
                  type="submit"
                  className="w-full font-bold h-11 text-sm bg-primary hover:bg-primary/90"
                  disabled={analyzeMutation.isPending}
                >
                  {analyzeMutation.isPending
                    ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />분석 중...</>
                    : <><Search className="mr-2 h-4 w-4" />AI 분석 시작</>}
                </Button>
              </CardContent>
            </form>
          </Form>
        </Card>

        {/* 입력 팁 */}
        <Card className="shadow-sm bg-muted/30">
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center gap-2 mb-2">
              <Lightbulb className="h-4 w-4 text-amber-500" />
              <span className="text-xs font-semibold text-foreground">입력 팁</span>
            </div>
            <ul className="space-y-1.5 text-xs text-muted-foreground">
              <li className="flex items-start gap-1.5"><span className="text-primary mt-0.5">•</span>실제 받은 문자 내용을 그대로 입력하세요.</li>
              <li className="flex items-start gap-1.5"><span className="text-primary mt-0.5">•</span>URL이 포함된 문자는 스미싱 가능성이 높으니 주의하세요.</li>
              <li className="flex items-start gap-1.5"><span className="text-primary mt-0.5">•</span>{MAX_LEN}자 이내로 입력 가능합니다.</li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* ── 오른쪽: 분석 결과 ── */}
      {result && verdict ? (
        <Card className="shadow-md overflow-hidden" data-testid="result-card">
          {/* 헤더 */}
          <CardHeader className="pb-3 border-b">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-base">
                <Brain className="h-4 w-4 text-primary" />
                AI 분석 결과
              </CardTitle>
              {result.analysisTime !== undefined && (
                <span className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  분석 시간: {result.analysisTime.toFixed(2)}초
                </span>
              )}
            </div>
          </CardHeader>

          <CardContent className="pt-4 space-y-5">
            {/* 판정 배너 */}
            <div className={`rounded-xl border p-4 flex items-center justify-between gap-4 ${getRiskBg(result.riskLevel)}`} data-testid="text-risk-summary">
              <div className="flex items-start gap-3">
                {result.riskLevel === "safe"
                  ? <CheckCircle2 className="h-6 w-6 mt-0.5 shrink-0" style={{ color: riskColor }} />
                  : <AlertTriangle className="h-6 w-6 mt-0.5 shrink-0" style={{ color: riskColor }} />}
                <div>
                  <p className="text-lg font-black" style={{ color: riskColor }}>{verdict.label}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">{verdict.desc}</p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <p className="text-xs text-muted-foreground font-medium">스미싱 위험 점수</p>
                <p className="text-3xl font-black leading-tight" style={{ color: riskColor }}>
                  {result.riskScore}<span className="text-base font-semibold text-muted-foreground"> / 100</span>
                </p>
              </div>
            </div>

            {/* 분석 상세 테이블 */}
            {categories.length > 0 && (
              <div>
                <p className="text-xs font-bold text-foreground mb-2">분석 상세</p>
                <div className="rounded-lg border overflow-hidden text-xs">
                  {/* 헤더 행 */}
                  <div className="grid bg-muted/60 px-3 py-2 font-semibold text-muted-foreground" style={{ gridTemplateColumns: "2fr 2fr 1fr 1.1fr 1.2fr" }}>
                    <span>분석 항목</span>
                    <span>값</span>
                    <span className="text-center">편향(Bias)</span>
                    <span className="text-center">가중치</span>
                    <span className="text-right">위험도 기여</span>
                  </div>

                  {categories.map((cat) => {
                    const score = result.categoryScores![cat] ?? 0;
                    const desc = result.categoryDescriptions?.[cat] ?? "";
                    const bias = result.biases?.[cat] ?? 0;
                    const w = result.weights?.[cat] ?? 0;
                    const contrib = result.weightedContributions?.[cat] ?? 0;
                    const IconComp = CATEGORY_ICONS[cat] ?? Network;
                    const contribColor = contrib >= 10 ? riskColor : contrib >= 5 ? "#f59e0b" : "#64748b";
                    return (
                      <div key={cat} className="grid border-t px-3 py-3 items-start gap-2" style={{ gridTemplateColumns: "2fr 2fr 1fr 1.1fr 1.2fr" }}>
                        <div className="flex items-center gap-1.5">
                          <IconComp className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
                          <span className="font-medium text-foreground/80">{cat}</span>
                        </div>
                        <div>
                          <p className="text-foreground/70 leading-tight">{desc}</p>
                          <div className="mt-1.5 h-1 w-full rounded-full bg-muted overflow-hidden">
                            <div className="h-full rounded-full transition-all" style={{ width: `${Math.min(100, score)}%`, backgroundColor: riskColor }} />
                          </div>
                          <p className="text-muted-foreground mt-0.5 font-mono">{score.toFixed(1)}점</p>
                        </div>
                        <div className="text-center">
                          <span className="font-mono text-muted-foreground">{bias >= 0 ? "+" : ""}{bias.toFixed(4)}</span>
                        </div>
                        <div className="text-center">
                          <span className="font-mono font-semibold">{w.toFixed(1)}%</span>
                        </div>
                        <div className="text-right">
                          <span className="font-mono font-bold text-sm" style={{ color: contribColor }}>{contrib.toFixed(1)}</span>
                        </div>
                      </div>
                    );
                  })}

                  {/* 합계 행 */}
                  <div className="grid border-t bg-muted/30 px-3 py-2.5 font-bold items-center" style={{ gridTemplateColumns: "2fr 2fr 1fr 1.1fr 1.2fr" }}>
                    <span className="text-foreground/80">총 점수</span>
                    <span className="text-muted-foreground">-</span>
                    <div className="text-center">
                      <span className="font-mono text-muted-foreground text-xs">
                        {(result.finalBias ?? 0) >= 0 ? "+" : ""}{(result.finalBias ?? 0).toFixed(4)}
                      </span>
                    </div>
                    <span className="text-center font-mono">100%</span>
                    <span className="text-right font-mono font-black" style={{ color: riskColor }}>
                      {(result.weightedSum ?? 0).toFixed(1)} / 100
                    </span>
                  </div>
                </div>

                {/* 산출 공식 설명 */}
                <p className="text-xs text-muted-foreground mt-2 leading-relaxed px-1">
                  <span className="font-semibold">점수 산출:</span>{" "}
                  각 항목 점수 × 가중치% = 위험도 기여 / 가중합 {(result.weightedSum ?? 0).toFixed(1)}점 → LSTM 통합 출력 → 최종 {result.riskScore}점
                </p>
              </div>
            )}

            <Separator />

            {/* 점수 기준 */}
            <div className="rounded-lg border bg-muted/20 p-3 space-y-1.5">
              <p className="text-xs font-bold text-foreground flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5 text-muted-foreground" />
                점수 기준
              </p>
              <div className="space-y-1 text-xs">
                <div className="flex items-center gap-2">
                  <span className="inline-block w-2 h-2 rounded-full bg-red-500 shrink-0" />
                  <span><span className="font-semibold">75점 이상:</span> 스미싱 의심 — 즉시 삭제하세요.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-block w-2 h-2 rounded-full bg-orange-400 shrink-0" />
                  <span><span className="font-semibold">57~74점:</span> 위험 — 클릭하지 마세요.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-block w-2 h-2 rounded-full bg-yellow-400 shrink-0" />
                  <span><span className="font-semibold">40~56점:</span> 주의 필요 — 발신자를 확인하세요.</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="inline-block w-2 h-2 rounded-full bg-green-400 shrink-0" />
                  <span><span className="font-semibold">39점 이하:</span> 정상 가능성 높음</span>
                </div>
              </div>
            </div>

            {/* 하단 버튼 */}
            <div className="flex gap-2 pt-1">
              <Button variant="outline" className="flex-1 text-xs font-semibold h-9" onClick={handleReset}>
                <RotateCcw className="mr-1.5 h-3.5 w-3.5" />다시 검사하기
              </Button>
              <Button className="flex-1 text-xs font-semibold h-9 bg-foreground text-background hover:bg-foreground/90" onClick={() => downloadResult(result)}>
                <Download className="mr-1.5 h-3.5 w-3.5" />검사 결과 저장
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="flex flex-col items-center justify-center text-center p-10 border-dashed bg-muted/20 min-h-[360px]">
          <div className="rounded-full bg-muted/60 p-5 mb-4">
            <ShieldX className="h-10 w-10 text-muted-foreground" />
          </div>
          <h3 className="text-base font-semibold text-foreground mb-2">분석 대기 중</h3>
          <p className="text-sm text-muted-foreground max-w-[230px] leading-relaxed">
            문자 내용을 입력하고 AI 분석 시작 버튼을 클릭하면 위험도를 확인할 수 있습니다.
          </p>
        </Card>
      )}
    </div>
  );
}
