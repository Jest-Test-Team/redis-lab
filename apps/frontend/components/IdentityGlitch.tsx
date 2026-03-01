"use client";

import { useEffect, useState } from "react";

interface IdentityGlitchProps {
  virtualId: string | null;
  triggerRefresh?: number;
  label?: string;
}

export function IdentityGlitch({ virtualId, triggerRefresh = 0, label = "Virtual ID" }: IdentityGlitchProps) {
  const [glitching, setGlitching] = useState(false);

  useEffect(() => {
    if (triggerRefresh === 0 || !virtualId) return;
    setGlitching(true);
    const t = setTimeout(() => setGlitching(false), 400);
    return () => clearTimeout(t);
  }, [triggerRefresh, virtualId]);

  if (!virtualId) return null;

  return (
    <p className="font-mono text-[10px] text-white/80 mt-2">
      {label}:{" "}
      <span
        className={`glow-cyan text-terminal-cyan inline-block ${glitching ? "glitch-active" : ""}`}
        aria-hidden={glitching}
      >
        {virtualId}
      </span>
    </p>
  );
}
