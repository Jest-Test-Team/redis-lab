"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useWs } from "@/hooks/useWs";
import { useAuction } from "@/hooks/useAuction";
import { getGatewayWsUrl } from "@/lib/gateway-url";
import { createAuction, bid, settle } from "@/lib/gateway-api";
import { useTranslations } from "@/contexts/LocaleContext";
import { Card } from "@/components/ui/Card";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Button } from "@/components/ui/Button";
import { LocaleSwitcher } from "@/components/LocaleSwitcher";
import { IdentityGlitch } from "@/components/IdentityGlitch";
import { OrderBookWaterfall } from "@/components/OrderBookWaterfall";
import { KillSwitchOverlay } from "@/components/KillSwitchOverlay";

export default function Home() {
  const t = useTranslations();
  const wsUrl = getGatewayWsUrl();
  const { connected, virtualId, lastEvent, identityRefreshCount, messages, logs } = useWs(wsUrl);
  const [auctionId, setAuctionId] = useState("");
  const [bidAmount, setBidAmount] = useState("");
  const [killSwitchVisible, setKillSwitchVisible] = useState(false);
  const [killSwitchIntel, setKillSwitchIntel] = useState("");

  const { entries, settledEvent } = useAuction(auctionId || null, messages);

  const handleCreate = async () => {
    const id = auctionId.trim() || `auction-${Date.now()}`;
    const res = await createAuction(id, 5000);
    if (res.ok) setAuctionId(id);
  };

  const handleBid = async () => {
    if (!auctionId || !virtualId) return;
    const amt = parseFloat(bidAmount);
    if (Number.isNaN(amt) || amt <= 0) return;
    await bid(auctionId, virtualId, amt);
    setBidAmount("");
  };

  const handleSettle = async () => {
    if (!auctionId) return;
    const res = await settle(auctionId);
    if (res.ok && res.winner_id === virtualId) {
      setKillSwitchIntel(res.top_bid != null ? `Winning bid: ${res.top_bid}` : "Intel received.");
      setKillSwitchVisible(true);
    }
  };

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
            <IdentityGlitch virtualId={virtualId} triggerRefresh={identityRefreshCount} label={t("virtualId")} />
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

      <motion.section
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mt-6 md:mt-8"
      >
        <Card>
          <h2 className="font-mono text-[10px] font-normal text-white/80 mb-3 uppercase tracking-wider">
            {t("liveBids")}
          </h2>
          <div className="flex flex-wrap gap-2 items-end mb-3">
            <label className="font-mono text-[10px] text-nothing-muted">
              {t("auctionId")}
              <input
                type="text"
                value={auctionId}
                onChange={(e) => setAuctionId(e.target.value)}
                placeholder="auction-1"
                className="ml-2 rounded-lg bg-nothing-bg border border-nothing-border px-2 py-1.5 font-mono text-xs text-white/80 w-36"
              />
            </label>
            <Button variant="pill" onClick={handleCreate}>
              {t("createAuction")}
            </Button>
          </div>
          {auctionId && (
            <>
              <div className="flex flex-wrap gap-2 items-end mb-3">
                <label className="font-mono text-[10px] text-nothing-muted">
                  {t("bidAmount")}
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={bidAmount}
                    onChange={(e) => setBidAmount(e.target.value)}
                    className="ml-2 rounded-lg bg-nothing-bg border border-nothing-border px-2 py-1.5 font-mono text-xs text-white/80 w-24"
                  />
                </label>
                <Button variant="pill" onClick={handleBid} disabled={!virtualId}>
                  {t("placeBid")}
                </Button>
                <Button variant="outline" onClick={handleSettle}>
                  {t("settle")}
                </Button>
              </div>
              <OrderBookWaterfall entries={entries} maxRows={12} />
            </>
          )}
        </Card>
      </motion.section>

      <KillSwitchOverlay
        visible={killSwitchVisible}
        intelText={killSwitchIntel}
        onComplete={() => setKillSwitchVisible(false)}
      />

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
