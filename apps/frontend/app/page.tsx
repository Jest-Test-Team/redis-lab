"use client";

import { motion } from "framer-motion";
import { useWs } from "@/hooks/useWs";
import { getGatewayWsUrl } from "@/lib/gateway-url";
import { useTranslations } from "@/contexts/LocaleContext";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { LocaleSwitcher } from "@/components/LocaleSwitcher";

export default function Home() {
  const t = useTranslations();
  const wsUrl = getGatewayWsUrl();
  const { connected, virtualId, lastEvent, logs } = useWs(wsUrl);

  return (
    <main className="min-h-screen p-4 sm:p-6 md:p-8 lg:p-10">
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-center justify-between gap-2 border-b border-nothing-border pb-4 mb-6 md:mb-8"
      >
        <div>
          <h1 className="text-sm sm:text-base md:text-lg font-semibold text-white tracking-tight">
            {t("title")}
          </h1>
          <p className="text-[10px] sm:text-xs font-light text-nothing-muted mt-0.5">
            {t("subtitle")}
          </p>
        </div>
        <LocaleSwitcher />
      </motion.header>

      <div className="grid gap-4 sm:gap-6 grid-cols-1 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <h2 className="font-mono text-[10px] font-normal text-white/80 mb-2 uppercase tracking-wider">
              {t("connectionStatus")}
            </h2>
            <p className="font-mono text-[10px] sm:text-xs font-light text-white/80">
              {t("gatewayWs")}: <StatusBadge connected={connected} label={connected ? t("connected") : t("disconnected")} />
            </p>
            {virtualId && (
              <p className="font-mono text-[10px] text-white/80 mt-2">
                {t("virtualId")}: <span className="glow-cyan text-terminal-cyan">{virtualId}</span>
              </p>
            )}
            {lastEvent && (
              <p className="font-mono text-[10px] text-nothing-muted mt-1 truncate">
                {t("lastEvent")}: {lastEvent.type}
              </p>
            )}
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.15 }}
        >
          <Card>
            <h2 className="font-mono text-[10px] font-normal text-white/80 mb-2 uppercase tracking-wider">
              {t("liveLog")}
            </h2>
            <div className="font-mono text-[10px] sm:text-xs max-h-36 sm:max-h-40 overflow-y-auto space-y-1 text-nothing-muted">
              {logs.length === 0 && (
                <span className="text-neutral-600">{t("logWaiting")}</span>
              )}
              {logs.slice(-8).map((line, i) => (
                <div key={i} className="truncate">
                  {line}
                </div>
              ))}
            </div>
          </Card>
        </motion.div>
      </div>

      <motion.footer
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
        className="mt-8 sm:mt-10 text-center text-nothing-muted text-[10px] font-light"
      >
        {t("footer")}
      </motion.footer>
    </main>
  );
}
