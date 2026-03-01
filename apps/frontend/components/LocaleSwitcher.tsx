"use client";

import { useLocale } from "@/contexts/LocaleContext";
import { Button } from "@/components/ui/Button";

export function LocaleSwitcher() {
  const { locale, setLocale, t } = useLocale();

  return (
    <div className="flex items-center gap-1 rounded-xl border border-nothing-border bg-nothing-surface/50 p-0.5">
      <Button
        variant="ghost"
        active={locale === "zh-TW"}
        onClick={() => setLocale("zh-TW")}
        className="min-w-[3rem]"
      >
        {t("localeZh")}
      </Button>
      <Button
        variant="ghost"
        active={locale === "en"}
        onClick={() => setLocale("en")}
        className="min-w-[3rem]"
      >
        {t("localeEn")}
      </Button>
    </div>
  );
}
