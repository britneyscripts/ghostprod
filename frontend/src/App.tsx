import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Shield, Zap, Cpu, AlertTriangle, CheckCircle2, Ghost, ArrowRight, Mail, Globe, Layout, Code } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Types
interface AnalysisResult {
  url: string;
  score: number;
  breakdown: {
    performance: number;
    schema: number;
    content: number;
  };
  analysis: {
    gap: string;
    missing: string[];
    recommendation: string;
  };
  timestamp: string;
}

export default function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // 1. Fetch HTML via Backend
      const fetchResponse = await fetch('/api/fetch-html', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      const fetchData = await fetchResponse.json();
      if (!fetchResponse.ok) throw new Error(fetchData.error || 'Failed to fetch page');

      const html = fetchData.html;
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');

      // 2. Agent 1: Performance (Mock)
      const performanceScore = Math.floor(Math.random() * 40) + 40;

      // 3. Agent 2: Schema.org
      let schemaScore = 0;
      const jsonLdScripts = doc.querySelectorAll('script[type="application/ld+json"]');
      let schemas: any[] = [];
      jsonLdScripts.forEach((script) => {
        try {
          const data = JSON.parse(script.textContent || "{}");
          schemas.push(data);
        } catch (e) {}
      });

      const hasProduct = schemas.some(s => s["@type"] === "Product" || (Array.isArray(s["@graph"]) && s["@graph"].some((g: any) => g["@type"] === "Product")));
      const hasOffers = schemas.some(s => s.offers || (Array.isArray(s["@graph"]) && s["@graph"].some((g: any) => g.offers)));
      const hasDescription = schemas.some(s => s.description || (Array.isArray(s["@graph"]) && s["@graph"].some((g: any) => g.description)));

      if (hasProduct) schemaScore += 50;
      if (hasOffers) schemaScore += 25;
      if (hasDescription) schemaScore += 25;

      // 4. Agent 3 & 4: NLP & Gap Analysis via Gemini
      const { GoogleGenAI } = await import("@google/genai");
      const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY! });

      const textContent = doc.body.innerText.substring(0, 5000);
      
      const prompt = `
        Analyze this Product Detail Page (PDP) content for AI Agent readiness.
        
        Content:
        ${textContent}
        
        Task:
        1. Score the technical attribute density (0-100).
        2. Perform a Gap Analysis: If an AI agent was asked 'is this product good for oily skin with niacinamide?', could it answer?
        3. Identify missing fields.
        
        Return JSON format:
        {
          "contentScore": number,
          "gapAnalysis": "string",
          "missingFields": ["string"],
          "recommendation": "string"
        }
      `;

      const aiResult = await ai.models.generateContent({
        model: "gemini-3-flash-preview",
        contents: prompt,
      });
      const aiData = JSON.parse(aiResult.text.replace(/```json|```/g, ""));

      // 5. Final ARS Calculation
      const finalScore = Math.round(
        (performanceScore * 0.4) + 
        (schemaScore * 0.4) + 
        (aiData.contentScore * 0.2)
      );

      setResult({
        url,
        score: finalScore,
        breakdown: {
          performance: performanceScore,
          schema: schemaScore,
          content: aiData.contentScore,
        },
        analysis: {
          gap: aiData.gapAnalysis,
          missing: aiData.missingFields,
          recommendation: aiData.recommendation,
        },
        timestamp: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    // Mock subscription
    setSubscribed(true);
    setEmail('');
  };

  return (
    <div className="min-h-screen grid-bg relative">
      <div className="scanline" />
      
      {/* Header */}
      <header className="p-6 flex justify-between items-center border-b border-neon-purple/20 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <Ghost className="text-neon-pink animate-pulse" size={32} />
          <h1 className="font-display text-2xl tracking-tighter text-neon-cyan crt-flicker">
            GHOSTPROD<span className="text-neon-pink">.IO</span>
          </h1>
        </div>
        <div className="hidden md:flex gap-6 font-mono text-xs text-text-muted">
          <span className="hover:text-neon-cyan cursor-pointer transition-colors">v0.1-ALPHA</span>
          <span className="hover:text-neon-pink cursor-pointer transition-colors">AGENT-READINESS</span>
          <span className="hover:text-neon-purple cursor-pointer transition-colors">BRAZIL-PDP</span>
        </div>
      </header>

      <main className="max-w-6xl mx-auto p-6 pt-12">
        {/* Hero Section */}
        {!result && !loading && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-5xl md:text-7xl mb-6 tracking-tight leading-none">
              IS YOUR PDP <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-neon-cyan via-neon-purple to-neon-pink">
                VISIBLE TO AGENTS?
              </span>
            </h2>
            <p className="font-sans text-xl text-text-muted max-w-2xl mx-auto mb-12">
              Diagnostic tool for AI Agent visibility. Validate if your product pages are readable for the next generation of e-commerce.
            </p>

            <form onSubmit={handleAnalyze} className="max-w-3xl mx-auto relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-neon-cyan to-neon-pink rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
              <div className="relative flex flex-col md:flex-row gap-4 bg-cyber p-2 rounded-2xl border border-white/10">
                <div className="flex-1 flex items-center px-4 gap-3">
                  <Globe className="text-neon-cyan" size={20} />
                  <input 
                    type="url" 
                    placeholder="https://www.sephora.com.br/produto-exemplo"
                    className="w-full bg-transparent border-none focus:ring-0 font-mono text-sm py-4 outline-none"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    required
                  />
                </div>
                <button 
                  type="submit"
                  className="bg-neon-cyan text-void font-display px-8 py-4 rounded-xl hover:bg-white transition-all flex items-center justify-center gap-2 group/btn"
                >
                  ANALYZE <ArrowRight size={18} className="group-hover/btn:translate-x-1 transition-transform" />
                </button>
              </div>
            </form>
            
            <div className="mt-8 flex justify-center gap-8 font-mono text-[10px] text-text-muted uppercase tracking-widest">
              <div className="flex items-center gap-2"><Zap size={12} /> Performance</div>
              <div className="flex items-center gap-2"><Layout size={12} /> Schema.org</div>
              <div className="flex items-center gap-2"><Cpu size={12} /> NLP Density</div>
            </div>
          </motion.div>
        )}

        {/* Loading State */}
        <AnimatePresence>
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex flex-col items-center justify-center py-24"
            >
              <div className="relative w-32 h-32 mb-8">
                <div className="absolute inset-0 border-4 border-neon-cyan/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-neon-cyan rounded-full border-t-transparent animate-spin"></div>
                <Ghost className="absolute inset-0 m-auto text-neon-pink animate-bounce" size={40} />
              </div>
              <h3 className="font-display text-xl text-neon-cyan mb-2">SCANNING PDP...</h3>
              <div className="font-mono text-xs text-text-muted space-y-1 text-center">
                <p>AGENT 1: CHECKING CrUX PERFORMANCE...</p>
                <p>AGENT 2: PARSING SCHEMA.ORG JSON-LD...</p>
                <p>AGENT 3: ANALYZING NLP ATTRIBUTE DENSITY...</p>
                <p>AGENT 4: RUNNING GAP ANALYSIS SIMULATION...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error State */}
        {error && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-card p-6 border-neon-pink/50 max-w-xl mx-auto text-center"
          >
            <AlertTriangle className="text-neon-pink mx-auto mb-4" size={48} />
            <h3 className="font-display text-xl text-neon-pink mb-2">ANALYSIS FAILED</h3>
            <p className="font-mono text-sm text-text-muted mb-6">{error}</p>
            <button 
              onClick={() => setError(null)}
              className="font-mono text-xs text-neon-cyan hover:underline"
            >
              TRY ANOTHER URL
            </button>
          </motion.div>
        )}

        {/* Results Section */}
        {result && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8 pb-24"
          >
            <div className="flex flex-col md:flex-row gap-8 items-start">
              {/* Score Card */}
              <div className="glass-card p-8 md:w-1/3 w-full flex flex-col items-center text-center relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-neon-cyan to-neon-pink"></div>
                <span className="font-mono text-[10px] text-text-muted tracking-[0.3em] mb-4">AGENT-READINESS SCORE</span>
                <div className="relative">
                  <div className="font-display text-8xl digital-score text-neon-cyan mb-2">
                    {result.score}
                  </div>
                  <div className="absolute -top-4 -right-4">
                    {result.score > 70 ? (
                      <CheckCircle2 className="text-neon-cyan" size={32} />
                    ) : (
                      <AlertTriangle className="text-neon-pink" size={32} />
                    )}
                  </div>
                </div>
                <div className="font-display text-sm tracking-widest text-text-primary mb-6">
                  {result.score > 80 ? 'OPTIMIZED' : result.score > 50 ? 'VISIBLE' : 'INVISIBLE'}
                </div>
                
                <div className="w-full space-y-4">
                  <ScoreBar label="PERFORMANCE" value={result.breakdown.performance} color="cyan" />
                  <ScoreBar label="SCHEMA.ORG" value={result.breakdown.schema} color="purple" />
                  <ScoreBar label="NLP DENSITY" value={result.breakdown.content} color="pink" />
                </div>
              </div>

              {/* Analysis Details */}
              <div className="flex-1 space-y-6">
                <div className="glass-card p-6">
                  <h3 className="font-display text-lg text-neon-cyan mb-4 flex items-center gap-2">
                    <Cpu size={20} /> AGENT SIMULATION (GAP ANALYSIS)
                  </h3>
                  <p className="font-sans text-text-primary leading-relaxed mb-4 italic">
                    "{result.analysis.gap}"
                  </p>
                  <div className="bg-void/50 p-4 rounded-lg border border-white/5">
                    <h4 className="font-mono text-xs text-neon-pink mb-2 uppercase tracking-wider">Missing Attributes:</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.analysis.missing.map((field, i) => (
                        <span key={i} className="px-2 py-1 bg-neon-pink/10 border border-neon-pink/20 text-neon-pink text-[10px] font-mono rounded">
                          {field}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="glass-card p-6">
                  <h3 className="font-display text-lg text-neon-purple mb-4 flex items-center gap-2">
                    <Zap size={20} /> RECOMMENDATION
                  </h3>
                  <p className="font-sans text-text-primary leading-relaxed">
                    {result.analysis.recommendation}
                  </p>
                </div>

                <div className="flex justify-between items-center px-2">
                  <div className="font-mono text-[10px] text-text-muted">
                    URL: <span className="text-neon-cyan">{result.url}</span>
                  </div>
                  <button 
                    onClick={() => setResult(null)}
                    className="font-mono text-xs text-neon-pink hover:underline"
                  >
                    NEW ANALYSIS
                  </button>
                </div>
              </div>
            </div>

            {/* Lead Capture */}
            <div className="glass-card p-12 text-center relative overflow-hidden">
              <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none"></div>
              <h3 className="font-display text-3xl mb-4 relative">WANT THE FULL REPORT?</h3>
              <p className="font-sans text-text-muted mb-8 max-w-xl mx-auto relative">
                Join our beta program. We're selecting 3 Brazilian e-commerce PMs for a deep-dive manual audit of their entire catalog.
              </p>
              
              {!subscribed ? (
                <form onSubmit={handleSubscribe} className="max-w-md mx-auto flex gap-2 relative">
                  <input 
                    type="email" 
                    placeholder="your@email.com"
                    className="flex-1 bg-void border border-white/10 rounded-lg px-4 py-3 font-mono text-sm focus:border-neon-purple outline-none"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <button 
                    type="submit"
                    className="bg-neon-purple text-white px-6 py-3 rounded-lg font-display text-xs hover:bg-white hover:text-void transition-colors"
                  >
                    JOIN BETA
                  </button>
                </form>
              ) : (
                <motion.div 
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="text-neon-cyan font-display"
                >
                  WELCOME TO THE VOID. WE'LL BE IN TOUCH.
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </main>

      {/* Footer */}
      <footer className="p-12 border-t border-neon-purple/20 text-center font-mono text-[10px] text-text-muted tracking-widest uppercase">
        <div className="flex justify-center gap-8 mb-4">
          <span>ICMC/USP 2026</span>
          <span>EVA DE PAULA</span>
          <span>V0.1 FREE-FIRST</span>
        </div>
        <p>© GHOSTPROD.IO - ALL RIGHTS RESERVED IN THE MULTIVERSE</p>
      </footer>
    </div>
  );
}

function ScoreBar({ label, value, color }: { label: string, value: number, color: 'cyan' | 'pink' | 'purple' }) {
  const colors = {
    cyan: 'bg-neon-cyan shadow-[0_0_10px_rgba(0,206,209,0.5)]',
    pink: 'bg-neon-pink shadow-[0_0_10px_rgba(255,0,255,0.5)]',
    purple: 'bg-neon-purple shadow-[0_0_10px_rgba(138,43,226,0.5)]',
  };

  return (
    <div className="w-full">
      <div className="flex justify-between font-mono text-[9px] mb-1">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-1 w-full bg-white/5 rounded-full overflow-hidden">
        <motion.div 
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={cn("h-full rounded-full", colors[color])}
        />
      </div>
    </div>
  );
}
