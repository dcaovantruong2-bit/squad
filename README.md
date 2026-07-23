# Squad ⚽

**Football card roguelike — draft a squad, pick phases from a dealt hand, stack synergies, and survive escalating opponent tactics.**

Inspired by Balatro and Slay the Spire.

---

## Quick Start

```bash
cd ~/games/squad
.venv/bin/python3 main.py    # Terminal version
```

Or play in the browser: **http://100.82.27.85:8765**

Click **DRAFT MODE** to build your squad, or **QUICK START** for an auto-filled team.

---

## Game Flow

### 1. Draft (New!)
Build your squad position-by-position from the full 55-player pool:
- **GK**: Pick 1 from all 5 goalkeepers
- **DEF**: Pick 4 defenders — **any mix of CBs & FBs** (2+2? 3+1? 4 CBs? Your call)
- **MID**: Pick 3 from all 17 midfielders (CM/CDM/CAM)
- **ATK**: Pick 2 from all 18 attackers (ST/LW/RW)

Every player in the pool is shown. Pick the ones that fit your strategy.

### 2. Formation
6 formations with position bonuses/penalties and global multipliers:

| Formation | Global | Identity |
|-----------|--------|----------|
| 4-4-2 | ×1.00 | Balanced |
| 4-3-3 | ×1.03 | Wingers thrive, defence exposed |
| 5-3-2 | ×0.95 | Defence wins, no width |
| 3-4-3 | ×1.05 | All-out attack, risky at the back |
| 4-2-3-1 | ×1.02 | CAM-focused possession |
| 4-5-1 | ×0.98 | Counter-attacking, lone striker |

### 3. Phase Selection — Hand-Based Dealing
**5 of 8 phases dealt per round.** You pick 3. You don't always get what you want — adapt to the hand you're dealt.

8 phases across 5 tags:

| Tag | Phases |
|-----|--------|
| 🛡️ Defensive | Goal Kick, Defensive Block |
| 🔄 Possession | Build-Up, Tiki-Taka |
| ⚡ Transition | Direct Play, Counter |
| 🎯 Attacking | Wide Attack |
| ✨ Specialist | Set Piece |

**Combo chains reward/punish your phase sequencing:**

| Good Sequence | Bonus | Bad Sequence | Penalty |
|--------------|-------|-------------|---------|
| Defensive→Transition | ×1.5 | Attacking→Attacking | ×0.8 — Overcommitted! |
| Possession→Attacking | ×1.3 | Transition→Defensive | ×0.85 — Panic clearance! |
| Transition→Transition | +35 chips | Possession→Defensive | −15 chips — Killed tempo! |
| Specialist→Any | +30 chips | Transition→Possession | ×0.85 — Lost momentum! |

**No matching chain?** Mild ×0.95 penalty. Plan your phase order carefully.

### 4. Match — 3 Phases per Round, Best of 3 Rounds
Each phase you field players into slots. Scoring uses Balatro-style formula:

```
(chips + synergy_chips) × (1 + add_mult) × x_mult × formation × momentum × phase_mult
```

**Out-of-position penalties** apply based on role adjacency (natural ×1.0, adjacent ×0.85, different ×0.70). Traits and high stats reduce the penalty.

---

## Energy System (Replaces Fatigue)

Players have 3 energy per match. Each phase use costs 1 energy:

| State | Energy | Multiplier | Effect |
|-------|--------|-----------|--------|
| Fresh | 3 | ×1.0 | Full power |
| Tired | 2 | ×0.85 | Slight penalty |
| Exhausted | 1 | ×0.65 | Big penalty + **25% injury risk** |
| Injured | 0 | ×0.0 | Cannot play rest of match |

- **Forced rotation**: can't spam your best player every phase
- **Bench recovery**: unused players gain 1 energy between rounds
- **Journeyman** trait: once-per-match full energy reset

---

## Opponent Tactical System (Boss Blinds)

