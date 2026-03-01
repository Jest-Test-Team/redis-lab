"use client";

import { type ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "outline" | "ghost" | "pill" | "pillLight";
  active?: boolean;
}

/** Nothing X 風格：GreyButton 對應 pill，OffWhite 對應 pillLight */
export function Button({
  children,
  variant = "ghost",
  active = false,
  className = "",
  ...props
}: ButtonProps) {
  const base =
    "min-h-touch font-mono text-xs sm:text-[10px] font-light transition-colors focus:outline-none focus:ring-2 focus:ring-nothing-border focus:ring-offset-2 focus:ring-offset-nothing-bg disabled:opacity-50";
  const variants = {
    outline:
      "rounded-lg border border-nothing-border text-nothing-muted hover:text-white hover:bg-nothing-surface px-3 py-2",
    ghost:
      "rounded-lg border border-transparent text-nothing-muted hover:text-white hover:bg-nothing-surface px-3 py-2",
    pill:
      "rounded-full bg-nothing-surface text-[rgba(255,255,255,0.8)] hover:bg-nothing-surfaceHover px-4 py-2",
    pillLight:
      "rounded-full bg-nothing-pill text-black/80 hover:opacity-90 px-4 py-2 font-normal",
  };
  const activeClass =
    active && (variant === "ghost" || variant === "outline")
      ? "bg-nothing-surface text-white border-nothing-border"
      : active && variant === "pill"
        ? "bg-nothing-pill text-black/80"
        : "";
  return (
    <button
      type="button"
      className={`${base} ${variants[variant]} ${activeClass} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
