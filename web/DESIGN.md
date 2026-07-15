---
version: v2
name: Squad Dark Neon
description: Dark neon pixel aesthetic — deep purple backgrounds, neon green/gold accents, CRT scan lines, retro gaming terminal feel.
colors:
  bg: "#161120"
  bg-deep: "#0d0a18"
  surface: "#231a3a"
  surface-raised: "#2e2250"
  surface-hover: "#3a2d60"
  fg: "#f0ecf8"
  fg-dim: "#c8b8e0"
  muted: "#9a8ab0"
  accent: "#39ff14"          # neon green
  accent-dim: "#2bcc10"
  gold: "#ffd700"
  gold-dim: "#cc9900"
  danger: "#ff3344"
  warn: "#ffa500"
  info: "#00ccff"
  pitch-green: "#0d3320"
  pitch-line: "rgba(57, 255, 20, 0.35)"
  border: "#3d2d5c"
  border-bright: "#4d3d6c"
typography:
  display:
    fontFamily: "'Press Start 2P', monospace"
    fontSize: "10px"
    textTransform: "uppercase"
  body:
    fontFamily: "'VT323', monospace"
    fontSize: "16px"
    lineHeight: "1.25"
  mono:
    fontFamily: "'VT323', monospace"
effects:
  scanlines: "repeating-linear-gradient(0deg, rgba(0,0,0,0.08) 0px, transparent 1px, transparent 3px)"
  neon-glow: "0 0 10px rgba(57,255,20,0.3)"
  text-glow: "0 0 6px rgba(57,255,20,0.25)"
  crt-curve: "none"
components:
  phase-card:
    background: "{colors.surface}"
    border: "1px solid {colors.border}"
    hover: "1px solid {colors.accent}"
    glow: "0 0 12px {colors.accent-glow}"
  stat-bar:
    background: "rgba(255,255,255,0.05)"
    fill: "{stat-color}"
    glow: "0 0 4px {stat-color}-glow"
  pitch-diagram:
    background: "{colors.pitch-green}"
    lines: "rgba(57,255,20,0.35)"
    slot-bg: "rgba(57,255,20,0.1)"
  button:
    background: "transparent"
    border: "1px solid {colors.accent}"
    color: "{colors.accent}"
    hover: "background {colors.accent}; color {colors.accent-on}"
  combo-chain:
    color: "{colors.gold}"
    glow: "text-shadow: 0 0 8px {colors.gold-glow}"
---

## Design Notes

- **Dark neon pixel aesthetic** — deep purple backgrounds with neon green and gold accents
- CRT scan lines overlay for retro terminal feel
- **Press Start 2P** for display/headings, **VT323** for body text
- Neon glow effects on interactive elements and stat bars
- Color-coded stats: ATK (red), PAC (gold), PAS (cyan), DEF (green), SPC (purple)
- Phase cards show combo tags with golden glow for active chains
- Pitch diagram uses dark green with neon line overlays
- Shop items use rarity colors: common (muted), uncommon (gold), rare (neon green)
- Auto-win flash effect with gold glow
- No beveled borders — flat with neon glow for modern retro feel
