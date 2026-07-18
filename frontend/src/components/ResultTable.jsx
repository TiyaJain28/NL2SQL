import React from "react";

export default function ResultTable({ columns, rows }) {
  if (!columns?.length) return null;

  return (
    <div className="mt-3 max-h-72 overflow-auto rounded-lg border border-slate-200">
      <table className="min-w-full text-left text-sm">
        <thead className="sticky top-0 bg-slate-100">
          <tr>
            {columns.map((col) => (
              <th key={col} className="px-3 py-2 font-semibold text-slate-700">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-slate-100 odd:bg-white even:bg-slate-50">
              {columns.map((col) => (
                <td key={col} className="px-3 py-2 text-slate-600">
                  {String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
