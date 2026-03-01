"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslations } from "@/contexts/LocaleContext";

const COUNTDOWN_MS = 3000;
const INTEL_DISPLAY_MS = 1500;

interface KillSwitchOverlayProps {
  visible: boolean;
  onComplete: () => void;
  intelText?: string;
}

export function KillSwitchOverlay({ visible, onComplete, intelText = "" }: KillSwitchOverlayProps) {
  const t = useTranslations();
  const [progress, setProgress] = useState(100);
  const [phase, setPhase] = useState<"countdown" | "intel" | "shatter">("countdown");

  useEffect(() => {
    if (!visible) {
      setProgress(100);
      setPhase("countdown");
      return;
    }
    const start = Date.now();
    const t = setInterval(() => {
      const elapsed = Date.now() - start;
      const p = Math.max(0, 100 - (elapsed / COUNTDOWN_MS) * 100);
      setProgress(p);
      if (p <= 0) {
        clearInterval(t);
        setPhase("intel");
      }
    }, 50);
    return () => clearInterval(t);
  }, [visible]);

  useEffect(() => {
    if (!visible || phase !== "intel") return;
    const id = setTimeout(() => setPhase("shatter"), INTEL_DISPLAY_MS);
    return () => clearTimeout(id);
  }, [visible, phase]);

  useEffect(() => {
    if (!visible || phase !== "shatter") return;
    const id = setTimeout(() => onComplete(), 800);
    return () => clearTimeout(id);
  }, [visible, phase, onComplete]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-red-950/85 backdrop-blur-sm"
        >
          {phase === "countdown" && (
            <div className="w-full max-w-xs px-4">
              <p className="font-mono text-[10px] text-white/80 uppercase tracking-wider mb-2 text-center">
                {t("countdown")}
              </p>
              <div className="h-2 w-full rounded-full bg-white/20 overflow-hidden">
                <motion.div
                  className="h-full rounded-full bg-white"
                  style={{ width: `${progress}%` }}
                  transition={{ duration: 0.05 }}
                />
              </div>
            </div>
          )}
          {(phase === "intel" || phase === "shatter") && (
            <motion.p
              initial={{ opacity: 0, scale: 0.9 }}
              animate={
                phase === "intel"
                  ? { opacity: 1, scale: 1 }
                  : { opacity: 0, scale: 0.8, filter: "blur(12px)" }
              }
              transition={{ duration: phase === "shatter" ? 0.5 : 0.2 }}
              className="font-mono text-sm text-white/90 text-center max-w-md px-4"
            >
              {intelText || t("intelDestroyed")}
            </motion.p>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
