"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import type { Locale } from "@/types/i18n";
import type { Messages } from "@/types/i18n";
import en from "@/messages/en.json";
import zhTW from "@/messages/zh-TW.json";

const STORAGE_KEY = "mirage-locale";

const messagesMap: Record<Locale, Messages> = {
  "zh-TW": zhTW as Messages,
  en: en as Messages,
};

type LocaleContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: keyof Messages) => string;
};

const LocaleContext = createContext<LocaleContextValue | null>(null);

function getInitialLocale(): Locale {
  if (typeof window === "undefined") return "zh-TW";
  const stored = localStorage.getItem(STORAGE_KEY) as Locale | null;
  if (stored === "zh-TW" || stored === "en") return stored;
  const lang = navigator.language;
  if (lang.startsWith("zh")) return "zh-TW";
  return "en";
}

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("zh-TW");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setLocaleState(getInitialLocale());
    setMounted(true);
  }, []);

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, next);
      document.documentElement.lang = next === "zh-TW" ? "zh-TW" : "en";
    }
  }, []);

  useEffect(() => {
    if (!mounted) return;
    document.documentElement.lang = locale === "zh-TW" ? "zh-TW" : "en";
  }, [mounted, locale]);

  const t = useCallback(
    (key: keyof Messages): string => {
      const messages = messagesMap[locale];
      return (messages[key] as string) ?? key;
    },
    [locale]
  );

  const value = useMemo(
    () => ({ locale, setLocale, t }),
    [locale, setLocale, t]
  );

  return (
    <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
  );
}

export function useLocale() {
  const ctx = useContext(LocaleContext);
  if (!ctx) throw new Error("useLocale must be used within LocaleProvider");
  return ctx;
}

export function useTranslations() {
  const { t } = useLocale();
  return t;
}
