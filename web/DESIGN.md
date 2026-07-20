# Squad — Design System & Screen Inventory

> **Football card roguelike.** Build a squad, pick formations, stack synergies (Balatro-style), win 5 matches.
>
> This document is the canonical source of truth for all screens, states, data models, and interaction rules.
>
> ## Architecture Overview
> **SPA architecture**: `game.html` is the shell (navigation + screen router), `game-engine.js` is the engine (state, scoring, shop, campaign), and each screen lives as a standalone HTML partial under `web/screens/`. The shell loads screens into an iframe with `postMessage` communication. `game-ui.js` is a **legacy file** — no longer used by the SPA. The match screen is routed as `match-screen-fixed.html` (replaces the older `match.html`).

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Genre | Football card roguelike (Slay the Spire × Balatro × CM01) |
| Platform | Web (HTML/CSS/JS), PWA, iOS native |
| Core loop | Build squad → Pick formation → Select 3 phases → Place players → Score → Shop → Repeat |
| Campaign | 5 escalating matches, win 2 of 3 rounds each |
| Scoring | `(chips) × (1 + add_mult) × x_mult × formation × momentum` |

---

## 2. Screens (10 Total + Screen Hub)

Each screen is a self-contained HTML file loaded by the SPA shell (`game.html`).

### Screen Hub (`index`)
- **Purpose**: Developer index listing all screens with links.
- **File**: `/web/screens/index.html`

### 2.1 Title Screen (`title-screen`)
- **Purpose**: Entry point. Start campaign or quick start.
- **File**: `web/screens/title-screen.html`
- **States**: Initial load
- **Content**: Game logo (SQUAD), tagline, Start Campaign button, Quick Start button, How to Play link

### 2.2 Squad Builder (`squad-builder-screen`)
- **Purpose**: Draft 11–12 players within 360 coin budget.
- **File**: `web/screens/squad-builder.html`
- **States**: Empty → Selecting → Complete (valid) → Invalid (budget/requirements not met)
- **Content**:
  - Budget bar (0–360 coins)
  - Position filter tabs (GK, DEF, MID, ATT)
  - Player card grid (scrollable)
  - Your Squad section (selected players as pills)
  - Role requirement strip (min GK/DEF/MID/ATT)
  - Formation fit preview
- **Data**: 36 players, each with: name, position, 5 stats (ATK/PAC/PAS/DEF/SPC 0–10), traits, cost (sum of stats)

### 2.3 Formation Select (`formation-select-screen`)
- **Purpose**: Choose tactical shape.
- **File**: `web/screens/formation-select.html`
- **States**: Browsing → Selected (can confirm)
- **Content**:
  - Formation carousel (6 formations)
  - Formation diagram (pitch view with positions)
  - Fit score / recommendation
  - Position bonuses/penalties
  - Global multiplier display
- **Formations**: 4-4-2 (×1.00), 4-3-3 (×1.05), 5-3-2 (×0.95), 3-4-3 (×1.08), 4-2-3-1 (×1.02), 4-5-1 (×0.98)

