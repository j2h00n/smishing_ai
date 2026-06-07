import { useGetSmishingStats } from "@workspace/api-client-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ShieldCheck, AlertTriangle, ShieldAlert, BarChart, TrendingUp, Skull } from "lucide-react";
import { getRiskColor } from "@/lib/utils-risk";

export default function Stats() {
  const { data: stats, isLoading } = useGetSmishingStats();

  if (isLoading || !stats) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <Card key={i}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <Skeleton className="h-4 w-[100px]" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-[60px]" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">총 분석 건수</CardTitle>
            <BarChart className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAnalyzed.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">누적 검사된 메시지 수</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium text-destructive">매우 위험</CardTitle>
            <Skull className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{stats.criticalCount.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground mt-1">발견된 악성 스미싱</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
            <CardTitle className="text-sm font-medium">최근 트렌드</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.recentTrend}</div>
            <p className="text-xs text-muted-foreground mt-1">스미싱 탐지율 동향</p>
          </CardContent>
        </Card>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>위험도별 분포</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-center">
            <div className="rounded-lg p-4 border bg-card"><div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full" style={{ backgroundColor: `${getRiskColor("safe")}20`, color: getRiskColor("safe") }}><ShieldCheck className="h-5 w-5" /></div><div className="mt-3 text-2xl font-bold">{stats.safeCount}</div><div className="text-xs text-muted-foreground font-medium">안전</div></div>
            <div className="rounded-lg p-4 border bg-card"><div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full" style={{ backgroundColor: `${getRiskColor("low")}20`, color: getRiskColor("low") }}><ShieldCheck className="h-5 w-5" /></div><div className="mt-3 text-2xl font-bold">{stats.lowCount}</div><div className="text-xs text-muted-foreground font-medium">주의</div></div>
            <div className="rounded-lg p-4 border bg-card"><div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full" style={{ backgroundColor: `${getRiskColor("medium")}20`, color: getRiskColor("medium") }}><AlertTriangle className="h-5 w-5" /></div><div className="mt-3 text-2xl font-bold">{stats.mediumCount}</div><div className="text-xs text-muted-foreground font-medium">경고</div></div>
            <div className="rounded-lg p-4 border bg-card"><div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full" style={{ backgroundColor: `${getRiskColor("high")}20`, color: getRiskColor("high") }}><ShieldAlert className="h-5 w-5" /></div><div className="mt-3 text-2xl font-bold">{stats.highCount}</div><div className="text-xs text-muted-foreground font-medium">위험</div></div>
            <div className="rounded-lg p-4 border bg-card"><div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full" style={{ backgroundColor: `${getRiskColor("critical")}20`, color: getRiskColor("critical") }}><Skull className="h-5 w-5" /></div><div className="mt-3 text-2xl font-bold">{stats.criticalCount}</div><div className="text-xs text-muted-foreground font-medium">매우 위험</div></div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
