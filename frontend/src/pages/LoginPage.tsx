import React, { useState, useEffect } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock } from "lucide-react";
import AuthCard from "../components/auth/AuthCard";
import AuthInput from "../components/auth/AuthInput";
import AuthButton from "../components/auth/AuthButton";
import GoogleSignInButton from "../components/auth/GoogleSignInButton";
import { useAuthStore } from "../store/authStore";

// ---------------------------------------------------------------------------
// Animated left panel
// ---------------------------------------------------------------------------
const CinematicPanel: React.FC = () => (
  <div className="hidden lg:flex lg:flex-1 relative overflow-hidden items-center justify-center">
    {/* Base gradient */}
    <div
      className="absolute inset-0"
      style={{
        background:
          "linear-gradient(135deg, #0a0a0f 0%, #110d1f 40%, #0d1020 100%)",
      }}
    />

    {/* Deep radial glow */}
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0"
      style={{
        background:
          "radial-gradient(ellipse 80% 70% at 40% 50%, rgba(139,92,246,0.18) 0%, transparent 65%), radial-gradient(ellipse 50% 50% at 70% 80%, rgba(59,130,246,0.12) 0%, transparent 60%)",
      }}
    />

    {/* Noise texture */}
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-[0.035]"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
      }}
    />

    {/* Floating orbs */}
    {[
      { size: 380, top: "8%",  left: "10%",  color: "rgba(139,92,246,0.07)",  dur: 9  },
      { size: 260, top: "55%", left: "55%",  color: "rgba(59,130,246,0.07)",  dur: 11 },
      { size: 200, top: "30%", left: "65%",  color: "rgba(52,211,153,0.05)",  dur: 7  },
      { size: 140, top: "75%", left: "15%",  color: "rgba(251,146,60,0.05)",  dur: 13 },
    ].map((orb, i) => (
      <motion.div
        key={i}
        animate={{ y: [0, -24, 0], scale: [1, 1.06, 1] }}
        transition={{ duration: orb.dur, repeat: Infinity, ease: "easeInOut" }}
        className="absolute rounded-full blur-3xl"
        style={{
          width: orb.size,
          height: orb.size,
          top: orb.top,
          left: orb.left,
          backgroundColor: orb.color,
        }}
      />
    ))}

    {/* Star particles */}
    <div aria-hidden className="pointer-events-none absolute inset-0">
      {Array.from({ length: 40 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full bg-white"
          style={{
            width: Math.random() * 2 + 1,
            height: Math.random() * 2 + 1,
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            opacity: Math.random() * 0.4 + 0.1,
          }}
          animate={{ opacity: [null, 0.05, Math.random() * 0.5 + 0.1] }}
          transition={{
            duration: Math.random() * 3 + 2,
            repeat: Infinity,
            repeatType: "reverse",
            delay: Math.random() * 4,
          }}
        />
      ))}
    </div>

    {/* Central content */}
    <div className="relative z-10 px-12 max-w-md space-y-8 text-center">
      {/* Logo */}
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, delay: 0.1 }}
        className="flex flex-col items-center gap-3"
      >
        <div
          className="w-16 h-16 rounded-2xl bg-violet-600 flex items-center justify-center"
          style={{
            boxShadow: "0 0 40px rgba(139,92,246,0.6), 0 0 80px rgba(139,92,246,0.3)",
          }}
        >
          <span className="text-white font-black text-3xl leading-none select-none">N</span>
        </div>
        <span className="text-2xl font-black tracking-tight text-white" style={{ letterSpacing: "0.1em" }}>
          NEBULA
        </span>
      </motion.div>

      {/* Headline */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.25 }}
        className="space-y-3"
      >
        <h2 className="text-3xl sm:text-4xl font-black text-white leading-tight">
          Your story.<br />
          <span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage: "linear-gradient(135deg,#a78bfa 0%,#60a5fa 50%,#34d399 100%)",
            }}
          >
            Infinite paths.
          </span>
        </h2>
        <p className="text-sm text-gray-400 leading-relaxed max-w-xs mx-auto">
          Step into AI-powered worlds where every choice reshapes the narrative.
        </p>
      </motion.div>

      {/* Feature pills */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="flex flex-wrap justify-center gap-2"
      >
        {["AI Narratives", "Genres", "Multiple Branches", "Your Choices Matter"].map((tag) => (
          <span
            key={tag}
            className="px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest"
            style={{
              backgroundColor: "rgba(139,92,246,0.1)",
              border: "1px solid rgba(139,92,246,0.25)",
              color: "#a78bfa",
            }}
          >
            {tag}
          </span>
        ))}
      </motion.div>
    </div>
  </div>
);

