# Squad — Complete Screen Architecture Design Spec

> **Ready for implementation.** Every screen described with purpose, layout, component tree, interaction model, and transition behavior.  
> Reference: `web/DESIGN.md` for visual tokens (colors, typography, components).  
> Reference: `README.md` for game mechanics (scoring, synergies, campaign).

---

## Table of Contents

1. [Screen 1: Title & Onboarding](#1-title--onboarding-screen)
2. [Screen 2: Squad Builder Redesign](#2-squad-builder-redesign)
3. [Screen 3: Formation Select](#3-formation-select)
4. [Screen 4: Phase Selection](#4-phase-selection)
5. [Screen 5: Match Screen](#5-match-screen)
6. [Screen 6: Phase Result](#6-phase-result)
7. [Screen 7: Shop](#7-shop)
8. [Screen 8: Round Result & Campaign Map](#8-round-result--campaign-map)
9. [Screen 9: Campaign Complete](#9-campaign-complete)

---

## Design System Reference

All screens use tokens from `DESIGN.md`:
- **Colors**: `bg` (#161120), `surface` (#231a3a), `accent` (#39ff14), `gold` (#ffd700), `danger` (#ff3344), `info` (#00ccff), `purple` (#c084fc)
- **Typography**: `'Press Start 2P'` (display), `'VT323'` (body/mono)
- **Effects**: `neon-glow`, `gold-glow`, `scanlines` overlay
- **Strict rules**: No gradients, no rounded corners, no white backgrounds, no shadows (only neon glow), no serif fonts, max 200ms animations

---

## 1. Title & Onboarding Screen

### Primary Purpose
First impression. Attract, inform, and route the player into gameplay with minimal friction.

### Player Goal
Understand what the game is and start a run — either via Quick Start (random squad) or Draft Mode (manual build).

---

### Layout

```
┌────────────────────────────────────────────────────────────┐
│                    [ SCANLINES OVERLAY ]                    │
│                                                            │
│                      ╔═══════════════╗                     │
│                      ║     SQUAD     ║  ← logo with pulse  │
│                      ╚═══════════════╝                     │
│                   FOOTBALL CARD ROGUELIKE                   │
│                                                            │
│         ┌─────────────────────────────────────┐            │
│         │  "Build your squad. Pick your       │            │
│         │   formation. Stack synergies.       │            │
│         │   Survive 5 escalating matches."    │            │
│         │                                     │            │
│         │  ⚽ 11+ players from 36             │            │
│         │  📋 13 tactical phases              │            │
│         │  🔗 Balatro-style scoring           │            │
│         │  🏆 5-match campaign                │            │
│         └─────────────────────────────────────┘            │
│                                                            │
│         ┌──────────────┐    ┌──────────────┐              │
│         │ ⚡ QUICK START │    │ 📝 DRAFT MODE │              │
│         │  Random squad  │    │  Build your    │              │
│         │  + recommend   │    │  own team      │              │
│         └──────────────┘    └──────────────┘              │
│                                                            │
│         [?] How to Play    [⚙] Settings                    │
│                                                            │
│         Best Run: 4 wins · High Score: 4.2M                │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Logo** | `SQUAD` in display font at 48px, `accent` color with `neon-glow` pulse animation (2s ease-in-out) |
| **Tagline** | `FOOTBALL CARD ROGUELIKE` in gold, 10px display, letter-spacing 0.2em |
| **Info Card** | `surface` panel with bulleted mechanic summary — dense, 4 lines max |
| **Quick Start Button** | Primary button (`accent` border, transparent bg, fills on hover). Icon + label. On click: auto-drafts a valid random squad, auto-picks recommended formation, jumps to Match screen. Confirmation toast: "Random squad built — good luck!" |
| **Draft Mode Button** | Secondary button (`border` border). Icon + label. On click: navigates to Squad Builder (Screen 2) |
| **How to Play** | Small muted text link. Opens a modal/overlay panel with 4-section accordion: Squad Building, Formations, Phases & Synergies, Campaign. Each section is a 2-4 sentence summary. |
| **Settings** | Small muted text link. Opens a minimal settings overlay: sound on/off, animation speed (normal/fast), reset progress |
| **Run History** | Bottom strip showing best run stats (best campaign wins, highest single-round score). Faded/optional. |

### Interactions

| Trigger | Action |
|---------|--------|
| Click Quick Start | Shuffle all players, pick 11 meeting composition reqs within budget, auto-assign best-matching formation, transition to Match (Screen 5) with 0.3s fade |
| Click Draft Mode | Navigate to Squad Builder (Screen 2) with slide-left transition |
| Click How to Play | Modal slides up from bottom with 4 accordion sections. Close button or click outside to dismiss |
| Hover How to Play | Underline appears, color shifts to `accent` |
| Keyboard: Enter | Triggers Quick Start |
| Keyboard: D | Triggers Draft Mode |

### Transition In
- Screen fades in from black over 0.4s
- Logo pulses after 0.2s delay
- Buttons stagger in with 0.1s offset each

### Transition Out
- To Squad Builder: slide-left 0.3s
- To Match (Quick Start): fade-out 0.2s → brief loading spinner (0.5s max) → fade-in Match

---

## 2. Squad Builder Redesign

### Primary Purpose
Build an 11–12 player squad within 360 coin budget meeting positional minimums (GK≥1, DEF≥3, MID≥3, ATT≥2).

### Player Goal
Assemble the strongest possible squad considering stats, traits, cost, and synergies — while understanding which persistent synergies the squad composition unlocks.

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│  BUILD YOUR SQUAD              Budget ████████░░ 285 / 360   │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  SQUAD COMPOSITION                                        ││
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  ...  ││
│  │  │ GK  │ │ DEF │ │ MID │ │ ATT │ │ DEF │ │ ST  │        ││
│  │  │Gigi │ │Rolls│ │Capt │ │Kun  │ │Lahm │ │Zlat │        ││
│  │  │  8  │ │  6  │ │  8  │ │  8  │ │  7  │ │  9  │        ││
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘        ││
│  │  [✓] GK ≥ 1  [✓] DEF ≥ 3  [✓] MID ≥ 3  [✓] ATT ≥ 2      ││
│  │  Total: 11/12 players  ·  Cost: 285  ·  75 coins remain  ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────┐ ┌─────────────────────────────┐   │
│  │ PERSISTENT SYNERGIES │ │ SYNERGY PREVIEW ON HOVER     │   │
│  │                      │ │                              │   │
│  │ ✓ Iron Wall          │ │ When adding Terry Henri:    │   │
│  │   2+ CBs with DEF≥8  │ │   + Fast Break (w/ Bale)    │   │
│  │   (+15 DEF bonus)    │ │   + Clinical Edge (w/ Don)  │   │
│  │                      │ │                              │   │
│  │ ✓ Leadership Council │ │                              │   │
│  │   3+ leaders         │ │                              │   │
│  │   (fatigue 0.85)     │ │                              │   │
│  │                      │ │                              │   │
│  │ ✗ Tiki-Taka          │ │                              │   │
│  │   Need 2+ technical  │ │                              │   │
│  │   + playmaker        │ │                              │   │
│  └──────────────────────┘ └─────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  PLAYER POOL  (36 cards)    [ALL] [GK] [DEF] [MID] [ATT]││
│  │  ┌──────────────────────────────────────────────────────┐││
│  │  │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐    │││
│  │  │ │ST Terry │ │ST Big   │ │ST El    │ │ST The   │    │││
│  │  │ │HENRI    │ │ZLAT  8  │ │CANÍBAL  │ │WAZ   8  │    │││
│  │  │ │▆▆▆▆▆▆▆▆▆│ │▆▆▆▆▆▆▆▆ ▆│ │▆▆▆▆▆▆▆▆ │ │▆▆▆▆▆▆▆ ▆│    │││
│  │  │ │pacey    │ │physical │ │pacey    │ │leader   │    │││
│  │  │ │clinical │ │technical│ │poacher  │ │physical │    │││
│  │  │ │ 42 ◎ ✓  │ │ 32 ◎    │ │ 38 ◎    │ │ 31 ◎    │    │││
│  │  │ └─────────┘ └─────────┘ └─────────┘ └─────────┘    │││
│  │  └──────────────────────────────────────────────────────┘││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  PLAYER COMPARISON (side-by-side)                         ││
│  │  ┌──────────────┬──────────────┬──────┐                  ││
│  │  │ Terry Henri  │ Big Zlat     │ Diff │                  ││
│  │  │ ST · cost 42 │ ST · cost 32 │      │                  ││
│  │  │ ATK 9 █████  │ ATK 8 ████   │ +1   │                  ││
│  │  │ PAC 9 █████  │ PAC 5 ██▌    │ +4   │                  ││
│  │  │ PAS 6 ███    │ PAS 7 ███▌   │ -1   │                  ││
│  │  │ DEF 1 ▌      │ DEF 2 ▌      │ -1   │                  ││
│  │  │ SPC 8 ████   │ SPC 10 █████ │ -2   │                  ││
│  │  │ pacey        │ physical     │      │                  ││
│  │  │ clinical     │ technical    │      │                  ││
│  │  └──────────────┴──────────────┴──────┘                  ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  [◂ BACK]                           [CONFIRM SQUAD ▸]       │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Budget Tracker** | Prominent horizontal progress bar + text. Fills from left, color: `accent` when under budget, `danger` when over. Text: "Budget: 285 / 360" with `gold` numbers. Animated width transitions. |
| **Squad Composition Strip** | Horizontal pill row showing drafted players. Color-coded by position group: GK=`gold`, DEF=`accent`, MID=`info`, ATT=`danger`. Each pill shows name + cost. Click to remove. Hover highlights with glow. Max 12 pills with `+empty` slots shown as dashed borders. |
| **Composition Requirements** | 4 badges (GK ≥1, DEF ≥3, MID ≥3, ATT ≥2) displayed horizontally below squad strip. Met = `accent` border + checkmark. Unmet = `danger` border. Updates in real-time. |
| **Position Filter Tabs** | Horizontal tabs: ALL, GK, DEF, MID, ATT. Sub-tabs (e.g., CB, FB, CDM, CM, CAM, LW, RW, ST) appear below when group tab is active. `accent` glow on active. |
| **Player Card Grid** | Responsive grid (min 200px per card). Each card shows: position badge, name, cost, 5 stat bars (ATK/PAC/PAS/DEF/SPC), traits. Selected cards have `accent` border + ✓ checkmark + 0 0 12px glow. Unselected have `border` border. Hover: border → `border-bright`, bg → `surface-raised`. |
| **Persistent Synergy Panel** (NEW) | Right sidebar (or collapsible panel). Shows which squad-persistent synergies are currently unlocked, which are close (show progress: 2/3 traits needed), and what each provides. Updates in real-time as players are added/removed. Synergies fire immediately at match start — this panel shows the "locked" set. |
| **Synergy Preview on Hover** (NEW) | When hovering a player card, a tooltip or adjacent panel shows which new persistent synergies would unlock if that player were added. List format: synergy name + short effect description. |
| **Player Comparison View** (NEW) | Two-slot comparison dock at the bottom. Drag a player card or click "Compare" to add them to slots A and B. Side-by-side stat view with difference column. Stats better in A are green, worse are red. Traits compared side-by-side. Cost difference shown. Close button on each slot. |
| **OOP Penalty Preview** (NEW) | Within player comparison or as a badge on each player card: shows natural position and how well they'd fit each slot position. Uses color coding: natural=accent, adjacent=gold, different=warn, blocked=danger. |
| **Total Cost Counter** | Gold text at bottom-right of squad composition: "Cost: 285 · 75 remain". Turns danger when over budget. |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Budget bar, squad composition strip, composition req badges, position tabs, player grid |
| **Expandable / Conditional** | Persistent synergy panel (collapsible sidebar), Player comparison dock (appears when 1+ players selected for compare), Synergy preview tooltip (on hover) |
| **Hidden / Modal** | Detailed OOP penalty breakdown (expand per-player via click), Player full stats card (click to expand inline) |

### Interactions

| Trigger | Action |
|---------|--------|
| Click player card | Toggle select/deselect (adds to/removes from squad). Max 12. Toast if max reached. |
| Right-click player card | Add to comparison slot A. Right-click another for slot B. |
| Hover player card (unselected) | Show synergy preview tooltip: "Would unlock: Iron Wall, Fast Break". Also show cost impact. |
| Hover selected player | Highlight in squad strip. Show removal hint (click to remove). |
| Click pill in squad strip | Remove player from squad (with confirmation highlight, 0.2s fade-out) |
| Click position tab | Filter grid. Sub-tabs appear or update. |
| Click sub-tab | Filter to specific position. |
| Click "Compare" button (bottom dock) | Opens comparison view with two drop-zones. |
| Click comparison slot X | Remove player from comparison. |
| Keyboard: 1-5 | Quick-select position tabs (1=ALL, 2=GK, 3=DEF, 4=MID, 5=ATT) |
| Keyboard: Esc | Clear comparison slots |
| Click Confirm Squad | Validate: composition reqs met, budget not exceeded. If valid: transition to Formation Select. If invalid: shake animation on error badge, toast message. |

### Transition In
- Slide from right 0.3s
- Squad composition strip populates instantly (if returning from Formation)
- Player cards stagger in rows with 0.05s delay per card

### Transition Out
- To Formation Select: slide-left 0.3s
- To Title: slide-right 0.3s

---

## 3. Formation Select

### Primary Purpose
Choose a formation that amplifies the squad's strengths and mitigates weaknesses. Formations provide position bonuses/penalties and a global multiplier.

### Player Goal
Find the formation that best fits the drafted squad — maximizing position coverage and bonus synergy.

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│             CHOOSE FORMATION                                  │
│    Browse formations. Select the one that fits your squad.     │
│                                                              │
│                    ●  ○  ○  ○  ○  ○                          │
│              ┌───────◂ [CAROUSEL] ▸───────┐                 │
│              │                            │                 │
│              │    ╔══════════════════╗    │                 │
│              │    ║    PITCH DIAGRAM  ║    │                 │
│              │    ║  •  •  •  •  •  ║    │                 │
│              │    ║   •  •     •    ║    │                 │
│              │    ║     •  •  •     ║    │                 │
│              │    ║      •  •       ║    │                 │
│              │    ║       [GK]      ║    │                 │
│              │    ╚══════════════════╝    │                 │
│              │                            │                 │
│              │      4-3-3                 │                 │
│              │    Formation 2 / 6         │                 │
│              └────────────────────────────┘                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  4-3-3 — Wingers thrive. ST and CDM stretched. +5% global││
│  │                                                          ││
│  │  ═══ SQUAD FIT ═══════════════════════  ┌────────────┐  ││
│  │  GK  2 in squad  → Gigi Wall, Rocket    │ AUTO-REC   │  ││
│  │  CB  3 in squad  → El Cap, JT, Rolls    │  Best Fit  │  ││
│  │  FB  2 in squad  → Dani Elvis, Lahm     │            │  ││
│  │  CM  3 in squad  → Xav, Don, Stevie     │  4-2-3-1   │  ││
│  │  LW  2 in squad  → Bale, Dictator       │  (92% fit) │  ││
│  │  RW  1 in squad  → Arjen Cutback        │            │  ││
│  │  ST  2 in squad  → Terry, Big Zlat      │  [APPLY]   │  ││
│  │  ═══════════════════════════════════════└────────────┘  ││
│  │                                                          ││
│  │  POSITION BONUSES                                         ││
│  │  [+20 LW] [+20 RW] [-15 ST] [-10 CDM]                    ││
│  │                                                          ││
│  │  GLOBAL MULTIPLIER: ×1.05                                ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  [◂ BACK TO SQUAD]              [CONFIRM FORMATION ▸]        │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Carousel** | Horizontal scroll with ◂ ▸ arrows and dot indicators (6 formations). Each card shows pitch diagram + formation name. Active card has `accent` border + glow. Transition between cards: smooth slide 0.3s. |
| **Pitch Diagram** | `pitch-green` background with `pitch-line` markings. Formation slots rendered as `accent` dots at position coordinates. GK always at bottom, ST at top. Slots color-coded by group. Size: ~220px max height, aspect ratio 68:105. |
| **Detail Panel** | Below carousel. Shows: formation name, description, global mult, position bonuses as tags (+green / -red), and MOST IMPORTANTLY: squad fit table. |
| **Squad Fit Table** (NEW) | Lists each position the formation requires, how many players from the drafted squad can fill it, their names, and a fit quality indicator (natural=green, adjacent=gold, OOP=warn). Rightmost column: "Coverage" as fraction (e.g. 3/2 = over-covered). Summarizes how well the squad slots into this formation. |
| **Auto-Recommend Button** (NEW) | Gold-accented button at top-right of detail panel. Click: evaluates all 6 formations against the current squad, picks the one with best fit (fewest OOP slots, most position bonuses utilized), highlights it in carousel. Shows recommendation badge: "Best Fit → 4-2-3-1 (92%)". |
| **Position Bonus Tags** | Small pills: `+20 LW` in green (`accent` background), `-15 ST` in red (`danger` background). Color-coded for immediate visual parsing. |
| **Global Multiplier Display** | Large gold number: `×1.05` with `gold-glow`. |
| **Confirm Button** | Primary. Disabled until a formation is selected (clicked in carousel). Active formation is preselected by auto-recommend on first visit. |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Carousel with pitch diagram, detail panel, auto-recommend button |
| **Expandable** | Position bonus rationale (hover over bonus tag shows: "Wingers +20 because wide play suits pacey wide players — your Bale Out (PAC 10) would get +20 chips per phase") |
| **Hidden** | None critical |

### Interactions

| Trigger | Action |
|---------|--------|
| Click ◂ / ▸ | Navigate carousel left/right. Wrap around (6 → 1, 1 → 6). |
| Click dot indicator | Jump to that formation. |
| Swipe left/right (touch) | Navigate carousel. |
| Click formation card | Select formation. Card gets `accent` border + glow. Detail panel updates. |
| Click Auto-Recommend | Evaluate all formations, navigate carousel to best fit, highlight with gold badge "RECOMMENDED". |
| Hover bonus tag | Tooltip with player-specific impact. |
| Hover squad fit row | Highlight corresponding pitch diagram positions. |
| Keyboard: ← → | Navigate carousel. |
| Keyboard: Enter | Confirm formation. |
| Click Confirm | Validate formation selected. Transition to Phase Selection screen. |

### Transition In
- Slide from right 0.3s
- Carousel card scales in from 0.9 to 1.0 with 0.2s ease-out
- Dot indicators appear with stagger 0.05s
- Auto-recommend fires immediately (0.1s delay) to preselect best formation

### Transition Out
- To Phase Selection: slide-left 0.3s
- To Squad Builder: slide-right 0.3s

---

## 4. Phase Selection

### Primary Purpose
Deal 6 phase cards from 13, pick exactly 3 in order. Order determines combo chains between phases.

### Player Goal
Choose 3 phases that: (1) exploit opponent weaknesses, (2) match the squad's strongest players, (3) chain combos for bonus effects.

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                    PICK YOUR PHASES                           │
│  Round 1 · vs Wolves FC · Target: 200K                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  📡 SCOUTING REPORT                                       ││
│  │  Wolves are weak against Set Pieces (+30%).              ││
│  │  They counter-attack well — Direct Play is risky (-30%). ││
│  │  Minor: Build-Up slightly effective (+15%).              ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ GOAL KICK│ │WIDE ATTK │ │ COUNTER  │ │SET PIECE │       │
│  │  GK·CB·CB│ │ FB·LW·RW │ │ LW·ST·RW│ │ CAM·CB·ST│       │
│  │ 🛡️ DEF   │ │ ⚡ PAC    │ │ ⚡ PAC   │ │ ✨ SPC    │       │
│  │          │ │          │ │          │ │          │       │
│  │SYN:Clean │ │SYN:Strtch│ │SYN:Overld│ │SYN:SetPc │       │
│  │ Sheet ✓  │ │ Bckln ✓  │ │          │ │ Threat   │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐                                  │
│  │TIKI-TAKA │ │DIRECT PLY│        (6 cards dealt)            │
│  │ CM·CM·CAM│ │LW/RW·ST·CM│                                 │
│  │ 🔄 PAS   │ │ ⚡ ATK     │                                 │
│  └──────────┘ └──────────┘                                  │
│                                                              │
│  YOUR PICKS (in order):                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐         │
│  │ [1] GOAL KICK│→│ [2] WIDE ATTK│→│ [3] COUNTER │         │
│  │   🛡️         │  │   ⚡          │  │   ⚡        │         │
│  │              │  │              │  │  [REMOVE]   │         │
│  └──────────────┘  └──────────────┘  └────────────┘         │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  CHAIN PREVIEW                                            ││
│  │  ①🛡️ Defensive → ②⚡ Transition: ✕1.5 MULT               ││
│  │    "Absorb pressure, hit on break"                       ││
│  │  ②⚡ Transition → ③⚡ Transition: +35 CHIPS               ││
│  │    "Rapid succession — no time to reset"                 ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  [UNDO LAST PICK]                  [CONFIRM PHASE ORDER ▸]   │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Round Info Bar** | Compact header: Round N · vs Opponent · Target score. Body font, muted. |
| **Scouting Report Panel** (NEW) | `surface` panel with gold-accented border. Shows opponent adjustments for this round: which phases get buffed (green "+30%"), which get nerfed (red "-30%"), any minor adjustments. Icons for each affected phase. Persists as reference. |
| **Phase Card Grid** | 6 dealt cards in a 3×2 grid (or auto-fill). Each card: phase icon (emoji), name (display font), slots required (mono), tag category (colored pill), chip formula hint, and — critically — which synergies are likely to fire with the current squad (preview from squad builder data). Cards that match scouting buffs get a green "↑" badge; nerfed cards get red "↓". |
| **Selection Order Tray** | Below the deal grid: 3 sequential slots showing picked phases. Each shows position number (1, 2, 3) in gold circle + phase name. Arrow indicators between slots. Click a filled slot to remove that pick (undo). Empty slots show dashed border with "Pick a phase" placeholder. |
| **Combo Chain Preview** (NEW) | Below the selection tray: shows which combo chains will fire based on the selected phase order. Each chain shown as: tag A → tag B, effect type + value, flavor description. Updates in real-time as picks change. Golden glow for active chains, muted for potential chains. |
| **Synergy Confidence Badges** | On each phase card: small badges showing which phase synergies the current squad can trigger for this phase. Green ✓ for "confident" (players exist), yellow ~ for "possible" (need OOP placement), grey ✗ for "unavailable" (missing key positions/stats). |
| **Undo Button** | Removes the last picked phase from the selection tray, restoring it to the deal grid. Re-evaluates combo chains. |
| **Confirm Button** | Primary. Enabled only when exactly 3 phases are picked. |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Round info, scouting report, 6 dealt phase cards, selection tray, combo chain preview, confirm button |
| **Expandable** | Per-phase card: click to see detailed synergy breakdown (which specific players would trigger which synergies), slot requirements expanded |
| **Hidden** | Phase detail tooltips (hover for stat weights) |

### Interactions

| Trigger | Action |
|---------|--------|
| Click phase card | Add to next available slot in selection tray. Card animates: scale down → slide to tray position → scale up. Card in grid deactivates (opacity 0.4). If 3 already picked, do nothing (toast). |
| Click filled slot in tray | Remove phase (undo). Card animates back to grid. Combo chains re-evaluate. |
| Click "Undo Last" button | Same as removing the 3rd slot. |
| Hover phase card | Glow border. Show synergy confidence tooltip. If phase matches scouting buff, show expected score boost. |
| Hover combo chain row | Highlight the two contributing phase cards in the tray. |
| Keyboard: 1-6 | Select card number 1-6 (grid position). |
| Keyboard: Backspace | Undo last pick. |
| Click Confirm | Lock in phases. Transition to Match screen. |

### Transition In
- Slide from right 0.3s
- Phase cards deal animation: cards fly in from center with stagger 0.08s each, slight rotation
- Scouting report panel slides down from top

### Transition Out
- Confirm: all cards shrink to center (0.2s), brief loading pulse, transition to Match
- Back: slide-right 0.3s to Formation Select

---

## 5. Match Screen

### Primary Purpose
Place players into phase slots, trigger synergies, submit the phase, and see scoring. This is the core gameplay loop — repeated 3× per round, 3 rounds per match.

### Player Goal
Maximize phase score by strategically assigning players to slots — balancing chip generation, synergy activation, and fatigue management — while trying to beat the round target.

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│  [YOUR XI]  0 - 0  [WOLVES FC]    Target: 200K  Score: 0    │
│  Round ● ○ ○   Phase ● ○ ○                                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  🛡️ GOAL KICK  [DEF]  Defensive Third                     ││
│  │  Keeper launches long — defenders win the header          ││
│  │  Fatigue: ×0.85  ·  Opponent: neutral                     ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  Phase Score:    0  ♣    Momentum: ×1.0                      │
│  Synergies: [Clean Sheet ready] [Organised Defence ready]    │
│                                                              │
│ ┌─────────────────────────┐ ┌──────────────────────────────┐ │
│ │  ⚽ PITCH / FORMATION    │ │  SINERGIES PANEL              │ │
│ │                         │ │                               │ │
│ │       [ST empty]        │ │  ● Clean Sheet                │ │
│ │                         │ │    (GK + CB DEF ≥ 15)         │ │
│ │  [LW]   [CAM]   [RW]   │ │    +20 chips                  │ │
│ │                         │ │    Gigi Wall + El Capitán ✓   │ │
│ │    [CM]       [CM]     │ │                               │ │
│ │                         │ │  ○ Organised Defence          │ │
│ │      [CDM empty]        │ │    (CB+CB DEF ≥ 16)          │ │
│ │                         │ │    Need: 2nd CB placed        │ │
│ │  [FB full] [CB] [FB]   │ │                               │ │
│ │                         │ │  ○ Stretch Backline           │ │
│ │      [GK full]          │ │    (FB+LWB PAC≥15)            │ │
│ │                         │ │    Need: LW w/ pace           │ │
│ └─────────────────────────┘ └──────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │  PLAYER ASSIGNMENT DOCK                                   │ │
│ │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │ │
│ │  │GK Gigi  │ │CB El Cap│ │CB JT    │ │FB Dani  │  ...   │ │
│ │  │DEF 10   │ │DEF 10   │ │DEF 10   │ │PAC 9    │        │ │
│ │  │fatigue✓ │ │fatigue✓ │ │fatigue✓ │ │fatigue✓ │        │ │
│ │  │ [SLOT 1]│ │ [SLOT 2]│ │ [ASSIGN]│ │ [ASSIGN]│        │ │
│ │  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │ │
│ └──────────────────────────────────────────────────────────┘ │
│                                                              │
│  [🤖 AUTO-FILL]                      [SUBMIT PHASE ▸]        │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Match Header** | Scoreline (You 0-0 Them), opponent name, running target, running score. Top of screen, compact. |
| **Progress Dots** | Round dots (3 circles, filled = completed, gold = current, empty = upcoming) + Phase dots (same). Below header. |
| **Phase Context Bar** | Full-width `surface` panel. Shows current phase: icon, name, tag (e.g., `[DEF]` pill), weight description, fatigue mult, opponent adjustment. Current context for all decisions below. |
| **Live Score Bar** | Shows real-time preview of phase score as players are placed. Three segments: chips value (gold) · add_mult (info) · x_mult (accent). Plus synergy badges that light up when triggered. Updates instantly on player assignment. |
| **Pitch/Formation Visual** (NEW) | Left panel. Shows the formation with player placements visualized as dots on a pitch diagram. Empty slots = dashed outline, filled = solid with player initials. Color-coded by position group. Adjacent to the current phase's required slots overlaid on the formation. Shows which formation slot each phase placeholder maps to. |
| **Synergies Panel** (ENHANCED) | Right panel. Lists all phase-specific synergies. Three states: `● Fired` (green dot, shows contributors), `○ Ready` (gold dot, shows what's needed), `· Inactive` (grey, doesn't apply to this phase). Click to expand detail with trigger conditions. Real-time updates as players are placed. |
| **Player Assignment Dock** (ENHANCED) | Bottom panel. Horizontal scroll of all squad players. Each shows: position, name, key stat, fatigue indicator (green bar = fresh, yellow = tired, red = exhausted), current assignment (which slot they're in, or unassigned). Drag-and-drop support. Clicking a player opens the slot picker modal. |
| **Player Picker Modal** | Overlay modal when clicking a slot. Shows all eligible (non-GK for outfield, GK for GK) players with: name, stat columns (ATK/PAC/PAS/DEF/SPC), predicted chips, OOP penalty badge, synergy preview (which synergies they'd newly trigger). Click to assign. Close button / click outside to dismiss. |
| **Fatigue Indicators** | On each player card in dock: colored dot + multiplier. Green = 1.0 (fresh), yellow = 0.7-0.99 (tired), orange = 0.5-0.69 (fatigued), red = <0.5 (exhausted). Also shows remaining uses before exhaustion. |
| **Momentum Indicator** | In live score bar: shows current momentum multiplier (×1.0, ×1.2, ×1.5) based on phase index. Animated pulse when it increases. |
| **Auto-Fill Button** | Fills all empty slots with best-fit players (max chips, minimal OOP penalty). One-click, instant. Highlight filled slots with brief pulse. |
| **Submit Button** | Primary. Validates all slots filled. If valid: resolves phase, transitions to Phase Result. If invalid: shake empty slots, toast "Fill all slots first". |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Match header, progress dots, phase context bar, live score, pitch diagram (left), synergy panel (right), player dock (bottom) |
| **Expandable** | Synergy details (click to expand — shows trigger formula, contributors, effect value), Player detail (click player in dock → expanded stat card overlays dock) |
| **Modal** | Player picker (click slot → modal overlay with player grid for that slot) |

### Interactions

| Trigger | Action |
|---------|--------|
| Click slot on pitch diagram | Open player picker modal for that slot, filtered to eligible players. |
| Click player in dock | If unassigned: highlight. If assigned: show which slot and allow reassignment. |
| Drag player → drop on slot | Assign player to slot. OOP penalty preview shown during drag. Slot lights up green if valid drop. |
| Click player in picker modal | Assign to active slot. Modal closes. Slot updates on pitch. Live score updates. |
| Click synth row in synergy panel | Expand to show trigger formula + current status. |
| Hover player in dock | Show quick tooltip: full stats, fatigue %, synergy potential. |
| Click Auto-Fill | All slots fill instantly. 0.1s stagger per slot with glow pulse. |
| Click Submit | Phase resolves → animation: score counts up in live bar → brief flash → transition to Phase Result. |
| Keyboard: Tab | Cycle focus through empty slots. |
| Keyboard: Enter | Open picker for focused slot. |
| Keyboard: S | Submit phase. |
| Keyboard: A | Auto-fill. |

### Transition In
- Slide from right 0.3s
- Pitch diagram builds: lines draw in (0.2s), slot dots appear with stagger (0.05s each)
- Player dock cards slide up from bottom (0.2s stagger)
- Synergy panel populates with 0.1s delay

### Transition Out
- To Phase Result: fade through white/gold flash (0.15s) → slide-left (0.3s) into result
- Phase completion: player cards on pitch animate upward/off screen, live score cascades up

---

## 6. Phase Result

### Primary Purpose
Show the scoring breakdown after each completed phase — Balatro-style formula visualization — and let the player understand what contributed to their score.

### Player Goal
Understand which players and synergies drove the score, learn from the breakdown, and decide whether to continue (if target not yet met) or celebrate (if auto-win triggered).

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│           🛡️ GOAL KICK — Phase 1 Complete                     │
│                                                              │
│                   ╔═══════════════════╗                      │
│                   ║      42,350       ║  ← score counting up │
│                   ╚═══════════════════╝                      │
│              Target: 200,000  ·  Round: 42,350               │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  FORMULA BREAKDOWN            chips × add_mult × x_mult  ││
│  │                                                          ││
│  │  CHIPS           ADD_MULT          X_MULT                ││
│  │  ┌─────────┐    ┌─────────┐       ┌─────────┐           ││
│  │  │  8,470  │ ×  │   1.0   │   ×   │  5.00   │ = 42,350  ││
│  │  │         │    │   +0    │       │ ×3.0 fm │           ││
│  │  │Players  │    │         │       │ ×1.5 mm │           ││
│  │  │+pos bon │    │         │       │ ×1.05 fm│           ││
│  │  │+synergy │    │         │       │ ×0.85 ft│           ││
│  │  └─────────┘    └─────────┘       └─────────┘           ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  PLAYER CONTRIBUTIONS                                     ││
│  │  #  PLAYER         POS   BASE   FORM  FATIGUE  CHIPS     ││
│  │  1  Gigi Wall      GK    1,200  DEF×3  ×1.00   1,200    ││
│  │  2  El Capitán     CB    2,400  DEF×5  ×1.00   2,400    ││
│  │  3  JT Rock        CB    3,500  DEF×5  ×0.85   2,975    ││
│  │  ──────────────────────────────────────────────────────  ││
│  │  + Position bonuses: +200                                 ││
│  │  + Synergy chips:   +400                                 ││
│  │  + Carryover:       +0                                    ││
│  │  TOTAL CHIPS:       8,470                                 ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  ▶ SYNERGY BREAKDOWN (3 fired)                      ▼    ││
│  │  ┌──────────────────────────────────────────────────────┐││
│  │  │ PHASE SYNERGIES (2 fired)                            │││
│  │  │ ● Clean Sheet      +20 chips    Gigi Wall + El Cap   │││
│  │  │ ● Organised Def     +30 chips    El Cap + JT Rock    │││
│  │  │                                                      │││
│  │  │ PERSISTENT SYNERGIES (1 active)                      │││
│  │  │ ● Iron Wall        +10% DEF→chips  All CBs          │││
│  │  │                                                      │││
│  │  │ COMBO CHAINS (0 this phase)                          │││
│  │  │                                                     │││
│  │  └──────────────────────────────────────────────────────┘││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  ⚡ AUTO-WIN! Round target beaten in 1 phase!             ││
│  │  +3 Morale earned. Remaining 2 phases skipped.           ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│                       [CONTINUE ▸]                            │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Hero Score** | Large gold number (56px+) that counts up from 0 to final score with eased animation (cubic ease-out, 0.8s). `gold-glow` text-shadow. Phase name and number above. |
| **Target vs. Running Total** | Below hero: "Target: 200,000 · Round so far: 42,350". Shows progress toward target. |
| **Formula Visualization** (NEW - CORE) | Balatro-style three-column layout: CHIPS × ADD_MULT × X_MULT = TOTAL. Each column is a `surface` card. Chips breakdown within its card: player contributions, position bonuses, synergy chips, carryover. Add_mult breakdown: base (1.0) + synergy add_effects. X_mult breakdown: all multiplicative factors (formation, momentum, phase mult, fatigue, synergy x_mults). Shows the exact multiplication path. |
| **Player Contribution Table** | Scrollable table with columns: #, Player, Position, Base (stat×formula), Formula Applied (e.g., DEF×5), Fatigue Mult, Final Chips. Sum row at bottom. Color-coded by position group. |
| **Synergy Breakdown Accordion** | Three sections (collapsible): Phase Synergies, Persistent Synergies, Combo Chains. Each triggered synergy shows: name, effect type+value, contributing players. Non-triggered but present synergies shown greyed out with "missed" indicator. Expand/collapse arrow. |
| **Auto-Win Banner** (NEW) | Conditional: only shown if running round score has already exceeded the target. Gold background strip with celebration text. Shows morale earned. "Remaining phases skipped" note. |
| **Continue Button** | Primary. Advances the game: if more phases remain, back to Match; if round complete, to Round Result; if match complete, to Shop or Campaign. |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Hero score, formula breakdown (3 columns), player contribution table summary (top 3 rows), continue button |
| **Expandable** | Full player contribution table (scroll), synergy breakdown accordion sections |
| **Conditional** | Auto-win banner (only when triggered) |

### Interactions

| Trigger | Action |
|---------|--------|
| Score animation | Automatic on entry. 0.8s count-up. Player can click to skip animation (jump to final). |
| Click synergy accordion header | Expand/collapse that section. Arrow rotates. |
| Hover player row | Highlight that player in the formula breakdown (which chips they contributed). |
| Hover formula column | Highlight the column and show extended description tooltip. |
| Click Continue | If more phases: transition back to Match. If round done: transition to Round Result. |

### Transition In
- Screen fades in from white/gold flash (0.15s)
- Hero score animates counting up (0.8s, skip on click)
- Formula columns slide in from bottom with 0.15s stagger
- Player table rows appear with 0.05s stagger per row
- Synergy accordion expands with 0.2s ease

### Transition Out
- Continue: fade-out 0.2s → brief transition → next screen

---

## 7. Shop

### Primary Purpose
Between rounds, spend morale earned from wins to buy buffs, recover fatigue, and prepare for upcoming rounds.

### Player Goal
Make strategic purchases that maximize the next round's chances — choosing between immediate power (items) and resource conservation (morale).

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                      💰 SHOP                                  │
│             Spend your morale before the next round           │
│                                                              │
│         ┌──────────────────────────────┐                    │
│         │  💎 MORALE: 5                 │                    │
│         │  ████████████████░░░░░░░░░░░  │                    │
│         └──────────────────────────────┘                    │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  SQUAD STATUS                                             ││
│  │  Gigi Wall    GK  ████████░░  fresh                       ││
│  │  El Capitán   CB  ██████████  fresh                       ││
│  │  JT Rock      CB  ████░░░░░░  tired (×0.70)              ││
│  │  Dani Elvis   FB  ██████████  fresh                       ││
│  │  ... (scroll for more)                                    ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ 🔍 SCOUT     │ │ 💉 INSPIRED  │ │ 🔄 FORMATION │         │
│  │ REPORT       │ │ SUB          │ │ TWEAK        │         │
│  │              │ │              │ │              │         │
│  │ See all 8    │ │ Restore one  │ │ Swap to a    │         │
│  │ phase cards  │ │ player's     │ │ different    │         │
│  │ next round   │ │ fatigue      │ │ formation    │         │
│  │              │ │              │ │              │         │
│  │  ⚡ COST: 2  │ │  ⚡ COST: 2  │ │  ⚡ COST: 3  │         │
│  │  [BUY]       │ │  [BUY]       │ │  [BUY]       │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │ ⚽ SET PIECE │ │ 📋 TACTICAL  │ │ 👴 VETERAN'S │         │
│  │ DRILL        │ │ SHIFT        │ │ WISDOM       │         │
│  │              │ │              │ │              │         │
│  │ Next round:  │ │ Next round:  │ │ Random trait │         │
│  │ +40 chips    │ │ +5 add_mult  │ │ bonus to one │         │
│  │              │ │              │ │ player       │         │
│  │  ⚡ COST: 4  │ │  ⚡ COST: 5  │ │  ⚡ COST: 6  │         │
│  │  [BUY]       │ │  [BUY]       │ │  [BUY]       │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
│                                                              │
│  ACTIVE BUFFS: (none yet)                                    │
│                                                              │
│  [SKIP SHOP — Save morale]          [CONTINUE TO NEXT ROUND ▸]│
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Morale Display** | Large gold number + progress bar. "💎 MORALE: 5". Bar fills with gold. Animated transitions on spend. |
| **Squad Status Panel** (NEW) | Compact list of all 11-12 squad players. Each row: name, position, fatigue bar (colored: green fresh, yellow tired, orange fatigued, red exhausted), fatigue multiplier number. Players marked "tired" or below get a subtle warning glow — encouraging fatigue-recovery purchases. |
| **Shop Item Cards** | Grid of 6 items (3×2). Each card: icon, name, description, cost badge (gold), rarity border (common=border, uncommon=gold, rare=accent). Buy button enabled if affordable, disabled (greyed) if not. Purchased items show ✓ and card dims. |
| **Item Tooltips** (NEW) | Hover over shop item: expanded tooltip showing exact effect, duration, and any synergies with current squad state. For "Inspired Sub": shows which player would benefit most (lowest fatigue). For "Veteran's Wisdom": shows possible trait outcomes. |
| **Active Buffs Strip** | Below item grid: shows currently purchased buffs for the next round. Icons + names. "Active for next round" label. |
| **Skip Shop Button** | Secondary button. Saves all morale for later rounds. |
| **Continue Button** | Primary. Advances to next round's Phase Selection. |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Morale display, squad status panel (collapsed to 4 visible + "show all"), shop item grid, active buffs, continue button |
| **Expandable** | Full squad status (click "show all"), item tooltips (hover) |
| **Hidden** | Item purchase confirmation modal |

### Interactions

| Trigger | Action |
|---------|--------|
| Hover shop item | Tooltip with detailed effect. If context-dependent (e.g., Inspired Sub), highlight most-beneficial player in squad status. |
| Click Buy | Deduct morale, apply buff to `G.shopBuffs`, dim card + show ✓. If insufficient morale: button shakes, nothing happens. |
| Hover squad status player | Show full fatigue detail: current mult, usage count, projected next phase contribution. |
| Click "show all" in squad status | Expand to show full 12-player list with scroll. |
| Click Skip Shop | Confirmation toast: "Morale saved. 5 morale carried over." Continue to next screen. |
| Click Continue | If any morale remains, toast: "Unspent morale carries over." Transition to next round Phase Selection. |

### Transition In
- Slide from right 0.3s
- Morale number counts up from 0 to current (0.4s)
- Shop item cards stagger in: top row left→right (0.1s stagger), bottom row (0.2s delay)

### Transition Out
- To Phase Selection: slide-left 0.3s
- Brief loading state (0.3s) while next round initializes

---

## 8. Round Result & Campaign Map

### Primary Purpose
Show round win/loss result within the broader match context, and display campaign progress across all 5 matches.

### Player Goal
Understand match status (2 rounds to win), see campaign progression, and mentally prepare for the next round or match outcome.

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                    ROUND WON! 🎯                              │
│                                                              │
│         Your Score              Target                       │
│          185,400    vs        200,000                        │
│              (Lost by 14,600)                                 │
│                                                              │
│       ┌──────────────────────────────────────┐               │
│       │  MATCH PROGRESS                      │               │
│       │                                      │               │
│       │  Round 1:  WON  ✓ (210K / 200K)     │               │
│       │  Round 2:  LOST ✗ (185K / 200K)     │               │
│       │  Round 3:  ● CURRENT                 │               │
│       │                                      │               │
│       │  Your XI  1 — 1  Wolves FC           │               │
│       │  Next round is DECISIVE!             │               │
│       └──────────────────────────────────────┘               │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  CAMPAIGN MAP                                             ││
│  │                                                          ││
│  │  [1] Group ──→ [2] R16 ──→ [3] QF ──→ [4] SF ──→ [5] F ││
│  │      ✓WON         ●HERE       ○          ○         ○    ││
│  │   Wolves FC    Inter Y-N   B. M-flp   Man City  Galáct. ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  [CONTINUE TO SHOP ▸]           [VIEW MATCH HISTORY]         │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Verdict Banner** | Large text: "ROUND WON!" (green) or "ROUND LOST" (red) with appropriate glow. |
| **Score Comparison** | Two large numbers side by side: Your Score vs. Target. Difference shown. Color-coded: green if exceeding target, red if short. |
| **Match Progress Panel** | Shows all rounds in current match (up to 3). Each round: status (WON ✓ / LOST ✗ / CURRENT ●), score achieved, target. Scoreline between teams. Status message: "Next round is DECISIVE!" or "Match point!" or "2-0, match won!". |
| **Campaign Map** (NEW) | Horizontal progression bar showing all 5 matches. Each match is a node: number, name, opponent, status (WON ✓ / LOST ✗ / CURRENT ● / UPCOMING ○). Connecting lines between nodes. Current match highlighted with gold border + glow. Previous matches show result. |
| **Match History Button** (NEW) | Opens a panel/modal with detailed breakdown of all completed matches: phase-by-phase scores, synergies fired, key players. |
| **Continue Button** | If match is won: "Continue to Shop ▸". If match lost: "View Campaign Results ▸". If round done but match not over: "Continue to Shop ▸". |

### Information Architecture

| Layer | Content |
|-------|---------|
| **Always Visible** | Verdict, score comparison, match progress panel, campaign map (compact), continue button |
| **Expandable** | Campaign map details (hover node for opponent scouting report), match history modal |
| **Hidden** | Phase-by-phase round replay (in match history modal) |

### Interactions

| Trigger | Action |
|---------|--------|
| Hover campaign map node | Tooltip: opponent name, difficulty tier, result (if played), target scores |
| Click campaign map node (completed) | Show quick summary: your score vs target, rounds won/lost |
| Click "View Match History" | Expand panel/modal showing all completed match details |
| Click Continue | Route: if match won → Shop. If match over and campaign won/lost → Campaign Complete. If round done → Shop. |

### Transition In
- Fade-in 0.3s
- Verdict text appears with dramatic scale-up (0.4s bounce)
- Score numbers count up (0.5s)
- Campaign map line draws from left to right (0.6s drawing animation)

### Transition Out
- To Shop: slide-left 0.3s
- To Campaign Complete: fade-to-black 0.5s → campaign screen

---

## 9. Campaign Complete

### Primary Purpose
Show final campaign result (victory or defeat), summarize all matches, and provide closure.

### Player Goal
Review performance, celebrate victory or process defeat, and decide to play again.

---

### Layout

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              🏆 CAMPAIGN COMPLETE — VICTORY! 🏆              │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  MATCH RESULTS                                           ││
│  │  ┌─────────────────────────────────────────────────────┐ ││
│  │  │ ✓ WON │ Group Stage      │ Wolves FC     │ 2-1    │ ││
│  │  │ ✓ WON │ Round of 16      │ Inter Y-N    │ 2-0    │ ││
│  │  │ ✓ WON │ Quarter Final    │ B. M-flp     │ 2-1    │ ││
│  │  │ ✓ WON │ Semi Final       │ Man City     │ 2-1    │ ││
│  │  │ ✓ WON │ THE FINAL        │ Galácticos   │ 2-0    │ ││
│  │  └─────────────────────────────────────────────────────┘ ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │  SQUAD HALL OF FAME                                      ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   ││
│  │  │Terry H.  │ │El Capitán│ │Gigi Wall │ │Don Andres│   ││
│  │  │ST ★ MVP  │ │CB ★ WALL │ │GK ★ LOCK │ │CM ★ ASST │   ││
│  │  │182K chps │ │4 cleans  │ │3 cleans  │ │14 syns   │   ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  STATS:  5 matches · 11 rounds won · 4.2M total score        │
│          Best round: 1.5M · Best phase: 520K                │
│                                                              │
│  [PLAY AGAIN ▸]                   [SHARE RESULT]             │
└──────────────────────────────────────────────────────────────┘
```

### Components

| Component | Description |
|-----------|-------------|
| **Verdict Banner** | "CAMPAIGN COMPLETE" — gold for victory, red for defeat. Trophy/emoji icon. |
| **Match Results List** | Scrollable table: match #, name, opponent, result (2-1, 2-0, etc.), W/L badge. Won rows have `accent` border-left, lost have `danger`. |
| **Squad Hall of Fame** (NEW) | Show the 11 players who played the campaign. Highlight top performers: most chips generated, most synergy contributions, most clean sheets. Player cards in a horizontal scroll with awards (MVP, Wall, Lock, Assist King, etc.). |
| **Stats Summary** | Total matches played, rounds won, total score, best round, best phase. Dense display. |
| **Play Again Button** | Resets game state, returns to Title screen. |
| **Share Result** (optional) | Copies a text summary for sharing. |

### Interactions

| Trigger | Action |
|---------|--------|
| Click Play Again | Reset G state, navigate to Title screen. |
| Hover match result row | Show expanded: rounds detail, key moments. |
| Hover hall of fame player | Show expanded stats tooltip. |
| Click Share | Copy text to clipboard. Toast confirmation. |

### Transition In
- Victory: gold particles/sparkle effect (CSS animation, 1.5s), screen fades in from black
- Defeat: red vignette fade-in, slower reveal
- Match results stagger in from bottom (0.1s per row)

### Transition Out
- Fade-out 0.3s → Title screen

---

## Screen Transition Map

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐
│  TITLE   │────→│ SQUAD BUILDER│────→│  FORMATION   │
│ (Screen1)│     │  (Screen 2)  │     │  (Screen 3)  │
└──────────┘     └──────────────┘     └──────┬───────┘
     ↑                                       │
     │                              ┌────────▼────────┐
     │                              │ PHASE SELECTION │
     │                              │   (Screen 4)    │
     │                              └────────┬────────┘
     │                                       │
     │                              ┌────────▼────────┐
     │                    ┌─────────│     MATCH       │←─────────┐
     │                    │         │   (Screen 5)    │          │
     │                    │         └────────┬────────┘          │
     │                    │                  │                   │
     │                    │         ┌────────▼────────┐          │
     │                    │         │  PHASE RESULT   │──────────┘
     │                    │         │   (Screen 6)    │  (more phases)
     │                    │         └────────┬────────┘
     │                    │                  │
     │                    │         ┌────────▼────────┐
     │                    │         │  ROUND RESULT   │←─────────┐
     │                    │         │   (Screen 8)    │          │
     │                    │         └───┬────────┬────┘          │
     │                    │             │        │               │
     │                    │    (more rounds)  (match over)       │
     │                    │             │        │               │
     │                    │             │  ┌─────▼──────┐        │
     │                    │             │  │    SHOP    │────────┘
     │                    │             │  │ (Screen 7) │ (next round)
     │                    │             │  └────────────┘
     │                    │             │
     │                    │      ┌──────▼────────┐
     │                    │      │   CAMPAIGN     │
     │                    └──────│   COMPLETE     │
     │                           │  (Screen 9)    │
     │                           └──────┬─────────┘
     │                                  │
     └──────────────────────────────────┘  (Play Again)
```

---

## Global Interaction Patterns

| Pattern | Description |
|---------|-------------|
| **Navigation** | Back buttons always in bottom-left. Primary action buttons bottom-right. No breadcrumbs — flat screen stack. |
| **Screen Transitions** | Slide-left for forward (deeper), slide-right for backward. Fade for reset/jump. Max 0.3s duration. |
| **Loading States** | Brief spinner (0.2s min, 0.5s max) when computing (phase resolution, auto-recommend). Avoid for instant operations. |
| **Empty States** | Dashed borders and muted placeholder text ("Pick a player", "No synergies yet"). Never blank. |
| **Error States** | Red border shake + toast notification. Inline validation messages next to affected component. |
| **Tooltips** | Appear on hover after 0.3s delay. `surface` background, `border` border, display font for labels, body font for details. Fade in 0.15s. |
| **Modals** | Dark overlay (rgba 0,0,0,0.65) with backdrop-blur. Modal has `surface-raised` bg, `accent` border, 12px padding. Close with ✕ button or click outside. |
| **Keyboard** | Full keyboard navigation. Tab through interactive elements. Enter to confirm. Esc to cancel/back. Arrow keys for carousels. Number keys for quick-select. |
| **Focus States** | `outline: 2px solid var(--accent); outline-offset: 2px` on all interactive elements. |
| **Reduced Motion** | `@media (prefers-reduced-motion: reduce)` disables all animations, sets durations to 0.01s. |
| **Sound Design** | Placeholder hooks: `onSynergyFire`, `onPhaseSubmit`, `onRoundWin`, `onShopBuy`, `onAutoWin`. Implementation deferred. |

---

## Data Flow Between Screens

```
GAME STATE (G):
  selectedIds      → Squad Builder → Formation Select
  squad[]          → Formation Select → Match
  formation        → Formation Select → Match
  matchIdx         → Round Result / Campaign Map
  roundScore       → Phase Result → Round Result
  phaseIdx         → Match → Phase Result
  fatigue{}        → Match → Squad status (Shop)
  morale           → Phase Result (earned) → Shop (spent)
  shopBuffs{}      → Shop → Match (applied)
  persistentBuffs  → Squad Builder (preview) → Match (active)
  phaseFatigue{}   → Phase Selection (advisory) → Match
```

---

## Implementation Notes for OpenDesign

1. **Component Library First**: Build the Phase Card, Player Card, Stat Bar, Shop Item Card, and Synergy Badge as reusable components before screen assembly.
2. **Data-Driven Rendering**: All game data (players, phases, synergies, formations) is defined in `game-engine.js`. Screens render from `G` (game state) object.
3. **Real-Time Updates**: Squad Builder synergy preview, Match live score, and Phase Selection combo chain preview must update reactively on state changes (no full re-render).
4. **Animation Budget**: Keep all animations under 200ms per `DESIGN.md`. Score cascade is the exception (0.8s, but skippable).
5. **Mobile Breakpoints**: 920px (switch to single column), 600px (compact cards). Touch targets minimum 44×44px per WCAG.
6. **Accessibility**: All icons need aria-labels. Color must not be the only indicator (use text/icons alongside). Focus order must follow visual layout.
7. **Performance**: Player grid should use virtual scrolling if >20 cards. Synergy computation should be debounced (50ms) during rapid player selection.
