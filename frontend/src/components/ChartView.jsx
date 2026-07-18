import React from "react";
import Plot from "react-plotly.js";

export default function ChartView({ chart, chartType }) {
  if (!chart || chartType === "table" || chartType === "kpi") return null;

  return (
    <div className="mt-3 rounded-lg border border-slate-200 bg-white p-2">
      <Plot
        data={chart.data}
        layout={{
          ...chart.layout,
          autosize: true,
          margin: { t: 30, r: 20, b: 40, l: 50 },
        }}
        style={{ width: "100%", height: "380px" }}
        useResizeHandler
        config={{ displaylogo: false, responsive: true }}
      />
    </div>
  );
}
