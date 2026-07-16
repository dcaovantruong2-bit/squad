# Squad — Design System

> Source of truth for visual consistency. AI agents: apply these rules. Do not improvise.

---

## 1. Identity

| Property | Value |
|----------|-------|
| Name | Squad |
| Style | Dark neon pixel — retro terminal meets football tactics |
| Screen | 1920×1080 reference. No responsive breakpoints. |
| Font stack | `'Press Start 2P'` (display) / `'VT323'` (body+mono) |

---

## 2. Color Tokens

### Backgrounds
| Token | Hex | Usage |
|-------|-----|-------|
| `bg` | `#161120` | Page background, screen containers |
| `bg-deep` | `#0d0a18` | Lowest layer (behind surfaces) |
| `surface` | `#231a3a` | Cards, panels, phase cards |
| `surface-raised` | `#2e2250` | Hovered items, active states |
| `surface-hover` | `#3a2d60` | Hovered cards, interactive highlight |

### Text
| Token | Hex | Usage |
|-------|-----|-------|
| `fg` | `#f0ecf8` | Primary text, headings |
| `fg-dim` | `#c8b8e0` | Secondary text, descriptions |
| `muted` | `#9a8ab0` | Tertiary text, labels, hints |

### Accents
| Token | Hex | Usage |
|-------|-----|-------|
| `accent` | `#39ff14` | Neon green — primary accent, CTA buttons, borders, glow |
| `accent-dim` | `#2bcc10` | Dimmed accent (inactive states) |
| `gold` | `#ffd700` | Gold — score values, combo chains, morale, premium items |
| `gold-dim` | `#cc9900` | Dimmed gold |

### Status
| Token | Hex | Usage |
|-------|-----|-------|
| `success` | `#39ff14` | Win state, auto-win, synergies fired |
| `warn` | `#ffa500` | Fatigue, moderate penalties |
| `danger` | `#ff3344` | ATK stat, OOP penalty, loss state |
| `info` | `#00ccff` | PAS stat, links, informational |
| `purple` | `#c084fc` | SPC stat, specialist effects |

### Pitch
| Token | Hex | Usage |
|-------|-----|-------|
| `pitch-green` | `#0d3320` | Pitch diagram background |
| `pitch-line` | `rgba(57,255,20,0.35)` | Pitch lines, zone boundaries |

### Borders
| Token | Hex | Usage |
|-------|-----|-------|
| `border` | `#3d2d5c` | Default borders on cards, panels |
| `border-bright` | `#4d3d6c` | Elevated borders, focused states |

---

## 3. Effects

| Name | CSS | Usage |
|------|-----|-------|
| `scanlines` | `repeating-linear-gradient(0deg, rgba(0,0,0,0.08) 0px, transparent 1px, transparent 3px)` | Full-screen CRT overlay |
| `neon-glow` | `0 0 10px rgba(57,255,20,0.3)` | Button hover, card glow |
| `text-glow` | `0 0 6px rgba(57,255,20,0.25)` | Headings, neon text |
| `gold-glow` | `0 0 8px rgba(255,215,0,0.35)` | Score displays, combo chains |

---

## 4. Typography

### Display (Headings, Labels, Phase Icons)
| Property | Value |
|----------|-------|
| Font | `'Press Start 2P', monospace` |
| Size | 10–48px (labels=10px, headings=16px, hero/title=48px) |
| Transform | Uppercase |
| Tracking | Normal |
| Usage | Phase names, section headers, stat labels, pill counts |

### Body (Descriptions, Scores, Player Names)
| Property | Value |
|----------|-------|
| Font | `'VT323', monospace` |
| Size | 16px |
| Line height | 1.25 |
| Usage | Descriptions, scores, player names, button text |

### Mono (Code, Formulas)
| Property | Value |
|----------|-------|
| Font | `'VT323', monospace` |
| Size | 14–16px |
| Usage | Scoring breakdowns, synergy rules, technical data |

---

## 5. Component Catalog

### Phase Card
| Property | Value |
|----------|-------|
| Background | `surface` |
| Border | `1px solid border` |
| Hover border | `1px solid accent` |
| Hover glow | `0 0 12px accent-glow` |
| Width | Fixed within grid |
| Padding | 8px–12px |
| Contains | icon (display), name (display), desc (body), slots (mono), tags (display) |

### Stat Bar
| Property | Value |
|----------|-------|
| Background | `rgba(255,255,255,0.05)` |
| Fill color | Stat-specific (ATK=danger, PAC=gold, PAS=info, DEF=accent, SPC=purple) |
| Fill glow | `0 0 4px` in stat color |
| Height | 4px |
| Width | Proportional to value (0–10 scale) |

### Player Card
| Property | Value |
|----------|-------|
| Background | `surface` |
| Border | `1px solid border` |
| Padding | 6px |
| Contains | name (display), position badge (mono), stat bars (stat-bar) |
| Selected border | `1px solid accent` with glow |

### Pitch Diagram
| Property | Value |
|----------|-------|
| Background | `pitch-green` |
| Lines | `pitch-line` |
| Slots | `rgba(57,255,20,0.1)` background |
| Filled slot | `accent` background with glow |
| Empty slot | Dimmed, dashed border |

### Button (Primary)
| Property | Value |
|----------|-------|
| Background | `transparent` |
| Border | `1px solid accent` |
| Text | `accent` (display font) |
| Hover | Background fills `accent`, text inverts to `bg` |
| Padding | 8px 16px |

### Button (Secondary)
| Property | Value |
|----------|-------|
| Background | `transparent` |
| Border | `1px solid border` |
| Text | `muted` (display font) |
| Hover | Border `accent`, text `accent` |
| Padding | 8px 16px |

### Shop Item Card
| Property | Value |
|----------|-------|
| Background | `surface` |
| Rarity border | common=`border`, uncommon=`gold`, rare=`accent` |
| Cost badge | `gold` text, `gold-glow` |

### Combo Chain Badge
| Property | Value |
|----------|-------|
| Color | `gold` |
| Glow | `gold-glow` (text-shadow) |
| Font | Display |

### Score Display
| Property | Value |
|----------|-------|
| Color | `gold` |
| Font | Display |
| Glow | `gold-glow` |
| Size | Large (24px+) |

### Synergy Trigger Badge
| Property | Value |
|----------|-------|
| Background | `accent` |
| Text | `bg` (inverted) |
| Font | Display |
| Padding | 2px 6px |

---

## 6. Layout Principles

- **Full-width panels** — no centering, no max-width
- **Dense information** — every screen shows maximum data
- **Single column** on mobile-sized viewport, **two columns** on wide screens
- **Carousel** for formation selection (horizontal scroll with dots)
- **Grid** for phase cards (auto-fill, min 200px columns)
- **Sticky** action bar at bottom for submit/skip buttons

---

## 7. Interaction Rules

| Interaction | Effect |
|-------------|--------|
| Hover on phase card | Border changes to `accent`, glow appears |
| Click phase card | `selected` class toggled, card highlights |
| Hover on player | `surface-raised` background |
| Click player | Toggle selected state |
| Submit phase | If valid: transition to result screen; if invalid: shake feedback |
| Auto-fill | Instant, no confirmation |
| Shop purchase | Deduct morale, apply effect, disable item |

---

## 8. Prohibited

- No gradients on surfaces (glow effects are acceptable)
- No rounded corners (everything is rectangular)
- No shadows (only neon glow)
- No white backgrounds anywhere
- No serif fonts
- No animations longer than 200ms
- No text smaller than 10px (display font minimum)
