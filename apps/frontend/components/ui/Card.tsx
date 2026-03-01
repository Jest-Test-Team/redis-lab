import { type ReactNode } from "react";

interface CardProps {
  children: ReactNode;
  className?: string;
}

export function Card({ children, className = "" }: CardProps) {
  return (
    <div
      className={`rounded-2xl border border-nothing-border bg-nothing-surface p-4 sm:p-5 ${className}`}
    >
      {children}
    </div>
  );
}
