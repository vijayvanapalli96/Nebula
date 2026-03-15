import React from "react";
import { motion } from "framer-motion";

interface AuthButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean;
  variant?: "primary" | "secondary";
}

const AuthButton: React.FC<AuthButtonProps> = ({
  children,
  loading = false,
  variant = "primary",
  disabled,
  ...props
}) => {
  const isPrimary = variant === "primary";

  return (
    <motion.button
      whileHover={!disabled && !loading ? { scale: 1.02 } : {}}
      whileTap={!disabled && !loading ? { scale: 0.97 } : {}}
      disabled={disabled || loading}
      {...(props as React.ComponentProps<typeof motion.button>)}
      className={[
        "relative w-full py-3.5 rounded-xl text-sm font-bold tracking-wide transition-all duration-200 overflow-hidden",
        isPrimary
          ? "text-white"
          : "text-gray-300 border border-white/10 hover:border-white/20 hover:text-white",
        disabled || loading ? "opacity-60 cursor-not-allowed" : "cursor-pointer",
        props.className ?? "",
      ].join(" ")}
      style={
        isPrimary
          ? {
              background: "linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%)",
              boxShadow: loading || disabled
                ? "none"
                : "0 0 24px rgba(139,92,246,0.4), 0 4px 12px rgba(0,0,0,0.3)",
            }
          : { backgroundColor: "rgba(255,255,255,0.04)" }
      }
    >
      {/* Shimmer overlay on primary hover */}
      {isPrimary && (
        <span
          aria-hidden
          className="pointer-events-none absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-300 rounded-xl"
          style={{
            background:
              "linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.12) 50%, transparent 60%)",
          }}
        />
      )}

      <span className="relative flex items-center justify-center gap-2">
        {loading && (
          <svg
            className="animate-spin h-4 w-4"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {children}
      </span>
    </motion.button>
  );
};

export default React.memo(AuthButton);
