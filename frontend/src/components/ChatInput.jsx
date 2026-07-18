import React, { useState } from "react";

const SUGGESTIONS = [
  "Show the top 5 products by revenue this quarter",
  "Compare monthly revenue by region",
  "Which category has the highest average order value?",
];

export default function ChatInput({ onSubmit, loading }) {
  const [value, setValue] = useState("");

  const submit = (text) => {
    const q = (text ?? value).trim();
    if (!q || loading) return;
    onSubmit(q);
    setValue("");
  };

  return (
    <div className="w-full">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="flex gap-2"
      >
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Ask a business question, e.g. 'Top 5 products by revenue this quarter'"
          className="flex-1 rounded-xl border border-slate-300 px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-xl bg-brand-600 px-5 py-3 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>
      <div className="mt-2 flex flex-wrap gap-2">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => submit(s)}
            disabled={loading}
            className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-600 hover:border-brand-500 hover:text-brand-600"
          >
            {s}
          </button>
        ))}
      </div>
    </div>
  );
}