### 2.4 Phase Selection (`phase-select-screen`)
- **Purpose**: Pick 3 phases from dealt hand, in order.
- **File**: `web/screens/phase-select.html`
- **States**: Dealing cards → Selecting → Confirming → Transition
- **Content**:
  - 8 phase cards dealt (pick 3)
  - Phase order matters (combo chains)
  - Available synergies preview
  - Round info (match #, round #, target score)
  - Picked phases display area
- **Phase categories (8 total)**: 🛡️ Defensive (2), 🔄 Possession (2), ⚡ Transition (2), 🎯 Attacking (1), ✨ Specialist (1)

### 2.5 Match — Phase Placement (`match-screen`)
- **Purpose**: Place players into phase slots for scoring.
- **File**: `web/screens/match-screen-fixed.html`
- **States**: Slot selected → Player selected → Slot filled → All filled → Submitting
- **Content**:
  - Match header (VS display, round score, target)
  - Progress (round 1–3, phase 1–3)
  - Active phase info bar
  - Live phase score (updates as players placed)
  - Phase slot cards (pitch-zoned: ATTACK / MIDFIELD / DEFENSE)
  - Eligible player panel (tap slot to see)
  - Synergy preview panel
  - Auto-fill button, Submit button
  - Fatigue indicators

### 2.6 Phase Result (`phase-result-screen`)
- **Purpose**: Show scoring breakdown for completed phase.
- **File**: `web/screens/phase-result.html`
- **States**: Score reveal animation → Breakdown table → Continue
- **Content**:
  - Hero score display (large, animated)
  - Target comparison
  - Player contributions table (PLAYER | POS | BASE CHIPS | +SYNERGY | ×MULT | ×FATIGUE | = SUBTOTAL)
  - Synergies fired accordion
  - Auto-win notification (if score exceeds target)

### 2.7 Round Result (`round-result-screen`)
- **Purpose**: Show round outcome and transition.
- **File**: `web/screens/round-result.html`
- **States**: Win → Loss → Advance to next round or shop
- **Content**:
  - Verdict (Won / Lost / Draw)
  - Your score vs target
  - Round progress (which rounds won/lost)
  - Phase performance (bar chart or visual)
  - Fatigue summary
  - Continue button

### 2.8 Shop (`shop-screen`)
- **Purpose**: Spend morale between rounds on upgrades.
- **File**: `web/screens/shop-screen.html`
- **States**: Items displayed → Purchased item → All sold → Skip
- **Content**:
  - Morale balance display
  - Shop items (boosts, fatigue recovery, chip/mult bonuses)
  - Item cards with rarity (common/uncommon/rare)
  - Purchase confirmation
  - Skip button

### 2.9 Campaign Complete (`campaign-complete-screen`)
- **Purpose**: End-of-campaign summary.
- **File**: `web/screens/campaign-complete.html`
- **States**: Won → Lost → Play again
- **Content**:
  - Title (Campaign Complete / Game Over)
  - Match results summary (all 5 matches)
  - Play Again button
  - Stats recap (optional)

---

## 3. Data Model

This is the canonical data model. All screen designs must handle these fields.

### Player
```typescript
interface Player {
  id: string;             // unique key
  name: string;           // display name
  position: Position;     // GK | CB | FB | CDM | CM | LW | RW | ST
  atk: number;            // 0–10
  pac: number;            // 0–10
  pas: number;            // 0–10
  def: number;            // 0–10
  spc: number;            // 0–10
  traits: Trait[];        // e.g. "pacey", "clinical", "physical", "playmaker", "technical"
  cost: number;           // sum of all stats (5–50)
}
```

### Formation
```typescript
interface Formation {
  id: string;             // "4-4-2", "4-3-3", etc.
  name: string;
  globalMult: number;     // ×1.00, ×1.05, etc.
  positions: Position[];  // 11 position slots
  bonuses: Record<string, number>;  // position → stat bonus
  label: string;          // "Balanced", "Wingers thrive", etc.
}
```

### Phase
```typescript
interface Phase {
  id: string;
  name: string;           // "Goal Kick", "Build-Up", etc.
  category: PhaseCategory;  // "defensive" | "possession" | "transition" | "attacking" | "specialist"
  icon: string;           // emoji or SVG
  slots: SlotDef[];       // 2–4 flexible role slots
  description: string;
  tags: string[];
}
```

### Slot
```typescript
interface SlotDef {
  id: string;             // "att-1", "mid-1", "def-1"
  zone: Zone;             // "attack" | "midfield" | "defense"
  label: string;          // "Target Forward", "Deep Playmaker"
  acceptedPositions: Position[];  // which positions can fill this
  keyStat: StatKey;       // which stat matters most (ATK/PAC/PAS/DEF/SPC)
}
```

### Synergy
```typescript
interface Synergy {
  id: string;
  name: string;           // "Tiki-Taka", "Iron Wall", "Double Pivot"
  condition: string;      // human-readable trigger description
  type: "chips" | "add_mult" | "x_mult";
  value: number;
  icon: string;
}
```

### Scoring Formula
```
Total = ( chips + synergy_chips + carryover )
      × ( 1 + add_mult + shop_add_mult )
      × x_mult × formation_mult × momentum × fatigue_mult
```
Where:
- `chips` = sum of key stats of placed players
- `synergy_chips` = chip bonuses from triggered synergies
- `carryover` = chips carried from previous phase (via combo chains)
- `add_mult` = additive multiplier bonuses (synergies, shop)
- `x_mult` = multiplicative multiplier bonuses
- `formation_mult` = formation's global multiplier (0.95–1.08)
- `momentum` = grows across phases (×1.0 → ×1.2 → ×1.5)
- `fatigue_mult` = per-player usage penalty (fresh=1.0, used=×0.7)

### Fatigue
```typescript
interface FatigueState {
  [playerId: string]: number;  // 0.0–1.0 multiplier
}
```
- Fresh = 1.0 (full stats)
- Used once = ×0.7 (multiplicative — each subsequent use multiplies by 0.7)
- Shop items can restore fatigue (Energy Drink: full reset)
- Rest between rounds: recovers 50% of lost fatigue (`recoverFatigue(0.5)`)

### Morale (Shop Currency)
Morale is earned through in-game performance and spent in the shop:
- **Phase contributes**: +1 if phase score ≥ 70% of round target (`target × 0.7`)
- **Round win**: +3 for winning the round
- **Beat target by 50%**: +2 if round score ≥ target × 1.5
- **Match win**: +5 for winning the match (2 of 3 rounds)
- **Clean sweep**: +3 if all 3 rounds won

### Shop Items (10 total)
The shop offers 10 items matching the Python backend:
| Item | Cost | Effect |
|------|------|--------|
| Energy Drink | 2 | Restore one player's fatigue to 100% |
| Tactical Upgrade | 3 | +1 to a chosen stat on one player |
| Set Piece Drill | 4 | Next round: all phases get +40 chips |
| Super Sub | 2 | Next round: fresh player gets ×1.3 |
| Tactical Shift | 5 | Next round: +5 add_mult on all phases |
| Formation Tweak | 3 | +0.05 formation mult for next match |
| Momentum Injector | 4 | Next phase starts at ×1.5 momentum |
| Scout Report | 2 | See all 8 phases this round |
| Double Training Session | 4 | This round fatigue penalty ×0.8 instead of ×0.7 |
| Morale Boost | 1 | +5 morale |

### Campaign Targets (5 matches)
| Match | Round 1 | Round 2 | Round 3 |
|-------|---------|---------|---------|
| 1 — Group Stage | 400 | 650 | 900 |
| 2 — Round of 16 | 450 | 700 | 950 |
| 3 — Quarter Final | 550 | 800 | 1100 |
| 4 — Semi Final | 650 | 950 | 1300 |
| 5 — THE FINAL | 800 | 1150 | 1500 |

### Campaign Structure
- **5 matches** to win the campaign
- Each match: win **2 of 3 rounds** to advance
- Between rounds: shop phase for purchases
- Between matches: shop phase with full fatigue recovery

---

## 4. Interaction Rules

| Interaction | Behaviour |
|-------------|-----------|
| Hover on card | Visual highlight (border colour change, slight lift) |
| Click to select | Toggle selected state, play micro-animation |
| Click to confirm | Transition to next screen with feedback |
| Invalid state | Button disabled, error message visible |
| Auto-fill | Instant, no confirmation needed |
| Score reveal | Animated number count-up, synergy badges appear staggered |
| Phase transition | Brief loading state, then result screen |
| Shop purchase | Deduct morale, apply effect, disable purchased item |

---

## 5. Visual Design (TO BE DECIDED — Open Design)

> The following sections are intentionally blank. You will define them using Open Design.
> For each screen, Open Design will propose a cohesive visual direction.
> Choose the one you like and fill in the tokens below.

### Colour Palette
| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | | Page background |
| `--surface` | | Card/panel backgrounds |
| `--fg` | | Primary text |
| `--accent` | | Primary accent, CTAs |
| `--gold` | | Scores, currency |
| `--danger` | | Errors, penalties |
| `--success` | | Wins, synergies |
| `--border` | | Borders |
| *(add more as needed)* | | |

### Typography
| Token | Value |
|-------|-------|
| Display font | (pick one) |
| Body font | (pick one) |
| Mono font | (pick one) |
| Base size | (pick one) |
| Scale | (pick one) |

### Effects
| Effect | CSS |
|--------|-----|
| Card glow | |
| Score glow | |
| Transition | |
| Animation | |

---

## 6. Design Process (Open Design Workflow)

### Per-Screen Workflow
1. Start the OD daemon (`od`)
2. Open `http://127.0.0.1:7456` in browser
3. For each screen, paste the following prompt into OD chat:

```
Design the [SCREEN NAME] for Squad, a football card roguelike.
Read DESIGN.md for the game rules and data model.
Create a self-contained HTML artifact with inline CSS/JS.
Target: modern browser, responsive (1920px → 600px).
Use the same design tokens across all screens for consistency.
```

4. When you're happy with a screen's design, export it as an artifact.
5. Repeat for the next screen.

### Screen Order (recommended)
1. Title Screen
2. Squad Builder
3. Formation Select
4. Phase Selection
5. Match — Phase Placement
6. Phase Result
7. Round Result
8. Shop
9. Campaign Complete

---

## 7. Prohibited Patterns
- No AI-generated placeholder images (use real player data)
- No gradients on surfaces (glow effects OK)
- No rounded corners unless design direction specifies otherwise
- No white backgrounds (dark theme assumed)
- No animations longer than 300ms
- No text smaller than 10px
- No modal dialogues unless explicitly required