Each campaign opponent has tactical styles that counter specific strategies:

| Match | Opponent | Tactics | Effect |
|-------|----------|---------|--------|
| 1 | Wolves FC | Low Block | Transition & Attacking phases ×0.75 |
| 2 | Inter Your-Nan | Possession Heavy | Transition phases ×0.7 |
| 3 | Borussia Mönchen-flapjack | High Press + Counter Attack | Possession/Defensive ×0.7 + Attacking ×0.7 |
| 4 | Man City Oilers | Man Mark + Time Waste | Best player ×0.6 + Phase 3 halved |
| 5 | Galácticos FC | Dirty Team + Man Mark + High Press | +15% injury + man-mark + press |

Scout the opponent, then adapt your phase picks and player placement.

---

## Momentum — Earned, Not Given

Momentum starts at ×1.0. After each phase, if your score ≥ 15% of the round target → **+0.15 momentum** for the next phase. Consecutive hits stack to ×1.3 max. A miss resets to ×1.0.

---

## Scoring

```
Phase Score = Σ(player_chips × energy × OOP × persistent_buffs)
            + synergy_chips + carryover
            × (1 + add_mult)
            × x_mult
            × formation_mult
            × momentum
            × phase_mult (combo chains + opponent tactics)
```

- **Chips**: position-weighted stat formulas (ST: ATK×3+PAC×2+SPC×1)
- **Synergies**: 18 phase-level + 12 persistent squad synergies
- **Combo chains**: tag sequence bonuses and penalties
- **Opponent tactics**: multiplicative nerfs on specific phase types

---

## Campaign

5 escalating matches. Win 2 of 3 rounds to advance. Lose a match = game over.

| Match | Opponent | Targets (R1/R2/R3) | Tactics |
|-------|----------|-------------------|---------|
| 1 | Wolves FC | 2000 / 3500 / 5000 | 1 |
| 2 | Inter Your-Nan | 3000 / 5000 / 7000 | 1 |
| 3 | Borussia Mönchen-flapjack | 4000 / 6500 / 9000 | 2 |
| 4 | Man City Oilers | 5000 / 8000 / 11500 | 2 |
| 5 | Galácticos FC | 6500 / 10000 / 14500 | 3 |

---

## Shop (Between Rounds)

Spend morale earned from round wins:

| Item | Cost | Effect |
|------|------|--------|
| Energy Drink | 2 | Restore one player's energy |
| Morale Boost | 1 | +5 morale |
| Scout Report | 2 | See all 8 phases next round |
| Set Piece Drill | 4 | +40 chips next round |
| Tactical Shift | 5 | +5 add_mult next round |
| Formation Tweak | 3 | +0.05 formation mult |
| Super Sub | 2 | Fresh player gets ×1.3 |
| Momentum Injector | 4 | Next phase ×1.5 momentum |

---

## Running Tests

```bash
cd ~/games/squad
source .venv/bin/activate
python3 -m pytest tests/ -v
```

312 tests covering: scoring formulas, synergy detection, energy system, opponent tactics, drafting, momentum, and full end-to-end integration.

---

## Architecture

| Layer | Files | Purpose |
|-------|-------|---------|
| **Python backend** | `src/` — cards, scoring, energy, opponents, draft, phases, match | Core game logic, data loading, tests |
| **JS frontend** | `web/game-engine.js` + `web/game-data.js` | Browser game logic, all data (players, synergies, formations, opponents) |
| **SPA shell** | `web/game.html` | Screen navigation shell, save/load, draft handoff |
| **Screens** | `web/screens/` (title, draft, squad, formation, phases, match, etc.) | Individual game screens |
| **Data** | `data/players.toml` + `data/synergies.toml` | Canonical player and synergy definitions |
| **Tests** | `tests/` (10 files, pytest) | Unit + integration tests |

Both Python and JS engines share the same game data and scoring logic.
