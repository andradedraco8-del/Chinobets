"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface Props {
  data: { x: number; bankroll: number }[];
}

export default function GrowthChart({ data }: Props) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
        <defs>
          <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#10b981" stopOpacity={0.45} />
            <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#1c2b25" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="x" stroke="#6b8079" fontSize={11} tickLine={false} />
        <YAxis stroke="#6b8079" fontSize={11} tickLine={false} domain={["auto", "auto"]} />
        <Tooltip
          contentStyle={{
            background: "#101614",
            border: "1px solid #1c2b25",
            borderRadius: 8,
            color: "#e6f1ec",
            fontFamily: "monospace",
            fontSize: 12,
          }}
          labelFormatter={(l) => `Apuesta #${l}`}
          formatter={(v: number) => [`${v} €`, "Bankroll"]}
        />
        <Area
          type="monotone"
          dataKey="bankroll"
          stroke="#10b981"
          strokeWidth={2}
          fill="url(#g)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
