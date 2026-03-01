"use client";

import { useLocale } from "@/contexts/LocaleContext";
import { Button } from "@/components/ui/Button";

export function LocaleSwitcher() {
  const { locale, setLocale, t } = useLocale();

  return (
    <div className="flex items-center gap-1 rounded-full border border-nothing-border bg-nothing-bg p-0.5">
      <Button
        variant="pill"
        active={locale === "zh-TW"}
        onClick={() => setLocale("zh-TW")}
        className="min-w-[2.5rem]"
      >
        {t("localeZh")}
      </Button>
      <Button
        variant="pill"
        active={locale === "en"}
        onClick={() => setLocale("en")}
        className="min-w-[2.5rem]"
      >
        {t("localeEn")}
      </Button>
    </div>
  );
}
