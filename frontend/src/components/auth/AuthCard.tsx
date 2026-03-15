import React from "react";
import { motion } from "framer-motion";

interface AuthCardProps {
  children: React.ReactNode;
}

const AuthCard: React.FC<AuthCardProps> = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 32, scale: 0.97 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
    className="w-full max-w-md rounded-3xl p-8 sm:p-10 relative overflow-hidden"
    style={{
      backgroundColor: "rgba(22,22,31,0.9)",
      border: "1px solid rgba(255,255,255,0.08)",
      backdropFilter: "blur(24px)",
      boxShadow: "0 32px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06)",
    }}
  >
    {/* Subtle inner gradient */}
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 rounded-3xl"
      style={{
        background:
          "radial-gradient(ellipse 70% 50% at 50% 0%, rgba(139,92,246,0.08) 0%, transparent 60%)",
      }}
    />
    <div className="relative z-10">{children}</div>
  </motion.div>
);

export default React.memo(AuthCard);
