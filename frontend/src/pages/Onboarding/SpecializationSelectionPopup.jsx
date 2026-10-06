import { Globe, Network, Shield } from "lucide-react";

const OPTIONS = [
  { slug: "web-pentest", label: "Web Pentesting", icon: Globe },
  { slug: "network-pentest", label: "Network Pentesting", icon: Network },
  { slug: "red-team", label: "Red Teaming", icon: Shield },
];

export default function SpecializationSelectionPopup({
  open,
  locked,
  onSelect,
  onClose,
}) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="nb-card w-full max-w-lg rounded-2xl p-6">
        <h2 className="text-lg font-bold text-white">
          Choose your offensive-security specialization
        </h2>

        <p className="mt-2 text-sm leading-6 text-slate-400">
          Your first choice is locked once you open the first lesson. You can
          still study Password Attacks and other foundations at any time.
        </p>

        <div className="mt-5 space-y-2">
          {OPTIONS.map(({ slug, label, icon: Icon }) => (
            <button
              key={slug}
              type="button"
              disabled={locked}
              onClick={() => onSelect?.(slug)}
              className="flex w-full items-center gap-3 rounded-xl border border-slate-800 bg-slate-950/40 px-4 py-3 text-left text-sm text-slate-200 transition enabled:hover:border-blue-500/50 disabled:opacity-50"
            >
              <Icon className="h-4 w-4 text-blue-400" />
              {label}
            </button>
          ))}
        </div>

        {onClose && (
          <div className="mt-5 flex justify-end">
            <button
              type="button"
              onClick={onClose}
              className="nb-button-secondary rounded-lg px-4 py-2 text-xs font-semibold"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
