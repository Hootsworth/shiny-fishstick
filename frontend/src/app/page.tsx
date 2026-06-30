"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Play, 
  Terminal, 
  Check, 
  Copy, 
  Moon, 
  Sun, 
  ChevronRight, 
  Cpu, 
  ShieldCheck, 
  Sparkles,
  GitBranch,
  Settings,
  HelpCircle,
  Code
} from 'lucide-react';

export default function LandingPage() {
  const [copied, setCopied] = useState(false);
  const [activeLang, setActiveLang] = useState<'py' | 'ts' | 'rs'>('py');
  const [theme, setTheme] = useState<'light' | 'dark'>('light');

  // Initialize theme from localStorage or document class
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const initialTheme = savedTheme || 'light';
    setTheme(initialTheme);
    document.documentElement.setAttribute('data-theme', initialTheme);
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    localStorage.setItem('theme', nextTheme);
    document.documentElement.setAttribute('data-theme', nextTheme);
  };

  const copyInstallCmd = () => {
    navigator.clipboard.writeText("pip install shiny-fishstick");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // SVG Pie Shape component
  const PieSlice = ({ className, size = 100, color = 'var(--pie-green)' }: { className?: string; size?: number; color?: string }) => (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      className={`pie-shape ${className}`}
      style={{ color }}
    >
      {/* Circle with a bite/slice missing */}
      <path 
        d="M50,50 L50,10 A40,40 0 1,1 10,50 L50,50 Z" 
        fill="currentColor"
        opacity="0.85"
      />
    </svg>
  );

  const CircleRing = ({ className, size = 80, color = 'var(--ink)' }: { className?: string; size?: number; color?: string }) => (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      className={`pie-shape ${className}`}
      style={{ color }}
    >
      <circle 
        cx="50" 
        cy="50" 
        r="40" 
        stroke="currentColor" 
        strokeWidth="6" 
        fill="none" 
        opacity="0.4"
      />
    </svg>
  );

  return (
    <div className="min-h-screen relative flex flex-col overflow-hidden">
      {/* Background ambient shapes */}
      <PieSlice size={450} className="top-[-100px] right-[-150px] opacity-10 animate-float-slow text-[var(--pie-green)]" />
      <CircleRing size={300} className="bottom-[-100px] left-[-100px] opacity-10 animate-float" />
      <PieSlice size={120} className="top-[35%] left-[5%] opacity-15 animate-float text-[var(--ink)]" />
      <CircleRing size={80} className="top-[60%] right-[10%] opacity-20 animate-float-slow text-[var(--pie-green)]" />

      {/* Floating Pill Nav */}
      <div className="w-full flex justify-center px-4 py-6 z-50">
        <header className="max-w-[850px] w-full flex items-center justify-between bg-[var(--ink)] text-[var(--cream)] px-6 py-3.5 rounded-full border border-[var(--line)] shadow-lg backdrop-blur-md bg-opacity-95">
          <div className="flex items-center gap-2.5">
            <svg width="24" height="24" viewBox="0 0 100 100" className="text-[var(--pie-green)] fill-current">
              <path d="M50,50 L50,10 A40,40 0 1,1 10,50 L50,50 Z" />
            </svg>
            <span className="font-extrabold tracking-tight text-sm uppercase">PREFLIGHT</span>
          </div>
          
          <nav className="hidden md:flex items-center gap-8 text-xs font-semibold uppercase tracking-wider">
            <a href="#features" className="hover:text-[var(--pie-green)] transition">Features</a>
            <a href="#benchmarks" className="hover:text-[var(--pie-green)] transition">Benchmarks</a>
            <a href="#sdk" className="hover:text-[var(--pie-green)] transition">SDK Spec</a>
            <a href="https://github.com/Hootsworth/shiny-fishstick" target="_blank" className="hover:text-[var(--pie-green)] transition">GitHub</a>
          </nav>

          <div className="flex items-center gap-4">
            <button onClick={toggleTheme} className="text-[var(--cream)] hover:text-[var(--pie-green)] transition">
              {theme === 'light' ? <Moon className="h-4.5 w-4.5" /> : <Sun className="h-4.5 w-4.5" />}
            </button>
            <Link 
              href="/dashboard" 
              className="bg-[var(--pie-green)] hover:bg-[var(--pie-green-deep)] text-[var(--ink)] font-bold text-xs uppercase px-4 py-2 rounded-full tracking-wider transition-all duration-150"
            >
              Launch App
            </Link>
          </div>
        </header>
      </div>

      {/* Hero Section */}
      <main className="flex-grow z-10 max-w-[1180px] w-full mx-auto px-6 md:px-12 flex flex-col items-center pt-12 pb-24 text-center">
        {/* Release Ticket / Changelog Banner */}
        <div className="mb-8 group flex items-center gap-3 bg-[var(--paper)] border border-[var(--line)] px-4 py-2 rounded-full text-xs font-medium text-[var(--ink-soft)] shadow-sm hover:border-[var(--pie-green)] transition-all duration-200">
          <span className="bg-[var(--pie-green)] text-[var(--ink)] font-bold px-2 py-0.5 rounded-full text-[10px] uppercase">New Release</span>
          <span className="flex items-center gap-1">
            v0.1.0-alpha has landed on GitHub
            <ChevronRight className="h-3 w-3 group-hover:translate-x-0.5 transition-transform" />
          </span>
        </div>

        {/* Huge Headline */}
        <h1 className="display-title text-4xl sm:text-6xl md:text-[80px] text-[var(--ink)] tracking-tight max-w-[950px] mb-6">
          COMPILE WEBSITES INTO <br className="hidden sm:inline" />
          <span className="text-[var(--pie-green)]">SEMANTIC SDKs</span> FOR AI AGENTS
        </h1>

        {/* Subhead */}
        <p className="text-base sm:text-xl text-[var(--ink-soft)] max-w-[700px] mb-10 leading-relaxed">
          Stop asking LLMs to click buttons and reason over raw, unpredictable HTML. 
          Compile websites into typed APIs, client SDKs, and ready-to-run Model Context Protocol (MCP) servers.
        </p>

        {/* Hero Actions */}
        <div className="flex flex-col sm:flex-row items-center gap-4 mb-20 w-full sm:w-auto">
          <Link 
            href="/dashboard"
            className="w-full sm:w-auto text-center bg-[var(--ink)] hover:bg-[var(--pie-green)] hover:text-[var(--ink)] text-[var(--cream)] font-bold text-sm uppercase px-8 py-3.5 rounded-full tracking-wider transition-all duration-200 shadow-md flex items-center justify-center gap-2"
          >
            Launch Console <ChevronRight className="h-4 w-4" />
          </Link>
          
          {/* Terminal Install Pill */}
          <div 
            onClick={copyInstallCmd}
            className="w-full sm:w-auto flex items-center justify-between gap-6 bg-[var(--paper)] border border-[var(--line)] px-5 py-3.5 rounded-full font-mono text-xs text-[var(--ink)] hover:border-[var(--ink)] cursor-pointer transition shadow-sm relative group"
          >
            <span className="flex items-center gap-2.5">
              <span className="text-[var(--pie-green-deep)] select-none">$</span>
              <span>pip install shiny-fishstick</span>
            </span>
            <button className="text-[var(--ink-soft)] group-hover:text-[var(--ink)] transition">
              {copied ? <Check className="h-4 w-4 text-[var(--pie-green-deep)]" /> : <Copy className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* Interactive Dual Terminal Preview */}
        <section id="sdk" className="w-full max-w-[1000px] mb-28 text-left">
          <div className="bg-[var(--code-bg)] rounded-[24px] border border-[var(--line)] shadow-2xl overflow-hidden">
            {/* Window Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--ink-soft)] border-opacity-20 bg-[var(--code-bg)]">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-[#FF5F56]"></span>
                <span className="h-3 w-3 rounded-full bg-[#FFBD2E]"></span>
                <span className="h-3 w-3 rounded-full bg-[#27C93F]"></span>
              </div>
              <span className="text-[11px] font-mono text-[var(--code-text)] opacity-40 uppercase tracking-widest">Compiler Pipeline View</span>
              <div className="w-12"></div>
            </div>

            {/* Split Terminals */}
            <div className="flex flex-col lg:flex-row divide-y lg:divide-y-0 lg:divide-x divide-[var(--ink-soft)] divide-opacity-20">
              
              {/* Left pane: preflight.yaml */}
              <div className="flex-1 p-6 font-mono text-xs text-[var(--code-text)] overflow-x-auto min-h-[300px]">
                <div className="flex items-center justify-between mb-4 border-b border-[var(--ink-soft)] border-opacity-10 pb-2">
                  <span className="text-[10px] uppercase text-[var(--pie-green)] tracking-wider">Compiled Spec (preflight.yaml)</span>
                </div>
                <pre className="leading-relaxed">
                  <span className="text-gray-500">version:</span> 1.0.0<br />
                  <span className="text-gray-500">site:</span> https://shop.example.com<br />
                  <span className="text-gray-500">actions:</span><br />
                  &nbsp;&nbsp;<span className="text-blue-400">login:</span><br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">description:</span> Authenticates session<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">action_type:</span> browser<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">selector:</span> '#login-form'<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">parameters:</span><br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <span className="text-gray-500">name:</span> email<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">selector:</span> '#email'<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- <span className="text-gray-500">name:</span> password<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">selector:</span> '#password'<br />
                  &nbsp;&nbsp;<span className="text-blue-400">add_to_cart:</span><br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">description:</span> Upgraded REST interface<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">action_type:</span> api<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">api:</span><br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">url:</span> /api/cart/add<br />
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span className="text-gray-500">method:</span> POST
                </pre>
              </div>

              {/* Right pane: SDK Target code */}
              <div className="flex-1 p-6 font-mono text-xs text-[var(--code-text)] overflow-x-auto min-h-[300px]">
                <div className="flex items-center justify-between mb-4 border-b border-[var(--ink-soft)] border-opacity-10 pb-2">
                  <div className="flex gap-4">
                    <button 
                      onClick={() => setActiveLang('py')}
                      className={`text-[10px] uppercase tracking-wider pb-1 transition-all ${activeLang === 'py' ? 'text-[var(--pie-green)] border-b border-[var(--pie-green)]' : 'opacity-40 hover:opacity-85'}`}
                    >
                      Python
                    </button>
                    <button 
                      onClick={() => setActiveLang('ts')}
                      className={`text-[10px] uppercase tracking-wider pb-1 transition-all ${activeLang === 'ts' ? 'text-[var(--pie-green)] border-b border-[var(--pie-green)]' : 'opacity-40 hover:opacity-85'}`}
                    >
                      TypeScript
                    </button>
                    <button 
                      onClick={() => setActiveLang('rs')}
                      className={`text-[10px] uppercase tracking-wider pb-1 transition-all ${activeLang === 'rs' ? 'text-[var(--pie-green)] border-b border-[var(--pie-green)]' : 'opacity-40 hover:opacity-85'}`}
                    >
                      Rust
                    </button>
                  </div>
                  <span className="text-[9px] uppercase opacity-45">Generated Target SDK</span>
                </div>

                {activeLang === 'py' && (
                  <pre className="leading-relaxed">
                    <span className="text-pink-400">from</span> shared.specs.sdk <span className="text-pink-400">import</span> ShinyFishstickSiteSDK<br /><br />
                    site = ShinyFishstickSiteSDK(<span className="text-green-300">"https://shop.example.com"</span>)<br />
                    site.start(headless=<span className="text-yellow-400">True</span>)<br /><br />
                    <span className="text-gray-400"># 1. Native browser interaction</span><br />
                    site.login(email=<span className="text-green-300">"agent@preflight.com"</span>, password=<span className="text-green-300">"****"</span>)<br /><br />
                    <span className="text-gray-400"># 2. Automatically upgraded direct API request</span><br />
                    cart = site.add_to_cart(product_id=<span className="text-green-300">"42"</span>, quantity=<span className="text-yellow-400">1</span>)<br /><br />
                    site.close()<br />
                    <span className="text-pink-400">print</span>(<span className="text-green-300">"Cart contents:"</span>, cart)
                  </pre>
                )}

                {activeLang === 'ts' && (
                  <pre className="leading-relaxed">
                    <span className="text-pink-400">import</span> &#123; ShinyFishstickSiteSDK &#125; <span className="text-pink-400">from</span> <span className="text-green-300">'./specs/sdk'</span>;<br /><br />
                    <span className="text-pink-400">const</span> site = <span className="text-pink-400">new</span> ShinyFishstickSiteSDK(<span className="text-green-300">"https://shop.example.com"</span>);<br />
                    <span className="text-pink-400">await</span> site.start(&#123; headless: <span className="text-yellow-400">true</span> &#125;);<br /><br />
                    <span className="text-pink-400">await</span> site.login(<span className="text-green-300">"agent@preflight.com"</span>, <span className="text-green-300">"****"</span>);<br />
                    <span className="text-pink-400">const</span> cart = <span className="text-pink-400">await</span> site.addToCart(<span className="text-green-300">"42"</span>, <span className="text-yellow-400">1</span>);<br /><br />
                    <span className="text-pink-400">await</span> site.close();
                  </pre>
                )}

                {activeLang === 'rs' && (
                  <pre className="leading-relaxed">
                    <span className="text-pink-400">let</span> site = ShinySDK::new(<span className="text-green-300">"https://shop.example.com"</span>);<br />
                    site.start()?;<br /><br />
                    <span className="text-gray-400">// Rust SDK generates reqwest API call for add_to_cart</span><br />
                    <span className="text-pink-400">let</span> cart = site.add_to_cart(<span className="text-green-300">"42"</span>, <span className="text-yellow-400">1</span>);<br /><br />
                    println!(<span className="text-green-300">"Cart response: &#123;:?&#125;"</span>, cart);<br />
                    Ok(())
                  </pre>
                )}
              </div>

            </div>
          </div>
        </section>

        {/* Feature Grid */}
        <section id="features" className="w-full mb-28 border-t border-[var(--line)] pt-20">
          <div className="text-left mb-12">
            <h2 className="display-title text-3xl sm:text-5xl text-[var(--ink)] mb-4">Core Capabilities</h2>
            <p className="text-[var(--ink-soft)] text-sm max-w-[600px] leading-relaxed">
              Constructed specifically for modern developer pipelines to transition browser automation into semantic tool calls.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
            <div className="bg-[var(--paper)] p-8 rounded-[24px] border border-[var(--line)] shadow-sm hover:border-[var(--pie-green)] hover:-translate-y-1 transition duration-200">
              <div className="h-10 w-10 bg-[var(--cream)] rounded-full flex items-center justify-center mb-6 text-[var(--ink)]">
                <Play className="h-5 w-5 text-[var(--pie-green-deep)]" />
              </div>
              <h3 className="font-bold text-lg mb-3 uppercase tracking-tight text-[var(--ink)]">Redirect-Aware Crawler</h3>
              <p className="text-[var(--ink-soft)] text-sm leading-relaxed">
                Gracefully tracks and automates redirection chains, cookie serialization, and credentials states during page scanning runs.
              </p>
            </div>

            <div className="bg-[var(--paper)] p-8 rounded-[24px] border border-[var(--line)] shadow-sm hover:border-[var(--pie-green)] hover:-translate-y-1 transition duration-200">
              <div className="h-10 w-10 bg-[var(--cream)] rounded-full flex items-center justify-center mb-6 text-[var(--ink)]">
                <Cpu className="h-5 w-5 text-[var(--pie-green-deep)]" />
              </div>
              <h3 className="font-bold text-lg mb-3 uppercase tracking-tight text-[var(--ink)]">API Upgrade Sniffer</h3>
              <p className="text-[var(--ink-soft)] text-sm leading-relaxed">
                Captures network XHR/Fetch payloads in real time, upgrading slow GUI button-clicks to direct, lightning-fast REST calls automatically.
              </p>
            </div>

            <div className="bg-[var(--paper)] p-8 rounded-[24px] border border-[var(--line)] shadow-sm hover:border-[var(--pie-green)] hover:-translate-y-1 transition duration-200">
              <div className="h-10 w-10 bg-[var(--cream)] rounded-full flex items-center justify-center mb-6 text-[var(--ink)]">
                <ShieldCheck className="h-5 w-5 text-[var(--pie-green-deep)]" />
              </div>
              <h3 className="font-bold text-lg mb-3 uppercase tracking-tight text-[var(--ink)]">Selector Self-Healing</h3>
              <p className="text-[var(--ink-soft)] text-sm leading-relaxed">
                Monitors page structure changes across production and staging, automatically re-scoring and correcting drifted locators on the fly.
              </p>
            </div>
          </div>
        </section>

        {/* Playwright Comparative Benchmarks Section */}
        <section id="benchmarks" className="w-full mb-28 border-t border-[var(--line)] pt-20 text-left">
          <div className="mb-12">
            <h2 className="display-title text-3xl sm:text-5xl text-[var(--ink)] mb-4">VERIFIED BENCHMARKS</h2>
            <p className="text-[var(--ink-soft)] text-sm max-w-[600px] leading-relaxed">
              We compared direct Playwright scripting against Shiny Fishstick's compiled SDK calls across real production sites.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            
            {/* Table */}
            <div className="bg-[var(--paper)] rounded-[24px] border border-[var(--line)] shadow-sm overflow-hidden p-6">
              <h3 className="font-bold text-sm uppercase tracking-wider text-[var(--ink)] mb-6">Performance Comparison</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-[var(--line)] pb-2 text-[var(--ink-soft)] font-semibold uppercase tracking-wider">
                      <th className="py-3 pr-4">Metric</th>
                      <th className="py-3 px-4">Raw Playwright</th>
                      <th className="py-3 pl-4 text-[var(--pie-green-deep)]">Shiny Fishstick</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--line)]">
                    <tr>
                      <td className="py-4 pr-4 font-medium">Context Token Size (Average)</td>
                      <td className="py-4 px-4 text-gray-500">25,808 tokens</td>
                      <td className="py-4 pl-4 font-bold text-[var(--pie-green-deep)]">46 tokens (99.9% savings)</td>
                    </tr>
                    <tr>
                      <td className="py-4 pr-4 font-medium">Action Latency</td>
                      <td className="py-4 px-4 text-gray-500">1,444 ms</td>
                      <td className="py-4 pl-4 font-bold text-[var(--pie-green-deep)]">1.5 ms (950x faster)</td>
                    </tr>
                    <tr>
                      <td className="py-4 pr-4 font-medium">DOM Mutation Reliability</td>
                      <td className="py-4 px-4 text-gray-500">0% (breaks instantly)</td>
                      <td className="py-4 pl-4 font-bold text-[var(--pie-green-deep)]">100% (self-heals)</td>
                    </tr>
                    <tr>
                      <td className="py-4 pr-4 font-medium">Client Memory Overhead</td>
                      <td className="py-4 px-4 text-gray-500">1,642 KB</td>
                      <td className="py-4 pl-4 font-bold text-[var(--pie-green-deep)]">21 KB (99% reduction)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Explanatory text */}
            <div className="flex flex-col justify-center space-y-6">
              <h3 className="font-extrabold text-2xl uppercase tracking-tight text-[var(--ink)]">WHY COMPILING THE WEB MATTERS</h3>
              <p className="text-[var(--ink-soft)] text-sm leading-relaxed">
                AI agents browsing websites with Raw Playwright pay a massive token tax. Sending complete DOM page models or visual screenshots back and forth to an LLM is expensive, slow, and prone to breaking when CSS classes update.
              </p>
              <div className="p-5 bg-[var(--paper)] border border-[var(--line)] rounded-[20px] text-xs font-mono text-[var(--ink)]">
                <div className="flex items-center gap-2 mb-2 font-bold uppercase text-[var(--pie-green-deep)]">
                  <Sparkles className="h-4 w-4" />
                  Real-world Token savings
                </div>
                * Wikipedia Python article: 40,833 tokens ➔ 131 via API summary spec.<br />
                * GitHub repositories layout: 34,292 tokens ➔ 5 tokens via upgraded REST spec.
              </div>
            </div>

          </div>
        </section>

        {/* Trusted By / Logo Strip */}
        <section className="w-full mb-28 border-t border-[var(--line)] pt-12 flex flex-col items-center">
          <span className="text-[10px] uppercase tracking-widest text-[var(--ink-soft)] opacity-60 mb-6 font-semibold">Integrates with your agentic tech stack</span>
          <div className="flex flex-wrap justify-center items-center gap-12 grayscale opacity-45 hover:opacity-85 transition duration-300">
            <span className="font-bold tracking-tight text-sm uppercase mono-text">Playwright</span>
            <span className="font-bold tracking-tight text-sm uppercase mono-text">TypeScript</span>
            <span className="font-bold tracking-tight text-sm uppercase mono-text">FastAPI</span>
            <span className="font-bold tracking-tight text-sm uppercase mono-text">Ollama</span>
            <span className="font-bold tracking-tight text-sm uppercase mono-text">PostgreSQL</span>
          </div>
        </section>

        {/* Call to action */}
        <section className="w-full bg-[var(--ink)] text-[var(--cream)] rounded-[32px] p-12 text-center relative overflow-hidden border border-[var(--line)] shadow-xl">
          <PieSlice size={200} className="bottom-[-50px] right-[-50px] opacity-10 text-[var(--pie-green)]" />
          <h2 className="display-title text-3xl sm:text-5xl mb-4 tracking-tight">Ready to compile the web?</h2>
          <p className="text-gray-400 text-sm max-w-[550px] mx-auto mb-8 leading-relaxed">
            Create specs, inspect models, generate type-safe packages, and serve local MCP connections instantly using our developer UI.
          </p>
          <Link 
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-[var(--pie-green)] hover:bg-[var(--pie-green-deep)] text-[var(--ink)] font-bold text-xs uppercase px-8 py-3.5 rounded-full tracking-wider transition-all duration-150"
          >
            Open Developer Console <ChevronRight className="h-4 w-4" />
          </Link>
        </section>
      </main>

      {/* Footer */}
      <footer className="w-full bg-[var(--ink)] text-[var(--cream)] border-t border-[var(--line)] py-12 px-6 mt-auto z-10">
        <div className="max-w-[1180px] w-full mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <svg width="24" height="24" viewBox="0 0 100 100" className="text-[var(--pie-green)] fill-current">
              <path d="M50,50 L50,10 A40,40 0 1,1 10,50 L50,50 Z" />
            </svg>
            <span className="font-extrabold tracking-tight text-sm uppercase">PREFLIGHT</span>
          </div>

          <div className="flex items-center gap-6 text-xs text-gray-400">
            <a href="https://github.com/Hootsworth/shiny-fishstick/blob/main/LICENSE" target="_blank" className="hover:text-[var(--pie-green)] transition">Apache 2.0 License</a>
            <a href="mailto:adityapdixit2006@gmail.com" className="hover:text-[var(--pie-green)] transition">Security Report</a>
          </div>

          {/* Theme switch button in footer */}
          <button 
            onClick={toggleTheme} 
            className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider bg-[var(--cream)] bg-opacity-5 hover:bg-opacity-10 px-4 py-2 rounded-full border border-gray-800 transition"
          >
            {theme === 'light' ? (
              <>
                <Moon className="h-3.5 w-3.5" />
                <span>Dark Mode</span>
              </>
            ) : (
              <>
                <Sun className="h-3.5 w-3.5" />
                <span>Light Mode</span>
              </>
            )}
          </button>
        </div>
      </footer>
    </div>
  );
}