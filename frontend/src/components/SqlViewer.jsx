import React, { useState } from "react";

export default function SqlViewer({ sql, repairAttempts }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-3 rounded-lg border border-slate-200 bg-slate-900">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-4 py-2 text-xs font-medium text-slate-200"
      >
        <span>
          Generated SQL {repairAttempts > 0 && `(self-corrected ${repairAttempts}x)`}
        </span>
        <span>{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <pre className="overflow-x-auto px-4 pb-4 text-xs text-emerald-300">
          <code>{sql}</code>
        </pre>
      )}
    </div>
  );
}
