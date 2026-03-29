import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Search, Shield, Zap, Cpu, AlertTriangle, CheckCircle2, Ghost, ArrowRight, Mail, Globe, Layout, Code } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Types - Ajustados para bater com o seu Backend Python
interface AnalysisResult {
  url: string;
  score: number;
  breakdown: {
    crux: number;
    pagespeed: number;
    schema: number;
    content: number;
  };
  // NOVO: scores individuais do Lighthouse
  lighthouse?: {
    performance: number;
    accessibility: number;
    best_practices: number;
    seo: number;
  };
  // NOVO: qualidade do Schema.org
  schema_quality?: {
    structure: number;
    quality: number;
    problemas: string[];
    campos_faltando: string[];
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
      const apiBase = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiBase}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Falha na análise do backend');
      }

      setResult({
        url: data.url,
        score: data.ars || 0,
        breakdown: {
          crux: data.agentes?.crux?.score || 0,
          pagespeed: data.agentes?.pagespeed?.score || 0,
          schema: data.agentes?.schema?.score || 0,
          content: data.agentes?.conteudo?.score || 0,
        },
        // NOVO: extrai scores individuais do Lighthouse
        lighthouse: {
          performance: data.agentes?.pagespeed?.score || 0,
          accessibility: data.agentes?.pagespeed?.accessibility_score || 0,
          best_practices: data.agentes?.pagespeed?.best_practices_score || 0,
          seo: data.agentes?.pagespeed?.seo_score || 0,
        },
        // NOVO: extrai qualidade do Schema
        schema_quality: {
          structure: data.agentes?.schema_quality?.structure_score || data.agentes?.schema?.score || 0,
          quality: data.agentes?.schema_quality?.quality_score || data.agentes?.schema?.score || 0,
          problemas: data.agentes?.schema_quality?.problemas || [],
          campos_faltando: data.agentes?.schema_quality?.campos_faltando || [],
        },
        analysis: {
          gap: data.agentes?.gap_analysis?.analise || data.agentes?.gap_analysis?.motivo || "Análise indisponível",
          missing: data.agentes?.gap_analysis?.campos_faltando || [],
          recommendation: data.recomendacoes?.[0] || "Otimize os metadados técnicos.",
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
            <h2 className="font-display text-5xl md:text-7xl mb-6 tracking-tight leading-none text-white">
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
              <div className="relative flex flex-col md:flex-row gap-4 bg-cyber p-2 rounded-2xl border border-white/10 text-white">
                <div className="flex-1 flex items-center px-4 gap-3">
                  <Globe className="text-neon-cyan" size={20} />
                  <input
                    type="url"
                    placeholder="https://www.natura.com.br/p/seu-produto"
                    className="w-full bg-transparent border-none focus:ring-0 font-mono text-sm py-4 outline-none text-white"
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
              <h3 className="font-display text-xl text-neon-cyan mb-2 tracking-widest">SCANNING PDP...</h3>
              <div className="font-mono text-xs text-text-muted space-y-1 text-center uppercase">
                <p>AGENT 1: CHECKING PAGESPEED METRICS...</p>
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
            <h3 className="font-display text-xl text-neon-pink mb-2 uppercase">Analysis Failed</h3>
            <p className="font-mono text-sm text-text-muted mb-6 uppercase">{error}</p>
            <button
              onClick={() => setError(null)}
              className="font-mono text-xs text-neon-cyan hover:underline uppercase"
            >
              Try another URL
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
              <div className="glass-card p-8 md:w-1/3 w-full flex flex-col items-center text-center relative overflow-hidden bg-void/50 border border-white/10">
                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-neon-cyan to-neon-pink"></div>
                <span className="font-mono text-[10px] text-text-muted tracking-[0.3em] mb-4 uppercase">Agent-Readiness Score</span>
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
                <div className="font-display text-sm tracking-widest text-text-primary mb-6 uppercase">
                  {result.score > 80 ? 'OPTIMIZED' : result.score > 50 ? 'VISIBLE' : 'INVISIBLE'}
                </div>

                <div className="w-full space-y-4">
                  <ScoreBar label="CrUX (FIELD DATA)" value={result.breakdown.crux} color="cyan" />

                  {/* PAGESPEED EXPANDIDO - 4 cards individuais com bolinhas */}
                  <div className="w-full">
                    <div className="font-mono text-[9px] mb-3 text-text-muted">PAGESPEED (LAB DATA)</div>
                    <div className="grid grid-cols-2 gap-3">
                      <CircularScore
                        label="Performance"
                        value={result.lighthouse?.performance || 0}
                      />
                      <CircularScore
                        label="Accessibility"
                        value={result.lighthouse?.accessibility || 0}
                      />
                      <CircularScore
                        label="Best Practices"
                        value={result.lighthouse?.best_practices || 0}
                      />
                      <CircularScore
                        label="SEO"
                        value={result.lighthouse?.seo || 0}
                      />
                    </div>
                  </div>

                  {/* SCHEMA.ORG EXPANDIDO - Structure + Quality */}
                  <div className="w-full">
                    <div className="font-mono text-[9px] mb-3 text-text-muted flex items-center justify-between">
                      <span>SCHEMA.ORG</span>
                      <span className="text-neon-purple">{result.breakdown.schema}%</span>
                    </div>

                    {/* Sub-scores do Schema */}
                    <div className="bg-void/30 rounded-lg p-3 space-y-2 border border-white/5">
                      <div className="flex justify-between items-center">
                        <span className="font-mono text-[8px] text-text-muted uppercase">✓ Estrutura válida</span>
                        <span className="font-mono text-[8px] text-neon-cyan">{result.schema_quality?.structure || result.breakdown.schema}%</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="font-mono text-[8px] text-text-muted uppercase">
                          {result.schema_quality?.quality >= 70 ? '✓' : '⚠️'} Qualidade de dados
                        </span>
                        <span className={`font-mono text-[8px] ${(result.schema_quality?.quality || 0) >= 70 ? 'text-neon-cyan' : 'text-neon-pink'
                          }`}>
                          {result.schema_quality?.quality || result.breakdown.schema}%
                        </span>
                      </div>

                      {/* Problemas encontrados */}
                      {result.schema_quality?.problemas && result.schema_quality.problemas.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-white/5">
                          <div className="font-mono text-[7px] text-neon-pink mb-1 uppercase">Problemas:</div>
                          {result.schema_quality.problemas.slice(0, 2).map((problema, i) => (
                            <div key={i} className="font-mono text-[7px] text-text-muted mb-1">
                              • {problema}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>

                  <ScoreBar label="NLP DENSITY" value={result.breakdown.content} color="pink" />
                </div>
              </div>

              {/* Analysis Details */}
              <div className="flex-1 space-y-6">
                <div className="glass-card p-6 bg-void/50 border border-white/10">
                  <div className="flex items-start gap-3 mb-4">
                    <Cpu size={20} className="text-neon-cyan mt-1" />
                    <div>
                      <h3 className="font-display text-lg text-neon-cyan uppercase">
                        Agent Simulation (Gap Analysis)
                      </h3>
                      <p className="font-mono text-[10px] text-text-muted mt-1 uppercase tracking-wider">
                        Simulação: Agente de compras real tentando responder query do usuário
                      </p>
                    </div>
                  </div>

                  <p className="font-sans text-text-primary leading-relaxed mb-4 italic">
                    "{result.analysis.gap}"
                  </p>

                  <div className="bg-void/80 p-4 rounded-lg border border-white/5">
                    <h4 className="font-mono text-xs text-neon-pink mb-3 uppercase tracking-wider flex items-center gap-2">
                      Missing in Schema.org:
                      <span className="text-[10px] text-text-muted normal-case">(campos que deveriam estar estruturados)</span>
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.analysis.missing.length > 0 ? (
                        result.analysis.missing.map((field, i) => (
                          <span key={i} className="px-2 py-1 bg-neon-pink/10 border border-neon-pink/20 text-neon-pink text-[10px] font-mono rounded uppercase">
                            {field}
                          </span>
                        ))
                      ) : (
                        <span className="text-[10px] text-neon-cyan font-mono">✓ Nenhum campo crítico faltando</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="glass-card p-6 bg-void/50 border border-white/10">
                  <h3 className="font-display text-lg text-neon-purple mb-4 flex items-center gap-2 uppercase">
                    <Code size={20} /> Recomendação Específica
                  </h3>
                  <p className="font-sans text-text-primary leading-relaxed mb-4">
                    {result.analysis.recommendation}
                  </p>

                  {/* Código Schema.org de exemplo */}
                  {result.analysis.missing.length > 0 && (
                    <div className="bg-void/80 p-4 rounded-lg border border-neon-purple/20 font-mono text-xs">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-neon-purple text-[10px] uppercase tracking-wider">
                          Adicione ao Schema.org JSON-LD:
                        </span>
                        <span className="text-neon-cyan text-[10px]">
                          Impacto estimado: +{result.analysis.missing.length * 15}% NLP
                        </span>
                      </div>
                      <pre className="text-[10px] text-text-muted overflow-x-auto">
                        {`"additionalProperty": [
${result.analysis.missing.map((field, i) =>
                          `  {
    "@type": "PropertyValue",
    "name": "${field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}",
    "value": "Especifique aqui"
  }${i < result.analysis.missing.length - 1 ? ',' : ''}`
                        ).join('\n')}
]`}
                      </pre>
                    </div>
                  )}
                </div>

                <div className="flex justify-between items-center px-2">
                  <div className="font-mono text-[10px] text-text-muted truncate max-w-[250px]">
                    URL: <span className="text-neon-cyan">{result.url}</span>
                  </div>
                  <button
                    onClick={() => setResult(null)}
                    className="font-mono text-xs text-neon-pink hover:underline uppercase"
                  >
                    New Analysis
                  </button>
                </div>
              </div>
            </div>

            {/* Lead Capture */}
            <div className="glass-card p-12 text-center relative overflow-hidden bg-void/50 border border-white/10">
              <div className="absolute inset-0 grid-bg opacity-20 pointer-events-none"></div>
              <h3 className="font-display text-3xl mb-4 relative uppercase text-white">Want the Full Report?</h3>
              <p className="font-sans text-text-muted mb-8 max-w-xl mx-auto relative uppercase text-xs tracking-widest">
                Join our beta program. We're selecting 3 Brazilian e-commerce PMs for a deep-dive manual audit.
              </p>

              {!subscribed ? (
                <form onSubmit={handleSubscribe} className="max-w-md mx-auto flex gap-2 relative">
                  <input
                    type="email"
                    placeholder="your@email.com"
                    className="flex-1 bg-void border border-white/10 rounded-lg px-4 py-3 font-mono text-sm focus:border-neon-purple outline-none text-white"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                  />
                  <button
                    type="submit"
                    className="bg-neon-purple text-white px-6 py-3 rounded-lg font-display text-xs hover:bg-white hover:text-void transition-colors uppercase"
                  >
                    Join Beta
                  </button>
                </form>
              ) : (
                <motion.div
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="text-neon-cyan font-display uppercase tracking-widest"
                >
                  Welcome to the Void. We'll be in touch.
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </main>

      {/* Footer */}
      <footer className="p-12 border-t border-neon-purple/20 text-center font-mono text-[10px] text-text-muted tracking-widest uppercase bg-void/30 backdrop-blur-md">
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
      <div className="flex justify-between font-mono text-[9px] mb-1 text-text-muted">
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

// NOVO COMPONENTE: Circular Progress como no PageSpeed Insights
function CircularScore({ label, value }: { label: string, value: number }) {
  // Cores baseadas no score (igual ao Lighthouse)
  const getColor = (score: number) => {
    if (score >= 90) return '#0cce6b'; // Verde
    if (score >= 50) return '#ffa400'; // Laranja
    return '#ff4e42'; // Vermelho
  };

  const color = getColor(value);
  const radius = 20;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-14 h-14">
        <svg className="transform -rotate-90 w-14 h-14">
          {/* Background circle */}
          <circle
            cx="28"
            cy="28"
            r={radius}
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="3"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx="28"
            cy="28"
            r={radius}
            stroke={color}
            strokeWidth="3"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={circumference}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1, ease: "easeOut" }}
            strokeLinecap="round"
          />
        </svg>
        <div
          className="absolute inset-0 flex items-center justify-center font-mono text-sm font-bold"
          style={{ color }}
        >
          {value}
        </div>
      </div>
      <span className="font-mono text-[8px] text-text-muted uppercase text-center leading-tight">
        {label}
      </span>
    </div>
  );
}
