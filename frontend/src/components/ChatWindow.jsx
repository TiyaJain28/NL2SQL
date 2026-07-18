import React from "react";
import SqlViewer from "./SqlViewer.jsx";
import ResultTable from "./ResultTable.jsx";
import ChartView from "./ChartView.jsx";

export default function ChatWindow({ turns, loading }) {
  return (
    <div className="flex flex-col gap-6">
      {turns.map((turn, i) => (
        <div key={i} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="mb-2 text-sm font-semibold text-slate-800">
            🧑 {turn.question}
          </div>

          {turn.error ? (
            <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
              {turn.error}
            </div>
          ) : (
            <>
              <p className="text-sm leading-relaxed text-slate-700">{turn.insight}</p>
              <ChartView chart={turn.chart} chartType={turn.chart_type} />
              <ResultTable columns={turn.columns} rows={turn.rows} />
              <SqlViewer sql={turn.sql} repairAttempts={turn.repair_attempts} />
            </>
          )}
        </div>
      ))}

      {loading && (
        <div className="animate-pulse rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-400">
          Agent is planning → generating SQL → validating → executing…
        </div>
      )}
    </div>
  );
}
