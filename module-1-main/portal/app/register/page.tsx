"use client"

import type React from "react"
import { useState } from "react"
import Link from "next/link"
import { EyeIcon, EyeSlashIcon, UserIcon, EnvelopeIcon } from "@heroicons/react/24/solid"
import { ShieldCheck, UserPlus, ArrowRight, Brain, Fingerprint, Database, GitBranch } from "@phosphor-icons/react"
import { FaLock } from "react-icons/fa"

const API_BASE = "http://127.0.0.1:5000/api"

export default function RegisterPage() {
  const [username, setUsername] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPass, setShowPass] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError("")
    setSuccess("")

    try {
      const resp = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      })
      const data = await resp.json()
      if (resp.ok) {
        setSuccess(`✅ Account '${username}' created! Redirecting to login...`)
        setTimeout(() => { window.location.href = "/" }, 1500)
      } else {
        setError(data.error || "Registration failed")
      }
    } catch {
      setError("Network error: Backend unreachable")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="relative min-h-screen bg-[#020502] text-white flex flex-col font-sans overflow-hidden">
      
      {/* BACKGROUND */}
      <div 
        className="absolute inset-0 z-0 opacity-40 bg-cover bg-center bg-no-repeat"
        style={{ 
          backgroundImage: `url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&q=80&w=3000')`,
          filter: 'hue-rotate(60deg) saturate(1.5)'
        }}
      />
      <div className="absolute inset-0 z-0 bg-gradient-to-tr from-[#020502] via-[#020502]/80 to-transparent" />
      <div className="absolute inset-0 z-0 opacity-10"
        style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='70' viewBox='0 0 40 70'%3E%3Cpath d='M20 46.2L0 35V11.2L20 0l20 11.2V35L20 46.2z' fill='none' stroke='%2300ff41' stroke-width='0.5'/%3E%3C/svg%3E\")" }} 
      />

      <header className="relative z-20 flex items-center justify-between px-12 py-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#00ff41] rounded-xl flex items-center justify-center shadow-[0_0_20px_rgba(0,255,65,0.4)]">
            <ShieldCheck size={28} weight="bold" className="text-black" />
          </div>
          <span className="text-xl font-bold tracking-tighter uppercase flex gap-1">
            <span>FUSION</span><span className="text-[#00ff41]">GRAPH</span>
          </span>
        </div>
        <Link href="/">
          <button className="px-6 py-2 bg-[#00e63a] hover:bg-[#00ff41] text-black font-bold rounded-xl transition-all">
            Login
          </button>
        </Link>
      </header>

      <main className="relative z-10 flex-1 flex items-center justify-center px-4 py-10">
        <div className="w-full max-w-lg">
          <div className="bg-[#020a02]/80 backdrop-blur-2xl border border-green-500/20 rounded-[40px] p-10 relative shadow-[0_40px_100px_rgba(0,0,0,0.8)]">
            <div className="h-1 w-full absolute top-0 left-0 rounded-t-[40px]" style={{ background: "linear-gradient(90deg, #10b981, #008f11, #00ff41)" }} />
            
            <div className="flex flex-col items-center gap-6 mt-4">
              <div className="w-20 h-20 bg-green-500/20 rounded-3xl flex items-center justify-center shadow-[0_0_40px_rgba(0,255,65,0.15)] overflow-hidden">
                <UserPlus size={40} className="text-[#00ff41]" weight="duotone" />
              </div>
              
              <div className="text-center">
                <h2 className="text-3xl font-bold tracking-tight">Access Protocol</h2>
                <p className="text-gray-500 text-sm mt-2">Initialize your operative profile</p>
              </div>

              {error && <div className="w-full p-4 bg-red-500/10 border border-red-500/30 rounded-2xl text-red-400 text-xs">{error}</div>}
              {success && <div className="w-full p-4 bg-green-500/10 border border-green-500/30 rounded-2xl text-green-400 text-xs">{success}</div>}

              <form onSubmit={handleRegister} className="w-full flex flex-col gap-5">
                <div className="relative">
                  <UserIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required
                    className="w-full bg-[#051105] border border-green-500/10 rounded-2xl py-4 pl-12 pr-4 text-sm text-white" />
                </div>
                <div className="relative">
                  <EnvelopeIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input type="email" placeholder="Email Address" value={email} onChange={e => setEmail(e.target.value)} required
                    className="w-full bg-[#051105] border border-green-500/10 rounded-2xl py-4 pl-12 pr-4 text-sm text-white" />
                </div>
                <div className="relative">
                  <FaLock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input type={showPass ? "text" : "password"} placeholder="Cipher Secret (Password)" value={password} onChange={e => setPassword(e.target.value)} required
                    className="w-full bg-[#051105] border border-green-500/10 rounded-2xl py-4 pl-12 pr-12 text-sm text-white" />
                  <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500">
                    {showPass ? <EyeSlashIcon className="w-5 h-5" /> : <EyeIcon className="w-5 h-5" />}
                  </button>
                </div>

                <button type="submit" disabled={isLoading}
                  className="w-full bg-[#00ff41] hover:bg-[#20ff56] py-5 rounded-3xl text-black font-extrabold flex items-center justify-center gap-3 transition-all mt-4"
                >
                  {isLoading ? 'INITIATING...' : <><UserPlus size={20} weight="bold" /> Create Account <ArrowRight size={20} weight="bold" /></>}
                </button>
              </form>
            </div>
          </div>
        </div>
      </main>

      <footer className="relative z-20 px-12 py-8 text-[10px] font-bold text-gray-700 tracking-[0.4em] uppercase text-center">
         © 2026 FUSION GRAPH OPERATIONS HUB
      </footer>
    </div>
  )
}
