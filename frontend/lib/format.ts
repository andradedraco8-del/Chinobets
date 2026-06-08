export const pct = (n: number, digits = 1) => `${(n * 100).toFixed(digits)}%`;
export const money = (n: number) =>
  new Intl.NumberFormat("es-ES", { style: "currency", currency: "EUR" }).format(n);
export const signed = (n: number, digits = 2) => `${n >= 0 ? "+" : ""}${n.toFixed(digits)}`;

export function riskColor(risk: string): string {
  switch (risk) {
    case "Bajo":
      return "text-term-green";
    case "Medio":
      return "text-term-amber";
    case "Alto":
    case "Muy alto":
      return "text-term-red";
    default:
      return "text-term-muted";
  }
}

export function categoryStyle(cat: string): string {
  switch (cat) {
    case "Pick Premium":
      return "bg-term-green/15 text-term-green border border-term-green/40";
    case "Pick Seguro":
      return "bg-emerald-500/10 text-emerald-300 border border-emerald-500/30";
    case "Pick de Valor":
      return "bg-term-amber/10 text-term-amber border border-term-amber/30";
    case "Pick de Alto Riesgo":
      return "bg-term-red/10 text-term-red border border-term-red/30";
    default:
      return "bg-term-border text-term-muted";
  }
}

export function confidenceColor(text: string): string {
  switch (text) {
    case "Muy alta":
    case "Alta":
      return "text-term-green";
    case "Media":
      return "text-term-amber";
    default:
      return "text-term-red";
  }
}
