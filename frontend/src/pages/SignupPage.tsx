import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Mail, Lock, ShieldCheck } from "lucide-react";
import AuthCard from "../components/auth/AuthCard";
import AuthInput from "../components/auth/AuthInput";
import AuthButton from "../components/auth/AuthButton";
import GoogleSignInButton from "../components/auth/GoogleSignInButton";
import { useAuthStore } from "../store/authStore";

// ---------------------------------------------------------------------------
// Animated left panel (same cinematic style as LoginPage, different copy)
// ---------------------------------------------------------------------------
const CinematicPanel: React.FC = () => (
  <div className="hidden lg:flex lg:flex-1 relative overflow-hidden items-center justify-center">
    <div
      className="absolute inset-0"
      style={{
        background:
          "linear-gradient(135deg, #0a0a0f 0%, #0d1120 40%, #110d1f 100%)",
      }}
    />
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0"
      style={{
        background:
          "radial-gradient(ellipse 80% 70% at 60% 50%, rgba(59,130,246,0.15) 0%, transparent 65%), radial-gradient(ellipse 50% 50% at 20% 80%, rgba(52,211,153,0.1) 0%, transparent 60%)",
      }}
    />
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 opacity-[0.035]"
      style={{
        backgroundImage:
          "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
      }}
    />

    {[
      { size: 340, top: "12%", left: "8%",  color: "rgba(59,130,246,0.07)",  dur: 10 },
      { size: 220, top: "60%", left: "50%", color: "rgba(52,211,153,0.07)",  dur: 8  },
      { size: 180, top: "20%", left: "60%", color: "rgba(139,92,246,0.06)",  dur: 12 },
      { size: 130, top: "80%", left: "20%", color: "rgba(251,146,60,0.05)",  dur: 9  },
    ].map((orb, i) => (
      <motion.div
        key={i}
        animate={{ y: [0, -22, 0], scale: [1, 1.05, 1] }}
        transition={{ duration: orb.dur, repeat: Infinity, ease: "easeInOut" }}
        className="absolute rounded-full blur-3xl"
        style={{ width: orb.size, height: orb.size, top: orb.top, left: orb.left, backgroundColor: orb.color }}
      />
    ))}

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
            opacity: Math.random() * 0.3 + 0.08,
          }}
          animate={{ opacity: [null, 0.04, Math.random() * 0.45 + 0.08] }}
          transition={{
            duration: Math.random() * 3 + 2,
            repeat: Infinity,
            repeatType: "reverse",
            delay: Math.random() * 4,
          }}
        />
      ))}
    </div>

    <div className="relative z-10 px-12 max-w-md space-y-8 text-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.7, delay: 0.1 }}
        className="flex flex-col items-center gap-3"
      >
        <div
          className="w-16 h-16 rounded-2xl bg-violet-600 flex items-center justify-center"
          style={{ boxShadow: "0 0 40px rgba(139,92,246,0.6), 0 0 80px rgba(139,92,246,0.3)" }}
        >
          <span className="text-white font-black text-3xl leading-none select-none">N</span>
        </div>
        <span className="text-2xl font-black tracking-tight text-white" style={{ letterSpacing: "0.1em" }}>
          NEBULA
        </span>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.25 }}
        className="space-y-3"
      >
        <h2 className="text-3xl sm:text-4xl font-black text-white leading-tight">
          Begin your<br />
          <span
            className="bg-clip-text text-transparent"
            style={{ backgroundImage: "linear-gradient(135deg,#60a5fa 0%,#34d399 50%,#a78bfa 100%)" }}
          >
            adventure.
          </span>
        </h2>
        <p className="text-sm text-gray-400 leading-relaxed max-w-xs mx-auto">
          Create your account and start shaping stories that bend to your every choice.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="space-y-3"
      >
        {[
          { icon: "🎭", text: "Choose from immersive genres" },
          { icon: "🤖", text: "AI that adapts to every decision" },
          { icon: "🔀", text: "Every playthrough is unique" },
        ].map(({ icon, text }) => (
          <div
            key={text}
            className="flex items-center gap-3 text-left px-4 py-2.5 rounded-xl"
            style={{ backgroundColor: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.06)" }}
          >
            <span className="text-lg">{icon}</span>
            <span className="text-xs text-gray-300 font-medium">{text}</span>
          </div>
        ))}
      </motion.div>
    </div>
  </div>
);

