import React, { forwardRef } from "react";
import { motion } from "framer-motion";

interface AuthInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  icon?: React.ReactNode;
}

const AuthInput = forwardRef<HTMLInputElement, AuthInputProps>(
  ({ label, error, icon, id, ...props }, ref) => {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="space-y-1.5">
        <label
          htmlFor={inputId}
          className="block text-xs font-semibold uppercase tracking-widest"
          style={{ color: "rgba(156,163,175,0.8)" }}
        >
          {label}
        </label>

        <div className="relative">
          {icon && (
            <div
              className="pointer-events-none absolute inset-y-0 left-3.5 flex items-center"
              style={{ color: "rgba(139,92,246,0.7)" }}
            >
              {icon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            {...props}
            className={[
              "w-full rounded-xl py-3 text-sm font-medium transition-all duration-200 outline-none",
              icon ? "pl-10 pr-4" : "px-4",
              "text-white placeholder:text-gray-600",
              error
                ? "border border-red-500/60 focus:border-red-400"
                : "border border-white/[0.07] focus:border-violet-500/60",
            ].join(" ")}
            style={{
              backgroundColor: "rgba(255,255,255,0.04)",
              boxShadow: error
                ? "0 0 0 3px rgba(239,68,68,0.1)"
                : undefined,
            }}
            onFocus={(e) => {
              if (!error) {
                e.currentTarget.style.boxShadow = "0 0 0 3px rgba(139,92,246,0.18)";
                e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.06)";
              }
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              e.currentTarget.style.boxShadow = "";
              e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.04)";
              props.onBlur?.(e);
            }}
          />
        </div>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-xs text-red-400 font-medium"
          >
            {error}
          </motion.p>
        )}
      </div>
    );
  }
);

AuthInput.displayName = "AuthInput";

export default React.memo(AuthInput);
