"use client";

import { type ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "outline" | "ghost";
  active?: boolean;
}

export function Button({
  children,
  variant = "ghost",
  active = false,
  className = "",
  ...props
}: ButtonProps) {
  const base =
    "min-h-touch rounded-xl px-3 py-2 font-mono text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-nothing-border focus:ring-offset-2 focus:ring-offset-nothing-bg disabled:opacity-50";
  const variants = {
    outline:
      "border border-nothing-border text-nothing-text hover:bg-nothing-surface",
    ghost:
      "border border-transparent text-nothing-muted hover:text-nothing-text hover:bg-nothing-surface",
  };
  const activeClass = active
    ? "border-nothing-border text-nothing-text bg-nothing-surface"
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
