"use client"

import type React from "react"
import { useState } from "react"
import Link from "next/link"
import { EyeIcon, EyeSlashIcon, UserIcon, LockClosedIcon } from "@heroicons/react/24/solid"
import { Brain, Fingerprint, ArrowRight, Database, GameController, WifiHigh, ShieldCheck, GitBranch } from "@phosphor-icons/react"
import { FaShieldAlt, FaLock } from "react-icons/fa"
import { BiNetworkChart } from "react-icons/bi"
import { MdSecurity } from "react-icons/md"

const API_BASE = "http://127.0.0.1:5000/api"

export default function LoginPage() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [showPass, setShowPass] = useState(false)
  const [remember, setRemember] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")

    try {
      const resp = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })
      const data = await resp.json()
      if (resp.ok) {
        localStorage.setItem("token", data.access_token)
        localStorage.setItem("user", JSON.stringify(data.user))
        window.location.href = `http://localhost:8501/?token=${data.access_token}`
      } else {
        setError(data.error || "Authentication failed")
      }
    } catch {
      setError("Network error: Backend unreachable")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-[#020502] text-white flex flex-col font-sans overflow-hidden">
      
      {/* ── BACKGROUND LAYER ──────────────────────────────────────────────── */}
      <div 
        className="absolute inset-0 z-0 opacity-40 bg-cover bg-center bg-no-repeat"
        style={{ 
          backgroundImage: `url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=3000')`,
          filter: 'hue-rotate(60deg) saturate(1.5)'
        }}
      />
      <div className="absolute inset-0 z-0 bg-gradient-to-tr from-[#020502] via-[#020502]/80 to-transparent" />
      
      {/* Subtle Hex Pattern */}
      <div className="absolute inset-0 z-0 opacity-10"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='70' viewBox='0 0 40 70'%3E%3Cpath d='M20 46.2L0 35V11.2L20 0l20 11.2V35L20 46.2z' fill='none' stroke='%2300ff41' stroke-width='0.5'/%3E%3C/svg%3E\")" }} 
      />

      {/* ── HEADER ───────────────────────────────────────────────────────── */}
      <header className="relative z-20 flex items-center justify-between px-12 py-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#00ff41] rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(0,255,65,0.4)]">
            <ShieldCheck size={28} weight="bold" className="text-black" />
          </div>
          <span className="text-xl font-bold tracking-tighter uppercase flex gap-1">
            <span>FUSION</span><span className="text-[#00ff41]">GRAPH</span>
          </span>
        </div>

        <nav className="hidden md:flex items-center gap-10 text-sm font-medium text-gray-400">
          <Link href="#" className="hover:text-white transition-colors">Home</Link>
          <Link href="#" className="hover:text-white transition-colors">About</Link>
          <Link href="#" className="hover:text-white transition-colors">Features</Link>
          <Link href="#" className="hover:text-white transition-colors">Contact</Link>
        </nav>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/30 text-[10px] font-bold text-[#00ff41] tracking-widest">
            <div className="w-2 h-2 rounded-full bg-[#00ff41] animate-pulse" />
            SECURE
          </div>
          <Link href="/register">
            <button className="px-6 py-2 bg-[#00e63a] hover:bg-[#00ff41] text-black font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(0,255,65,0.3)]">
              Register
            </button>
          </Link>
        </div>
      </header>

      {/* ── HERO CONTENT ─────────────────────────────────────────────────── */}
      <main className="relative z-10 flex-1 flex items-center justify-between px-20 max-w-[1600px] mx-auto w-full gap-16">
        
        {/* LEFT SECTION */}
        <div className="flex-1 flex flex-col gap-8">
          <div className="flex items-center gap-2 text-[#00ff41] text-xs font-bold tracking-[0.3em] uppercase">
             <ShieldCheck size={16} /> 
             AI CYBERSECURITY PLATFORM
          </div>
          <h1 className="text-7xl font-bold leading-[1.1]">
            Secure Your<br />
            <span className="text-[#00ff41]">Digital Network</span>
          </h1>
          <p className="text-gray-400 text-lg leading-relaxed max-w-xl">
            NEURAHASH — Cross-domain AI knowledge mapping platform for cybersecurity intelligence, threat detection, and network analysis.
          </p>

          <div className="flex flex-col gap-5 mt-4">
            {[
              { icon: <Brain size={24} weight="duotone" />, label: "AI-Powered Threat Intelligence" },
              { icon: <GitBranch size={24} weight="duotone" />, label: "Threat Intelligence Analysis" },
              { icon: <Fingerprint size={24} weight="duotone" />, label: "JWT Secured Authentication" },
              { icon: <Database size={24} weight="duotone" />, label: "Encrypted Data Vault" },
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-4 group">
                <div className="w-12 h-12 rounded-xl bg-green-500/10 border border-green-500/20 flex items-center justify-center text-[#00ff41] group-hover:scale-110 transition-transform">
                  {feature.icon}
                </div>
                <span className="text-gray-300 font-medium">{feature.label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* RIGHT SECTION — LOGIN CARD */}
        <div className="w-[500px] flex justify-end">
          <div className="w-full bg-[#020a02]/80 backdrop-blur-2xl border border-green-500/20 rounded-[40px] p-10 relative shadow-[0_40px_100px_rgba(0,0,0,0.8)]">
            
            <div className="absolute inset-0 rounded-[40px] border border-green-500/10 pointer-events-none" />
            
            <div className="flex flex-col items-center gap-6">
              <div className="w-20 h-20 bg-green-500/20 rounded-3xl flex items-center justify-center shadow-[0_0_40px_rgba(0,255,65,0.15)] overflow-hidden relative group">
                <div className="absolute inset-0 bg-gradient-to-tr from-green-500/20 to-transparent" />
                <LockClosedIcon className="w-10 h-10 text-[#00ff41]" />
              </div>
              
              <div className="text-center">
                <h2 className="text-3xl font-bold tracking-tight">Sign In</h2>
                <p className="text-gray-500 text-sm mt-2">Access your Fusion Graph dashboard</p>
              </div>

              {error && (
                <div className="w-full p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400 text-sm flex items-center gap-2">
                   <ShieldCheck size={20} className="rotate-180" /> {error}
                </div>
              )}

              <form onSubmit={handleLogin} className="w-full flex flex-col gap-6">
                <div className="flex flex-col gap-2">
                  <label className="text-[#00ff41] text-[10px] font-bold tracking-widest uppercase ml-1">Username or Email</label>
                  <div className="relative">
                    <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input 
                      type="text"
                      placeholder="Enter username or email"
                      value={username}
                      onChange={e => setUsername(e.target.value)}
                      required
                      className="w-full bg-[#051105] border border-green-500/10 rounded-2xl py-4 pl-12 pr-4 text-sm text-white focus:border-green-500/40 focus:bg-[#081a08] transition-all outline-none"
                    />
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-[#00ff41] text-[10px] font-bold tracking-widest uppercase ml-1">Password</label>
                  <div className="relative">
                    <FaLock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input 
                      type={showPass ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={e => setPassword(e.target.value)}
                      required
                      className="w-full bg-[#051105] border border-green-500/10 rounded-2xl py-4 pl-12 pr-12 text-sm text-white focus:border-green-500/40 focus:bg-[#081a08] transition-all outline-none"
                    />
                    <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors">
                      {showPass ? <EyeSlashIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between px-1">
                  <label className="flex items-center gap-3 cursor-pointer group text-sm text-gray-400">
                    <input type="checkbox" checked={remember} onChange={e => setRemember(e.target.checked)} className="hidden" />
                    <div className={`w-5 h-5 rounded-md border border-green-500/30 flex items-center justify-center transition-all ${remember ? 'bg-green-500 border-green-500' : 'bg-transparent'}`}>
                       {remember && <ArrowRight size={14} className="text-black rotate-[-45deg]" />}
                    </div>
                    Remember me
                  </label>
                  <Link href="#" className="text-sm font-semibold text-[#00ff41]/80 hover:text-[#00ff41] transition-colors">Forgot Password?</Link>
                </div>

                <button 
                  type="submit" 
                  disabled={isLoading}
                  className="w-full bg-[#00ff41] hover:bg-[#20ff56] py-5 rounded-3xl text-black font-extrabold flex items-center justify-center gap-3 transition-all hover:scale-[1.02] shadow-[0_15px_30px_rgba(0,255,65,0.25)]"
                >
                  {isLoading ? 'HANDSHAKING...' : <><ShieldCheck size={20} weight="bold" /> Sign In <ArrowRight size={20} weight="bold" /></>}
                </button>
              </form>

              <div className="w-full flex flex-col items-center gap-6 mt-2">
                 <div className="w-full h-[1px] bg-gradient-to-r from-transparent via-green-500/20 to-transparent relative">
                    <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-[#020a02] px-3 text-[9px] font-bold text-gray-600 tracking-[0.2em] uppercase">Secured By</span>
                 </div>
                 
                 <div className="flex gap-4">
                    {[
                      { icon: <FaShieldAlt />, label: "AES-256" },
                      { icon: <BiNetworkChart />, label: "JWT Auth" },
                      { icon: <MdSecurity />, label: "TLS 1.3" },
                    ].map((badge, i) => (
                      <div key={i} className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/5 border border-green-500/20 text-[9px] font-bold text-gray-400">
                        <span className="text-green-500/60">{badge.icon}</span>
                        {badge.label}
                      </div>
                    ))}
                 </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className="relative z-20 px-12 py-8 flex justify-between items-center text-[10px] font-bold text-gray-700 tracking-[0.4em] uppercase">
         <div>© 2026 FUSION GRAPH OPERATIONS</div>
         <div className="flex gap-8">
            <Link href="#">System Status</Link>
            <Link href="#">Privacy Protocol</Link>
            <Link href="#">Terms of Access</Link>
         </div>
      </footer>
    </div>
  )
}
