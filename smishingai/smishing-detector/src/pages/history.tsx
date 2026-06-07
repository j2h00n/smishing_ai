import { useState } from "react";
import { useGetSmishingHistory } from "@workspace/api-client-react";
import { format } from "date-fns";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Separator } from "@/components/ui/separator";
import { getRiskColor, getRiskBgClass, getRiskLabel, getRiskSummary } from "@/lib/utils-risk";
import { AlertCircle, Link, CalendarDays, ChartNoAxesColumn, ShieldAlert } from "lucide-react";

export default function History() {
  const { data: history, isLoading, error } = useGetSmishingHistory();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const selected = history?.find((item: { id: number }) => item.id === selectedId) ?? null;

  if (error) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg border border-destructive bg-destructive/10 text-destructive">
        <div className="flex flex-col items-center gap-2">
          <AlertCircle className="h-8 w-8" />
          <p>기록을 불러오는 중 오류가 발생했습니다.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>분석 기록</CardTitle>
          <CardDescription>최근 분석한 스미싱 내역을 클릭해서 상세하게 확인합니다.</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
              <Skeleton className="h-16 w-full" />
            </div>
          ) : history && history.length > 0 ? (
            <div className="rounded-md border overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-[140px]">분석 일시</TableHead>
                    <TableHead>문자 내용 요약</TableHead>
                    <TableHead className="w-[100px] text-right">위험도 점수</TableHead>
                    <TableHead className="w-[100px] text-center">결과</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {history.map((item: { id: number; analyzedAt: string; messagePreview: string; riskScore: number; riskLevel: any }) => (
                    <TableRow key={item.id} className="cursor-pointer hover:bg-muted/60" onClick={() => setSelectedId(item.id)}>
                      <TableCell className="text-sm text-muted-foreground">
                        {format(new Date(item.analyzedAt), "yyyy-MM-dd HH:mm")}
                      </TableCell>
                      <TableCell className="font-medium">
                        <div className="line-clamp-1 max-w-[400px]" title={item.messagePreview}>
                          {item.messagePreview}
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-mono">{item.riskScore}</TableCell>
                      <TableCell className="text-center">
                        <Badge style={{ backgroundColor: getRiskColor(item.riskLevel), color: "white" }} variant="outline" className="border-transparent">
                          {getRiskLabel(item.riskLevel)}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-4 mb-4">
                <AlertCircle className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium text-foreground mb-1">분석 기록이 없습니다</h3>
              <p className="text-sm text-muted-foreground">
                첫 번째 스미싱 분석을 진행해보세요.
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={!!selected} onOpenChange={(open) => !open && setSelectedId(null)}>
        <DialogContent className="max-w-3xl">
          {selected && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <ChartNoAxesColumn className="h-5 w-5 text-primary" />
                  기록 상세 보기
                </DialogTitle>
                <DialogDescription>이 분석이 어떤 방식으로 기록되었는지 확인할 수 있습니다.</DialogDescription>
              </DialogHeader>
              <div className={`rounded-xl border p-4 ${getRiskBgClass(selected.riskLevel)}`}>
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm text-muted-foreground">위험도 점수</p>
                    <p className="text-3xl font-black" style={{ color: getRiskColor(selected.riskLevel) }}>
                      {selected.riskScore}
                    </p>
                  </div>
                  <Badge className="text-white border-0" style={{ backgroundColor: getRiskColor(selected.riskLevel) }}>
                    {getRiskLabel(selected.riskLevel)}
                  </Badge>
                </div>
                <p className="mt-3 text-sm leading-relaxed text-foreground/80">
                  {getRiskSummary(selected.riskLevel, selected.riskScore)}
                </p>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div className="rounded-lg border p-4 space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold">
                    <CalendarDays className="h-4 w-4" /> 분석 시각
                  </div>
                  <p className="text-sm text-muted-foreground">{format(new Date(selected.analyzedAt), "yyyy-MM-dd HH:mm:ss")}</p>
                </div>
                <div className="rounded-lg border p-4 space-y-2">
                  <div className="flex items-center gap-2 text-sm font-semibold">
                    <ShieldAlert className="h-4 w-4" /> 기록 ID
                  </div>
                  <p className="text-sm text-muted-foreground">#{selected.id}</p>
                </div>
              </div>
              <div className="space-y-3">
                <h4 className="text-sm font-bold flex items-center gap-2">
                  <Link className="h-4 w-4" /> 기록된 문자 요약
                </h4>
                <div className="rounded-lg border bg-muted/30 p-4 text-sm leading-relaxed whitespace-pre-wrap">
                  {selected.messagePreview}
                </div>
              </div>
              <Separator />
              <div className="space-y-3">
                <h4 className="text-sm font-bold">기록 방식</h4>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  이 항목은 최근 분석 기록에 저장된 결과로, 문자 요약과 점수, 위험 등급이 함께 보관됩니다.
                  목록에서는 짧게 보이지만, 이 상세 화면에서 어떤 기준으로 위험하다고 판단했는지 더 명확하게 확인할 수 있습니다.
                </p>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
