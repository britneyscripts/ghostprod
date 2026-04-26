import "dotenv/config";
import "newrelic";
import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
// safeFetch: workaround para replicar o comportamento de erro do Axios com fetch nativo
async function safeFetch(url: string, options: RequestInit = {}) {
  const response = await fetch(url, {
    ...options,
    signal: AbortSignal.timeout(10000),
  });

  if (!response.ok) {
    const error = new Error(`Erro HTTP! Status: ${response.status}`);
    (error as any).status = response.status;
    throw error;
  }

  return response;
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // Agent-Readiness Score (ARS) Calculation
  // Weights: 40 (Performance) / 40 (Schema) / 20 (Content)
  
  app.post("/api/fetch-html", async (req, res) => {
    const { url } = req.body;
    if (!url) return res.status(400).json({ error: "URL is required" });

    try {
      const response = await safeFetch(url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
          "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
          "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        },
      });

      const html = await response.text();
      res.json({ html });
    } catch (error: any) {
      console.error("Erro na coleta ghostprod:", error.message);

      const status = error.status || 500;
      res.status(status).json({
        error: `Falha ao acessar PDP: ${error.message}`,
        ars_status: "incompleto",
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
