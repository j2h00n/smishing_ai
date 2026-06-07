import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useQueryClient } from "@tanstack/react-query";
import { ShieldAlert, ShieldCheck, ShieldX, Loader2, Link, Smartphone, Clock, Gift, UserX, Banknote, AlertTriangle, MousePointerClick, Layers, AlertCircle, ShieldOff, CheckCircle2, XCircle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useAnalyzeSmishing, getGetSmishingHistoryQueryKey, getGetSmishingStatsQueryKey, type SmishingResult } from "@workspace/api-client-react";
import { getRiskColor, getRiskBgClass, getRiskTextClass, getRiskLabel, getRiskSummary, getCategoryIcon, extractUrlFromText } from "@/lib/utils-risk";
import { useToast } from "@/hooks/use-toast";

const formSchema = z.object({
  message: z.string().min(1, "분석할 문자 내용 을 입력해주세요."),
  url: z.string().optional(),
});

type FormValues = z.infer<typeof formSchema>;

const ICON_MAP: Record<string, React.ElementType> = {
  "shield-off": ShieldOff,
  clock: Clock,
  gift: Gift,
  "user-x": UserX,
  banknote: Banknote,
  smartphone: Smartphone,
  link: Link,
  "mouse-pointer-click": MousePointerClick,
  "alert-triangle": AlertTriangle,
  layers: Layers,
  "alert-circle": AlertCircle,
};

function ReasonIcon({ reason }: { reason: string }) {
  const iconName = getCategoryIcon(reason);
  const IconComp = ICON_MAP[iconName] ?? AlertCircle;
  return <IconComp className="h-4 w-4 shrink-0 mt-0.5" />;
}

function extractBracketLabel(reason: string): { label: string; detail: string } {
  const match = reason.match(/^\[([^\]]+)\]\s*(.+)$/);
  if (match) return { label: match[1], detail: match[2] };
  return { label: "", detail: reason };
}

function RiskGauge({ score, level }: { score: number; level: SmishingResult["riskLevel"] }) {
  const color = getRiskColor(level);
  const radius = 68;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (circumference * score) / 100;

  return (
    <div className="flex flex-col items-center gap-3 py-4">
      <div className="relative flex h-44 w-44 items-center justify-center">
        <svg className="absolute inset-0 h-full w-full -rotate-90" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r={radius} fill="none" stroke="currentColor" strokeWidth="14" className="text-muted/40" />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            style={{ transition: "stroke-dashoffset 1s ease-in-out, stroke 0.5s ease" }}
          />
        </svg>
        <div className="flex flex-col items-center z-10">
          <span className="text-5xl font-black tracking-tight" style={{ color }}>{score}</span>
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mt-0.5">위험 점수</span>
        </div>
      </div>
      <div className="w-full space-y-1.5">
        <div className="flex justify-between text-xs text-muted-foreground font-medium px-1">
          <span>0 안전</span>
          <span>50 위험</span>
          <span>100 매우위험</span>
        </div>
        <div className="relative h-3 w-full rounded-full overflow-hidden bg-muted/40">
          <div className="absolute inset-y-0 left-0 rounded-full" style={{ width: `${score}%`, background: `linear-gradient(to right, #22c55e, #f59e0b, #ef4444)`, transition: "width 1s ease-in-out" }} />
          <div className="absolute top-0 h-full w-1 bg-white/80 rounded-full shadow" style={{ left: `${score}%`, transform: "translateX(-50%)", transition: "left 1s ease-in-out" }} />
        </div>
      </div>
    </div>
  );
}