// ---------------------------------------------------------------------------
// Login Form
// ---------------------------------------------------------------------------
interface FormErrors {
  email?: string;
  password?: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { signIn, user, actionLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  // Redirect once authenticated
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/dashboard";
  useEffect(() => {
    if (user) navigate(from, { replace: true });
  }, [user, navigate, from]);

  // Clear store error when inputs change
  useEffect(() => {
    if (error) clearError();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [email, password]);

  const validate = (): boolean => {
    const errs: FormErrors = {};
    if (!email.trim()) errs.email = "Email is required.";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Enter a valid email.";
    if (!password) errs.password = "Password is required.";
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await signIn(email, password);
  };

  return (
    <div
      className="min-h-screen flex"
      style={{ backgroundColor: "#0a0a0f" }}
    >
      {/* ── Left: cinematic panel ────────────────────────────────────── */}
      <CinematicPanel />

      {/* ── Right: form panel ────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col items-center justify-center px-6 py-12 relative">
        {/* Subtle bg gradient */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 60% 50% at 50% 100%, rgba(139,92,246,0.06) 0%, transparent 70%)",
          }}
        />

        {/* Mobile logo */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="lg:hidden flex items-center gap-2.5 mb-8"
        >
          <div
            className="w-9 h-9 rounded-xl bg-violet-600 flex items-center justify-center"
            style={{ boxShadow: "0 0 20px rgba(139,92,246,0.5)" }}
          >
            <span className="text-white font-black text-lg leading-none">N</span>
          </div>
          <span className="text-lg font-black tracking-widest text-white">NEBULA</span>
        </motion.div>

        <div className="relative z-10 w-full max-w-md">
          <AuthCard>
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.15 }}
              className="mb-8 space-y-1"
            >
              <h1 className="text-2xl font-black text-white">Welcome back</h1>
              <p className="text-sm text-gray-500">Sign in to continue your story</p>
            </motion.div>

            {/* Global Firebase error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-5 px-4 py-3 rounded-xl text-sm text-red-300 font-medium"
                style={{
                  backgroundColor: "rgba(239,68,68,0.08)",
                  border: "1px solid rgba(239,68,68,0.25)",
                }}
              >
                {error}
              </motion.div>
            )}

            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              <AuthInput
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={formErrors.email}
                icon={<Mail size={15} />}
                autoComplete="email"
              />

              <AuthInput
                label="Password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={formErrors.password}
                icon={<Lock size={15} />}
                autoComplete="current-password"
              />

              <div className="pt-1">
                <AuthButton type="submit" loading={actionLoading}>
                  Sign In
                </AuthButton>
              </div>
            </form>

            {/* Divider */}
            <div className="my-5 flex items-center gap-3">
              <div className="flex-1 h-px" style={{ backgroundColor: "rgba(255,255,255,0.06)" }} />
              <span className="text-[11px] font-semibold uppercase tracking-widest text-gray-600">or</span>
              <div className="flex-1 h-px" style={{ backgroundColor: "rgba(255,255,255,0.06)" }} />
            </div>

            <GoogleSignInButton />

            {/* Footer link */}
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-6 text-center text-sm text-gray-500"
            >
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="font-semibold text-violet-400 hover:text-violet-300 transition-colors"
              >
                Create one
              </Link>
            </motion.p>
          </AuthCard>

          {/* Back to landing */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-6 text-center"
          >
            <Link
              to="/"
              className="text-xs text-gray-600 hover:text-gray-400 transition-colors inline-flex items-center gap-1.5"
            >
              ← Back to home
            </Link>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
