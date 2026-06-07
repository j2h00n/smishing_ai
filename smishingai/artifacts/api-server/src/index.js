import { createServer } from "http";

const PORT = process.env.API_PORT || 3001;
const AI_PORT = process.env.AI_PORT || 3002;

const db = {
  analyses: [],
  nextId: 1,
};

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  });
  res.end(JSON.stringify(data));
}

async function callAI(message) {
  const body = JSON.stringify({ message });
  return new Promise((resolve, reject) => {
    import("http").then(({ default: http }) => {
      const req = http.request(
        { hostname: "localhost", port: AI_PORT, path: "/ai/analyze", method: "POST",
          headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) } },
        (res) => {
          let data = "";
          res.on("data", (chunk) => { data += chunk; });
          res.on("end", () => {
            try { resolve(JSON.parse(data)); }
            catch (e) { reject(new Error("AI 서버 응답 파싱 실패")); }
          });
        }
      );
      req.on("error", reject);
      req.write(body);
      req.end();
    });
  });
}

function getStats() {
  const analyses = db.analyses;
  const counts = { safe: 0, low: 0, medium: 0, high: 0, critical: 0 };
  for (const a of analyses) counts[a.riskLevel] = (counts[a.riskLevel] || 0) + 1;

  const total = analyses.length;
  let recentTrend = "데이터 없음";
  if (total >= 5) {
    const recent = analyses.slice(-5);
    const avg = recent.reduce((s, a) => s + a.riskScore, 0) / recent.length;
    recentTrend = avg >= 70 ? "증가 추세 ↑" : avg >= 40 ? "보통 수준 →" : "낮은 수준 ↓";
  } else if (total > 0) {
    recentTrend = "분석 중";
  }

  return {
    totalAnalyzed: total,
    safeCount: counts.safe,
    lowCount: counts.low,
    mediumCount: counts.medium,
    highCount: counts.high,
    criticalCount: counts.critical,
    recentTrend,
  };
}

const server = createServer((req, res) => {
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    });
    res.end();
    return;
  }

  const url = new URL(req.url, `http://localhost:${PORT}`);

  if (req.method === "POST" && url.pathname === "/api/smishing/analyze") {
    let body = "";
    req.on("data", (chunk) => { body += chunk; });
    req.on("end", async () => {
      try {
        const { message } = JSON.parse(body);
        if (!message || typeof message !== "string" || !message.trim()) {
          return sendJSON(res, 400, { error: "message is required" });
        }

        const t0 = Date.now();
        const aiResult = await callAI(message.trim());
        const analysisTime = ((Date.now() - t0) / 1000).toFixed(2);

        const preview = message.length > 100 ? message.slice(0, 97) + "..." : message;
        const entry = {
          id: db.nextId++,
          message,
          url: null,
          riskScore: Math.round(aiResult.score),
          riskLevel: aiResult.riskLevel,
          reasons: aiResult.reasons,
          messagePreview: preview,
          analyzedAt: new Date().toISOString(),
          categoryScores: aiResult.categoryScores || {},
          weights: aiResult.weights || {},
          weightedContributions: aiResult.weightedContributions || {},
          weightedSum: aiResult.weightedSum ?? null,
          biases: aiResult.biases || {},
          finalBias: aiResult.finalBias ?? null,
          categoryDescriptions: aiResult.categoryDescriptions || {},
          analysisTime: parseFloat(analysisTime),
        };
        db.analyses.unshift(entry);
        sendJSON(res, 200, entry);
      } catch (e) {
        console.error("분석 오류:", e.message);
        sendJSON(res, 500, { error: "AI 분석 중 오류가 발생했습니다: " + e.message });
      }
    });
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/smishing/history") {
    const items = db.analyses.slice(0, 50).map((a) => ({
      id: a.id,
      messagePreview: a.messagePreview,
      riskScore: a.riskScore,
      riskLevel: a.riskLevel,
      analyzedAt: a.analyzedAt,
      url: a.url,
    }));
    sendJSON(res, 200, items);
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/smishing/stats") {
    sendJSON(res, 200, getStats());
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/health") {
    sendJSON(res, 200, { status: "ok" });
    return;
  }

  sendJSON(res, 404, { error: "Not found" });
});

server.listen(PORT, "localhost", () => {
  console.log(`API 서버 실행 중: http://localhost:${PORT}`);
});
