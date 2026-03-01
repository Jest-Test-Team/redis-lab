interface StatusBadgeProps {
  connected: boolean;
  label: string;
}

export function StatusBadge({ connected, label }: StatusBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-sm">
      <span
        className={`h-2 w-2 shrink-0 rounded-full ${
          connected ? "bg-terminal-green" : "bg-terminal-red"
        }`}
        aria-hidden
      />
      <span
        className={
          connected ? "text-terminal-green" : "text-terminal-red"
        }
      >
        {label}
      </span>
    </span>
  );
}