export default function Home() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [result, setResult] = useState<SmishingResult | null>(null);
  const [urlAutoExtracted, setUrlAutoExtracted] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { message: "", url: "" },
  });

  const analyzeMutation = useAnalyzeSmishing();

  function handleMessageChange(value: string, fieldOnChange: (v: string) => void) {
    fieldOnChange(value);
    const extracted = extractUrlFromText(value);
    if (extracted) {
      form.setValue("url", extracted);
      setUrlAutoExtracted(true);
    } else if (urlAutoExtracted) {
      form.setValue("url", "");
      setUrlAutoExtracted(false);
    }
  }

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

  const riskColor = result ? getRiskColor(result.riskLevel) : undefined;

  return (
    <div className="grid gap-6 lg:grid-cols-2 items-start">
      <Card className="h-fit shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-2 text-lg">
            <ShieldAlert className="h-5 w-5 text-primary" />
            새로운 분석
          </CardTitle>
          <CardDescription>의심스러운 문자 내용 을 붙여넣으면 자동으로 URL을 감지하고 위험도를 분석합니다.</CardDescription>
        </CardHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <CardContent className="space-y-5">
              <FormField
                control={form.control}
                name="message"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="font-semibold">문자 내용</FormLabel>
                    <FormControl>
                      <Textarea
                        data-testid="input-message"
                        placeholder="분석할 문자 메시지 내용을 붙여넣기 하세요.\n\nURL이 포함된 경우 자동으로 감지됩니다."
                        className="min-h-[160px] resize-none text-sm leading-relaxed"
                        {...field}
                        onChange={(e) => handleMessageChange(e.target.value, field.onChange)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <FormField
                control={form.control}
                name="url"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="font-semibold flex items-center gap-2">
                      <Link className="h-3.5 w-3.5 text-muted-foreground" />
                      URL
                      {urlAutoExtracted && (
                        <Badge variant="outline" className="ml-1 text-xs font-normal px-1.5 py-0 text-blue-600 border-blue-300 bg-blue-50">
                          자동 감지됨
                        </Badge>
                      )}
                      <span className="text-muted-foreground font-normal">(선택사항)</span>
                    </FormLabel>
                    <FormControl>
                      <Input
                        data-testid="input-url"
                        placeholder="https://example.com"
                        {...field}
                        onChange={(e) => { field.onChange(e); setUrlAutoExtracted(false); }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button data-testid="button-analyze" type="submit" className="w-full font-bold h-11 text-sm" disabled={analyzeMutation.isPending}>
                {analyzeMutation.isPending ? (<><Loader2 className="mr-2 h-4 w-4 animate-spin" />분석 중...</>) : ("분석하기")}
              </Button>
            </CardContent>
          </form>
        </Form>
      </Card>

      <div className="flex flex-col gap-4">
        {result ? (
          <Card className={`overflow-hidden shadow-md border-2 ${getRiskBgClass(result.riskLevel)}`} data-testid="result-card">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">분석 결과</CardTitle>
                <Badge className="px-3 py-1 text-sm font-bold text-white border-0" style={{ backgroundColor: riskColor }} data-testid="badge-risk-level">
                  {getRiskLabel(result.riskLevel)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-5">
              <RiskGauge score={result.riskScore} level={result.riskLevel} />
              <div className={`rounded-xl border p-4 ${getRiskBgClass(result.riskLevel)}`} data-testid="text-risk-summary">
                <div className="flex items-start gap-3">
                  {result.riskLevel === "safe" ? (<CheckCircle2 className="h-5 w-5 mt-0.5 text-green-600 shrink-0" />) : (<XCircle className="h-5 w-5 mt-0.5 shrink-0" style={{ color: riskColor }} />)}
                  <p className={`text-sm leading-relaxed font-medium ${getRiskTextClass(result.riskLevel)}`}>
                    {getRiskSummary(result.riskLevel, result.riskScore)}
                  </p>
                </div>
              </div>
              {result.riskLevel === "safe" ? (
                <div className="flex flex-col items-center gap-2 py-4 text-center">
                  <ShieldCheck className="h-10 w-10 text-green-500" />
                  <p className="text-sm text-muted-foreground">특별한 위험 요소가 감지되지 않았습니다.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4" style={{ color: riskColor }} />
                    <h4 className="text-sm font-bold" style={{ color: riskColor }}>
                      감지된 위험 요소 ({result.reasons.length}건)
                    </h4>
                  </div>
                  <Separator />
                  <ul className="space-y-3" data-testid="list-reasons">
                    {result.reasons.map((reason: string, i: number) => {
                      const { label, detail } = extractBracketLabel(reason);
                      return (
                        <li key={i} className="flex items-start gap-3" data-testid={`reason-item-${i}`}>
                          <div className="flex items-center justify-center rounded-md p-1.5 shrink-0 mt-0.5" style={{ backgroundColor: `${riskColor}20`, color: riskColor }}>
                            <ReasonIcon reason={reason} />
                          </div>
                          <div className="flex-1 min-w-0">
                            {label && (
                              <span className="inline-block text-xs font-bold px-1.5 py-0.5 rounded mb-1" style={{ backgroundColor: `${riskColor}18`, color: riskColor }}>
                                {label}
                              </span>
                            )}
                            <p className="text-sm text-foreground/80 leading-relaxed">{detail}</p>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              {result.url && (
                <>
                  <Separator />
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">분석된 URL</p>
                    <p className="text-xs font-mono break-all text-foreground/70 bg-muted/50 rounded px-2 py-1.5" data-testid="text-analyzed-url">
                      {result.url}
                    </p>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        ) : (
          <Card className="flex flex-col items-center justify-center text-center p-10 border-dashed bg-muted/20 min-h-[300px]">
            <div className="rounded-full bg-muted/60 p-5 mb-4">
              <ShieldX className="h-10 w-10 text-muted-foreground" />
            </div>
            <h3 className="text-base font-semibold text-foreground mb-2">분석 대기 중</h3>
            <p className="text-sm text-muted-foreground max-w-[230px] leading-relaxed">
              문자 내용을 입력하고 분석하기 버튼을 클릭하면 위험도를 확인할 수 있습니다.
            </p>
          </Card>
        )}
      </div>
    </div>
  );
}