// ---------------------------------------------------------------------------
// Password strength indicator
// ---------------------------------------------------------------------------
function getPasswordStrength(pw: string): { level: number; label: string; color: string } {
  if (pw.length === 0) return { level: 0, label: "", color: "" };
  if (pw.length < 6)   return { level: 1, label: "Too short",  color: "#ef4444" };
  if (pw.length < 8)   return { level: 2, label: "Weak",       color: "#f97316" };
  if (/[A-Z]/.test(pw) && /[0-9]/.test(pw)) return { level: 4, label: "Strong", color: "#22c55e" };
  return { level: 3, label: "Good", color: "#eab308" };
}

// ---------------------------------------------------------------------------
// Signup form
// ---------------------------------------------------------------------------
interface FormErrors {
  email?: string;
  password?: string;
  confirm?: string;
}

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const { signUp, user, actionLoading, error, clearError } = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  const strength = getPasswordStrength(password);

  useEffect(() => {
    if (user) navigate("/dashboard", { replace: true });
  }, [user, navigate]);

  useEffect(() => {
    if (error) clearError();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [email, password, confirm]);

  const validate = (): boolean => {
    const errs: FormErrors = {};
    if (!email.trim()) errs.email = "Email is required.";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = "Enter a valid email.";
    if (!password) errs.password = "Password is required.";
    else if (password.length < 6) errs.password = "Password must be at least 6 characters.";
    if (!confirm) errs.confirm = "Please confirm your password.";
    else if (password !== confirm) errs.confirm = "Passwords do not match.";
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    await signUp(email, password);
  };

  return (
    <div className="min-h-screen flex" style={{ backgroundColor: "#0a0a0f" }}>
      {/* ── Left panel ───────────────────────────────────────────────── */}
      <CinematicPanel />

      {/* ── Right panel ──────────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col items-center justify-center px-6 py-12 relative">
        <div
          aria-hidden
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              "radial-gradient(ellipse 60% 50% at 50% 0%, rgba(59,130,246,0.06) 0%, transparent 70%)",
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
              className="mb-7 space-y-1"
            >
              <h1 className="text-2xl font-black text-white">Create your account</h1>
              <p className="text-sm text-gray-500">Join Nebula and start your journey</p>
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

              <div className="space-y-2">
                <AuthInput
                  label="Password"
                  type="password"
                  placeholder="Min. 6 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  error={formErrors.password}
                  icon={<Lock size={15} />}
                  autoComplete="new-password"
                />
                {/* Strength bar */}
                {password.length > 0 && (
                  <div className="space-y-1">
                    <div className="flex gap-1">
                      {[1, 2, 3, 4].map((lvl) => (
                        <div
                          key={lvl}
                          className="flex-1 h-1 rounded-full transition-all duration-300"
                          style={{
                            backgroundColor:
                              lvl <= strength.level ? strength.color : "rgba(255,255,255,0.08)",
                          }}
                        />
                      ))}
                    </div>
                    <p className="text-[10px] font-semibold" style={{ color: strength.color }}>
                      {strength.label}
                    </p>
                  </div>
                )}
              </div>

              <AuthInput
                label="Confirm Password"
                type="password"
                placeholder="••••••••"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                error={formErrors.confirm}
                icon={<ShieldCheck size={15} />}
                autoComplete="new-password"
              />

              <div className="pt-1">
                <AuthButton type="submit" loading={actionLoading}>
                  Create Account
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

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              className="mt-6 text-center text-sm text-gray-500"
            >
              Already have an account?{" "}
              <Link
                to="/login"
                className="font-semibold text-violet-400 hover:text-violet-300 transition-colors"
              >
                Sign in
              </Link>
            </motion.p>
          </AuthCard>

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

export default SignupPage;
