import express from "express";
import { createServer as createViteServer } from "vite";
import path from "path";
import axios from "axios";

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
      const response = await axios.get(url, {
        headers: {
          "User-Agent": "Mozilla/5.0 (compatible; ghostprod-bot/0.1; +https://ghostprod.io)",
        },
        timeout: 10000,
      });
      res.json({ html: response.data });
    } catch (error: any) {
      console.error("Fetch error:", error);
      res.status(500).json({ error: "Failed to fetch URL. " + (error.message || "") });
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
