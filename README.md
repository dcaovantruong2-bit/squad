# Squad ⚽

**Football card roguelike — build a squad, pick your phases, stack synergies like Balatro.**

---

## How to Play

```bash
cd ~/games/squad
.venv/bin/python3 main.py
```

Or play in the browser: **http://100.82.27.85:8081**

---

## Game Flow

### 1. Squad Builder
Pick **11+ players** from 36 within a **360 coin budget**.
- Cost = ATK+PAC+PAS+DEF+SPC (stat sum)
- Minimums: 1 GK · 3+ Defenders · 3+ Midfielders · 2+ Attackers
- Build creatively — 5 CBs and 3 CMs? Go for it.

### 2. Formation Pick
6 formations with different **position bonuses/penalties** and **global multipliers**:
| Formation | Global Mult | Identity |
|-----------|-------------|----------|
| **4-4-2** | ×1.00 | Balanced |
| **4-3-3** | ×1.05 | Wingers thrive |
| **5-3-2** | ×0.95 | Defence wins |
| **3-4-3** | ×1.08 | All-out attack |
| **4-2-3-1** | ×1.02 | CAM-focused |
| **4-5-1** | ×0.98 | Counter-attack |

### 3. Phase Selection (🃏 Pick 3 of 6)
Dealt **6 phase cards** — pick **3 to play** in any order.
- Order matters for carryover synergies (e.g. Double Pivot)
- Each card shows: slots required, best-fit player, and **⚡ potential synergies** that would fire
- **All 18 phase synergies** available every round — your squad determines what fires, not RNG

### 4. Match — 3 Phases × 3 Rounds
Each phase you field players into stat-based slots:
```
→CB [DEF≥7] → any player with DEF≥7 scores as CB
→ST [ATK≥7, physical] → ATK≥7 AND physical trait required
```
Targets: progressive difficulty (350→1200). Beat 2 of 3 rounds to win the match.

---

## Scoring (Balatro-Style)

```
(base_chips + formation_bonus + synergy_add) × synergy_mult × fatigue × formation_mult
```

Each phase result shows:
```
Player (Pos)  62 base +25 bonus = 87 chips  ×1.5 mult  ×0.7 fatigue  = 91 pts
Player (Pos)  44 base +25 bonus = 69 chips  ×1.3 mult  ×1.0 fatigue  = 90 pts
────────────────────────────────────────────────────────────────────────
Subtotal:                                                             181 pts
× Formation (4-3-3):                                            ×1.05
════════════════════════════════════════════════════════════════════════
PHASE TOTAL:                                                          190 pts
```

### Synergy Math
Each synergy is like a Balatro joker:
- **+chips** = add to base chips (like Balatro chip bonuses)
- **×mult** = multiply everything (like Balatro mult jokers)
- Stack multiplicatively across persistent + phase synergies

---

## Key Features

- **Fatigue carries over**: 50% recovery between rounds (not full reset)
- **Synergy filter**: Only shows synergies your squad can actually trigger, with involved players listed
- **13 phases** (up from 11): Goal Kick, Build-Up, Wing Attack, Long Ball, Defensive Block, Tiki-Taka, Counter-Attack, Set Piece, Flair Moment, Second Ball, High Press, Through Ball, Wingback Push
- **223 tests** covering everything

---

## Campaign

5 matches, best-of-3 rounds each:
| Match | Round Targets | Difficulty |
|-------|--------------|------------|
| Group Stage | 350 / 450 / 600 | Easy |
| Round of 16 | 450 / 580 / 750 | Moderate |
| Quarter Final | 550 / 700 / 880 | Challenging |
| Semi Final | 700 / 850 / 1050 | Elite |
| THE FINAL | 850 / 1000 / 1200 | Final Boss |

---

## Running Tests

```bash
cd ~/games/squad
.venv/bin/python3 -m pytest tests/ -v
```

223 tests covering phases, fatigue, stat eligibility, scoring formulas, all 18 phase synergies, all 12 persistent synergies, full match end-to-end.
