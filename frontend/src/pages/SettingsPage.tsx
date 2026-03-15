import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LogOut,
  User,
  Mail,
  Shield,
  AlertTriangle,
} from "lucide-react";
import DashboardLayout from "../components/layout/DashboardLayout";
import { useAuthStore } from "../store/authStore";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getProviderLabel(user: { providerData?: { providerId: string }[] } | null): string {
  if (!user?.providerData?.length) return "Email / Password";
  const id = user.providerData[0].providerId;
  if (id === "google.com") return "Google";
  if (id === "password")   return "Email / Password";
  return id;
}

function getProviderColor(user: { providerData?: { providerId: string }[] } | null): string {
  if (!user?.providerData?.length) return "#a78bfa";
  const id = user.providerData[0].providerId;
  return id === "google.com" ? "#60a5fa" : "#a78bfa";
}

function getUserInitial(displayName: string | null, email: string | null): string {
  if (displayName) return displayName[0].toUpperCase();
  if (email)       return email[0].toUpperCase();
  return "?";
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const fadeUp = {
  hidden:  { opacity: 0, y: 16 },
  visible: (d: number) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.45, ease: "easeOut" as const, delay: d },
  }),
};

interface InfoRowProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  accent?: string;
}

const InfoRow: React.FC<InfoRowProps> = ({ icon, label, value, accent = "#a78bfa" }) => (
  <div
    className="flex items-center gap-4 px-5 py-4 rounded-xl transition-colors"
    style={{
      backgroundColor: "var(--bg-elevated)",
      border: "1px solid var(--border-color)",
    }}
  >
    <div
      className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0"
      style={{ backgroundColor: `${accent}15`, border: `1px solid ${accent}30`, color: accent }}
    >
      {icon}
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-[10px] font-bold uppercase tracking-widest mb-0.5" style={{ color: "var(--text-muted)" }}>
        {label}
      </p>
      <p className="text-sm font-semibold truncate" style={{ color: "var(--text-primary)" }}>
        {value}
      </p>
    </div>
  </div>
);

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

const SettingsPage: React.FC = () => {
  const navigate   = useNavigate();
  const { user, logout, actionLoading } = useAuthStore();

  const [confirmLogout, setConfirmLogout] = useState(false);

  const handleLogout = async () => {
    if (!confirmLogout) {
      setConfirmLogout(true);
      // Auto-reset confirm state after 4 s
      setTimeout(() => setConfirmLogout(false), 4000);
      return;
    }
    await logout();
    navigate("/login", { replace: true });
  };

  const providerLabel = getProviderLabel(user);
  const providerColor = getProviderColor(user);
  const initial       = getUserInitial(user?.displayName ?? null, user?.email ?? null);

  return (
    <DashboardLayout title="Settings">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* ── Page header ──────────────────────────────────────────────── */}
        <motion.div
          variants={fadeUp} custom={0} initial="hidden" animate="visible"
          className="space-y-1"
        >
          <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-violet-400">
            Dashboard / Settings
          </p>
          <h1 className="text-2xl font-black" style={{ color: "var(--text-primary)" }}>
            Account Settings
          </h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            View your profile information and manage your session.
          </p>
        </motion.div>

        {/* ── Profile card ─────────────────────────────────────────────── */}
        <motion.section
          variants={fadeUp} custom={0.08} initial="hidden" animate="visible"
          className="rounded-2xl p-6 space-y-5"
          style={{
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-color)",
          }}
        >
          {/* Avatar + name */}
          <div className="flex items-center gap-4">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-black text-white flex-shrink-0"
              style={{
                background: "linear-gradient(135deg, #7c3aed 0%, #2563eb 100%)",
                boxShadow: "0 0 24px rgba(139,92,246,0.35)",
              }}
            >
              {user?.photoURL ? (
                <img
                  src={user.photoURL}
                  alt="avatar"
                  className="w-full h-full rounded-2xl object-cover"
                />
              ) : (
                initial
              )}
            </div>
            <div>
              <p className="text-lg font-black" style={{ color: "var(--text-primary)" }}>
                {user?.displayName ?? "Nebula User"}
              </p>
              <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                {user?.email ?? "—"}
              </p>
              {/* Provider badge */}
              <span
                className="inline-flex items-center gap-1.5 mt-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-widest"
                style={{
                  backgroundColor: `${providerColor}12`,
                  border: `1px solid ${providerColor}30`,
                  color: providerColor,
                }}
              >
                <Shield size={9} />
                {providerLabel}
              </span>
            </div>
          </div>

          {/* Divider */}
          <div className="h-px" style={{ backgroundColor: "var(--border-color)" }} />

          {/* Info rows */}
          <div className="space-y-3">
            <p
              className="text-[10px] font-bold uppercase tracking-widest"
              style={{ color: "var(--text-muted)" }}
            >
              Account
            </p>

            <InfoRow
              icon={<User size={15} />}
              label="Display Name"
              value={user?.displayName ?? "Not set"}
              accent="#a78bfa"
            />
            <InfoRow
              icon={<Mail size={15} />}
              label="Email Address"
              value={user?.email ?? "—"}
              accent="#60a5fa"
            />
            <InfoRow
              icon={<Shield size={15} />}
              label="Sign-in Method"
              value={providerLabel}
              accent={providerColor}
            />
          </div>
        </motion.section>

        {/* ── Danger zone ──────────────────────────────────────────────── */}
        <motion.section
          variants={fadeUp} custom={0.16} initial="hidden" animate="visible"
          className="rounded-2xl p-6 space-y-4"
          style={{
            backgroundColor: "var(--bg-card)",
            border: "1px solid rgba(239,68,68,0.15)",
          }}
        >
          <div className="space-y-1">
            <p
              className="text-[10px] font-bold uppercase tracking-widest"
              style={{ color: "#ef4444" }}
            >
              Session
            </p>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              Signing out will end your current session on this device.
            </p>
          </div>

          <motion.button
            whileHover={!actionLoading ? { scale: 1.015 } : {}}
            whileTap={!actionLoading  ? { scale: 0.97  } : {}}
            onClick={handleLogout}
            disabled={actionLoading}
            className={[
              "flex items-center gap-2.5 px-5 py-3 rounded-xl text-sm font-bold transition-all duration-200",
              actionLoading ? "opacity-60 cursor-not-allowed" : "cursor-pointer",
              confirmLogout
                ? "text-white"
                : "text-red-400 hover:text-white",
            ].join(" ")}
            style={
              confirmLogout
                ? {
                    backgroundColor: "rgba(239,68,68,0.18)",
                    border: "1px solid rgba(239,68,68,0.5)",
                    boxShadow: "0 0 16px rgba(239,68,68,0.2)",
                  }
                : {
                    backgroundColor: "rgba(239,68,68,0.06)",
                    border: "1px solid rgba(239,68,68,0.2)",
                  }
            }
          >
            {actionLoading ? (
              <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : confirmLogout ? (
              <AlertTriangle size={15} />
            ) : (
              <LogOut size={15} />
            )}
            {actionLoading
              ? "Signing out…"
              : confirmLogout
              ? "Click again to confirm sign out"
              : "Sign Out"}
          </motion.button>
        </motion.section>
      </div>
    </DashboardLayout>
  );
};

export default SettingsPage;
