import { Sidebar, SidebarContent, SidebarHeader, SidebarMenu, SidebarMenuItem, SidebarMenuButton, SidebarProvider, SidebarGroup, SidebarGroupContent } from "@/components/ui/sidebar";
import { Link, useLocation } from "wouter";
import { ShieldCheck, History, BarChart3 } from "lucide-react";

export function Layout({ children }: { children: React.ReactNode }) {
  const [location] = useLocation();

  const pageTitle =
    location === "/" ? "스미싱 분석" :
    location === "/history" ? "분석 기록" :
    "통계";

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <Sidebar>
          <SidebarHeader className="p-4">
            <div className="flex items-center gap-2.5 font-bold text-base text-primary-foreground tracking-tight">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
                <ShieldCheck className="h-4.5 w-4.5" />
              </div>
              <span className="text-[15px] font-extrabold">SmishGuard</span>
            </div>
          </SidebarHeader>
          <SidebarContent>
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location === "/"}>
                      <Link href="/">
                        <ShieldCheck className="h-4 w-4" />
                        <span className="font-semibold">스미싱 분석</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location === "/history"}>
                      <Link href="/history">
                        <History className="h-4 w-4" />
                        <span className="font-semibold">분석 기록</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                  <SidebarMenuItem>
                    <SidebarMenuButton asChild isActive={location === "/stats"}>
                      <Link href="/stats">
                        <BarChart3 className="h-4 w-4" />
                        <span className="font-semibold">통계</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>
        </Sidebar>

        <main className="flex-1 flex flex-col min-w-0">
          <header className="sticky top-0 z-10 flex h-14 items-center gap-4 border-b bg-background/98 px-6 backdrop-blur-sm shadow-sm">
            <h1 className="text-[17px] font-bold tracking-tight text-foreground">
              {pageTitle}
            </h1>
          </header>
          <div className="flex-1 p-6 overflow-auto">
            <div className="mx-auto max-w-5xl page-enter">
              {children}
            </div>
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}
