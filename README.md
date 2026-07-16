# Squad ⚽

**Football card roguelike — build a squad, pick your phases, stack synergies like Balatro.**

---

## How to Play

```bash
cd ~/games/squad
.venv/bin/python3 main.py
```

Or play in the browser: **http://100.82.27.85:8081/game.html**

---

## Game Flow

### 1. Squad Builder
Pick **11+ players** from 36 within a **360 coin budget**.
- Cost = ATK+PAC+PAS+DEF+SPC (stat sum)
- Minimums: 1 GK · 3+ Defenders · 3+ Midfielders · 2+ Attackers
- Every player has **traits** (pacey, clinical, technical, physical, playmaker, etc.) that affect OOP penalties and persistent synergies
- **Persistent synergies** trigger based on your squad's trait composition — Iron Wall, Leadership Council, Tiki-Taka, etc.

### 2. Formation Pick
6 formations with **position bonuses/penalties** and **global multipliers**:

| Formation | Global Mult | Identity |
|-----------|-------------|----------|
| **4-4-2** | ×1.00 | Balanced |
| **4-3-3** | ×1.05 | Wingers thrive |
| **5-3-2** | ×0.95 | Defence wins |
| **3-4-3** | ×1.08 | All-out attack |
| **4-2-3-1** | ×1.02 | CAM-focused |
| **4-5-1** | ×0.98 | Counter-attack |

### 3. Phase Selection (🃏 Pick 3 from 13)
All **13 tactical focuses** are available every round — pick **3 in order**. Order matters for **combo chains** (sequences of phase tags unlock bonus effects).

**Categories:**

| Tag | Phases | Count |
|-----|--------|-------|
| 🛡️ Defensive | Goal Kick, Defensive Block, Regroup, Hold Shape | 4 |
| 🔄 Possession | Build-Up, Tiki-Taka, Controlled Tempo | 3 |
| ⚡ Transition | Direct Play, Counter Attack | 2 |
| 🎯 Attacking | Wide Overload, Target Man, Late Run | 3 |
| ✨ Specialist | Set Piece | 1 |

Each phase has **2-4 flexible slots** that accept multiple position options.

**Combo Chains** trigger when you sequence phases from specific categories:
- 🛡️ Defensive → ⚡ Transition: **×1.5 mult** (absorb pressure, hit on break)
- 🔄 Possession → 🎯 Attacking: **×1.3 mult** (patient build to incision)
- 🔄 Possession → 🔄 Possession: **+25 chips** (keep the ball)
- ⚡ Transition → ⚡ Transition: **+35 chips** (rapid succession)
- 🛡️ Defensive → 🛡️ Defensive: **fatigue recovery** (rest while defending)
- ✨ Specialist → any: **carryover +30 chips** (set piece leads to chance)
- 🎯 Attacking → 🛡️ Defensive: **opponent -10%** (suck them in, hold firm)
- 🔄 Possession → ⚡ Transition: **×1.2 mult** (unexpected speed shift)

### 4. Match — 3 Phases × 3 Rounds
Each phase you field players into **flexible slots**. Any player can fill any slot (except GK → GK only) but **OOP penalties** apply based on role adjacency:

| Gap | Base | Max with traits |
|-----|------|-----------------|
| **Natural** (CB in DEF slot) | ×1.0 | ×1.0 |
| **Adjacent** (FB at winger, CDM at CM) | ×0.85 | ×0.95 |
| **Different** (CB at striker, CM at right-back) | ×0.70 | ×0.95 |
| **Blocked** (GK anywhere outfield) | ×0.0 | ×0.0 |

Each matching **trait** reduces the penalty by +0.10. A key stat ≥9 for that slot role adds +0.05.

**Example:** Your CB with `pacey` trait and PAC 10 in a winger slot:
- Different role base: ×0.70
- `pacey` fits WNG slots: +0.10
- PAC ≥9 (key stat for WNG): +0.05
- **Final: ×0.85** — that's a viable creative pick.

---

## Scoring (Balatro-Style)

```
(player_chips + synergy_chips + carryover_chips + shop_chips)
  × (1 + add_mult + shop_add_mult)
  × x_mult × formation × momentum × phase_mult
```

Each phase, **chips × add_mult × x_mult** = total. Synergies trigger based on the fielded players and stack multiplicatively. **Momentum grows** across phases (×1.0 → ×1.2 → ×1.5).

### Auto-Win
If your running round score **exceeds the target** after any phase, you **immediately win the round** — remaining phases are skipped. You earn **morale** (spent in the shop) based on how decisively you won.

---

## Shop (Between Rounds)

Spend **morale** earned from round wins:

| Item | Cost | Effect |
|------|------|--------|
| Scout Report | 2 | See all 8 phase cards next round |
| Inspired Sub | 2 | Restore one player's fatigue |
| Formation Tweak | 3 | Swap to a different formation |
| Set Piece Drill | 4 | Next round: +40 chips |
| Tactical Shift | 5 | Next round: +5 add_mult |
| Veteran's Wisdom | 6 | Random trait bonus |

---

## Campaign

5 matches, best-of-3 rounds each. Beat 2 rounds to win the match:

| Match | Targets | Difficulty |
|-------|---------|------------|
| Group Stage | 200K / 350K / 500K | Easy |
| Round of 16 | 350K / 500K / 700K | Moderate |
| Quarter Final | 500K / 700K / 900K | Challenging |
| Semi Final | 700K / 900K / 1.1M | Elite |
| THE FINAL | 900K / 1.1M / 1.5M | Final Boss |

Lose a match = game over. Win 3+ to win the campaign.

---

## Key Features

- **Balatro-style scoring**: chips × add_mult × x_mult with stacking synergies
- **OOP penalty system**: any player anywhere, with role-adjacency, trait, and stat modifiers
- **Combo chains**: phase sequencing unlocks bonus effects
- **13 tactical focuses** across 5 categories (2-4 players per phase)
- **Fatigue**: decays ×0.85 per phase use, partial recovery between rounds
- **Opponent adjustments**: random buff/nerf per round encouraging adaptive phase picks
- **Persistent squad synergies**: Iron Wall, Tiki-Taka, Leadership Council, and more
- **Morale economy**: earn from wins, spend in shop between rounds
- **Momentum**: ×1.0 → ×1.2 → ×1.5 across phases
- **Auto-win**: beat the target mid-round to skip remaining phases

---

## Running Tests

```bash
cd ~/games/squad
.venv/bin/python3 -m pytest tests/ -v
```

221 tests covering phases, OOP penalties, fatigue, scoring formulas, all synergies, full match end-to-end.

---

## Architecture

- **Python terminal game**: `main.py` + `src/` (phases, scoring, shop, match)
- **Web UI**: Three-file split:
  - `web/game-engine.js` — Pure game data + logic (PLAYERS, FORMATIONS, SYNERGIES, scoring, OOP)
  - `web/game-ui.js` — Rendering, state management, event handlers, all 9 screens
  - `web/game.html` — HTML layout + `<script>` loaders
  - `web/game.css` — Dark neon design system
- Both share the same game data (`data/players.toml`, `data/synergies.toml`) and logic
- Tests in `tests/` use pytest
