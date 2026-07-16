1|# Squad — UI Layout Plan  [HISTORICAL]
2|>
3|> ⚠️ **This document describes the terminal UI redesign plan and has been superseded.**
4|> See **`docs/SCREEN_ARCHITECTURE.md`** for the current web UI design specification.
5|> This file is retained for reference only — content may be outdated.
6|>

> Game design + UI engineering plan for every screen in the game.
> Goal: clear visual hierarchy, reduced cognitive load, meaningful information at each decision point.

---

## Current Screen Inventory

| # | Screen | Where | Player's Decision |
|---|--------|-------|-------------------|
| 1 | Title | `main.py:660` | "Start the game" |
| 2 | Squad Builder | `squad_builder.py:68` | Pick players within budget |
| 3 | Formation Select | `main.py:393` | Choose tactical formation |
| 4 | Persistent Synergies | `main.py:676` | (Informational — acknowledge) |
| 5 | Match Intro | `main.py:694` | (Informational — prepare) |
| 6 | Phase Selection | `main.py:697` | Pick 3 of 6 phase cards in order |
| 7 | Phase Header + Placement | `main.py:311` | Fill 2-3 slots with players |
| 8 | Live Score Preview | `main.py:357` | (Informational — see running score) |
| 9 | Phase Result | `main.py:138` | (Informational — Balatro-style breakdown) |
| 10 | Round Result | `main.py:186` | (Informational — won/lost) |
| 11 | Match Result | `main.py:598` | (Informational — advance/eliminated) |
| 12 | Campaign Champion | `main.py:751` | (Celebration) |

---

## Design Principles

1. **One decision per screen** — don't mix "pick a player" with "see your whole squad"
2. **Progressive disclosure** — show summary first, details on demand
3. **Persistent context bar** — round/score/target/fatigue always visible at top
4. **Visual zones** — divide the screen into labeled regions (header, field, bench, info)
5. **Color = meaning** — green=good/fresh, yellow=warning/fatigued, red=danger/exhausted, cyan=info, yellow=synergy
6. **Whitespace is free** — don't cram; let the eye rest between zones

---

## Screen-by-Screen Layouts

### 1. Title Screen
**Current:** Box-drawn banner, 2 lines of flavor text, press Enter.
**Keep it.** It's fine. Maybe add a subtle "Season X" or version tag.

```
  ╔═══════════════════════════════════════════════════╗
  ║              ⚽  S Q U A D  ⚽                   ║
  ║     Football Card Roguelike — Phase System       ║
  ╚═══════════════════════════════════════════════════╝

  A campaign of 5 matches. Win a match = win 2 of 3 rounds.
  Lose any match — tournament over. Win all 5 — champion!

  Press Enter to start...
```

**Verdict:** ✅ No changes needed.

---

### 2. Squad Builder ⭐ (HIGH PRIORITY — most complex screen)
**Current problems:**
- All 50+ players shown as a flat numbered list — overwhelming
- Stats dumped inline make it hard to compare
- Role-group status is crammed at the bottom
- No visual grouping between "your bench" and "the market"
- Synergy potential shown as a bare number

**Proposed layout — 3 zones:**

```
┌─────────────────────────────────────────────────────────┐
│  ⚽ BUILD YOUR SQUAD                                    │
│  Budget: ████████████░░░░░░░░  240/360  (120 left)     │
│  Squad:  8 players  │  Min: 10 required                 │
├─────────────────────────────────────────────────────────┤
│  ROLE REQUIREMENTS                                      │
│  ✅ GK        1/1   ✅ Defenders  4/3   ⬜ Mid  2/3   ⬜ Att  1/2 │
├─────────────────────────────────────────────────────────┤
│  YOUR SQUAD (8 players, 240 coins)                      │
│  ┌─────────────────────────────────────────────────┐    │
│  │ [0] Mbappé       ST  35  ⚡Counter-Attack       │    │
│  │ [1] De Bruyne    CM  40  ⚡Tiki-Taka, Engine     │    │
│  │ [2] Van Dijk     CB  30  ⚡Clean Sheet           │    │
│  │ ...                                              │    │
│  └─────────────────────────────────────────────────┘    │
│  Type 'drop <#>' to remove  │  'done' to finalize       │
├─────────────────────────────────────────────────────────┤
│  AVAILABLE — sorted by position                         │
│                                                         │
│  🧤 GK                                                  │
│    [3] Alisson      25   ATK:3 PAC:4 PAS:5 DEF:9 SPC:7 │
│    [4] Ter Stegen   20   ATK:2 PAC:3 PAS:8 DEF:8 SPC:6 │
│                                                         │
│  🛡️ CB                                                  │
│    [5] Rudiger      22   ATK:4 PAC:7 PAS:4 DEF:8 SPC:3 │
│    ...                                                  │
│                                                         │
│  ⚡ = synergy potential (how many synergies this        │
│       player could unlock with your current squad)      │
└─────────────────────────────────────────────────────────┘
  > _
```

**Key changes:**
- **Role requirements bar** moves to top — always visible, at-a-glance progress
- **Your squad** shown before available players (what you HAVE > what you CAN get)
- **Synergy tags** shown per selected player (what they unlock)
- **Available players** grouped by position with clean stat line
- **Budget bar** is visual (█░) not just numeric
- **Separation** between "your squad" and "the market" with clear dividers

---

### 3. Formation Select
**Current:** Numbered list with fit scores and reasons. Decent.
**Proposed:** Minor tweaks — show formation diagram (ASCII art) for the top recommendation.

```
  ╔═══════════════════════════════════════════════════╗
  ║         Choose Your Formation                    ║
  ╚═══════════════════════════════════════════════════╝

  ⭐ RECOMMENDED: 4-3-3 (fit score: 85)
  ┌───────────────────────────────────┐
  │           ST                      │
  │     LW          RW                │
  │        CM  CM  CM                 │
  │   FB              FB              │
  │        CB      CB                 │
  │              GK                   │
  └───────────────────────────────────┘
  Your squad: 3 CMs PAS8+ → Tiki-Taka, Wingers → Cut Inside

  [0] 4-4-2   CB:+2 FB:+2   ⭐ (fit: 85)
      Balanced width, strong midfield line
      📊 4 STs, Physical ST → Big Man

  [1] 4-3-3   CM:+2 LW:+1 RW:+1
      Attacking trio, midfield control
      📊 3 CMs PAS8+ → Tiki-Taka

  ...

  Pick formation # (default 0): _
```

**Verdict:** Medium priority. ASCII pitch diagram is a nice touch but not critical.

---

### 4. Match Intro
**Current:** Campaign bracket + opponent name + targets. Good.
**Proposed:** Add opponent "scouting report" — a 1-line flavor description.

```
  Campaign: [GS] ✅ → [R16] ⚔️ → [QF] ⬜ → [SF] ⬜ → [FN] ⬜

  ╔═══════════════════════════════════════════════════╗
  ║          GROUP STAGE — Match 1/5                 ║
  ║          Tier: Regional Qualifier                ║
  ╚═══════════════════════════════════════════════════╝

  🆚 FC Rivals
  "Physical side, strong in the air. Exploit their slow CBs."

  Targets: R1=500  R2=650  R3=850
  Formation: 4-3-3 (×1.10 mult)

  Press Enter to kick off...
```

**Verdict:** Low priority. Flavor text is nice-to-have.

---

### 5. Round Start — Synergy Reveal
**Current:** Just a list of 5 synergy names + descriptions.
**Proposed:** Frame it as a "tactical briefing" — what synergies are in play this round.

```
  ┌─────────────────────────────────────────────────────┐
  │  ROUND 1/3  │  Target: 500  │  Score: 0            │
  │  Record: 0-0                                        │
  └─────────────────────────────────────────────────────┘

  📋 ROUND SYNERGIES (5 active this round)

  ✦ Clean Sheet [Rare] — GK+CB DEF sum ≥ 17 → both +25 chips
  ✦ Counter-Attack [Epic] — LW PAC+ST ATK ≥ 16 → ST ×1.4
  ✦ Tiki-Taka [Rare] — 3 CMs PAS ≥ 7 → chain ×1.3/×1.5/×1.3
  ✦ Double Pivot [Uncommon] — 2 CMs PAS ≥ 17 → carryover bonus
  ✦ Set Piece Threat [Rare] — DEF≥9 + SPC≥8 → global +30

  These synergies apply to phases where conditions are met.
  Build your phases around them!

  Press Enter to begin Round 1...
```

**Key change:** Frame as actionable intel, not just a data dump.

---

### 6. Phase Header + Placement ⭐ (HIGHEST PRIORITY — most-played screen)
**Current problems:**
- Header and placement are the same screen but serve different purposes
- Slot filling is sequential (one at a time) with "Press Enter" between each
- Player list is a wall of stats — hard to scan
- No visual representation of the "pitch" for this phase
- Running preview is tacked on at the bottom

**Proposed layout — persistent context + phase-specific zones:**

```
  ┌─────────────────────────────────────────────────────────┐
  │  R1/3  │  Score: 0/500  │  0-0  │  Phase 1/6          │
  └─────────────────────────────────────────────────────────┘

  🛡️ GOAL KICK — "Keeper launches long — defenders win the header"
  Weight: DEF  │  Slots: GK → CB → CB  │  Cards: 3

  ─── ON THE PITCH ─────────────────────────────────────────
  │  Slot 1: GK          │  [EMPTY]                        │
  │  Slot 2: CB [DEF≥7]  │  [EMPTY]                        │
  │  Slot 3: CB [DEF≥6]  │  [EMPTY]                        │
  ──────────────────────────────────────────────────────────

  ─── ELIGIBLE PLAYERS ─────────────────────────────────────
  For slot: GK
  ┌──────────────────────────────────────────────────────┐
  │ [0] Alisson     GK→GK  FRESH   42 chips  DEF:9 SPC:7│
  │ [1] Ter Stegen  GK→GK  70%     35 chips  DEF:8 SPC:6│
  └──────────────────────────────────────────────────────┘
  ⚡ Synergy hints: Alisson → could trigger Clean Sheet

  Pick # (or 'skip'): _
```

**After filling a slot, the pitch updates:**
```
  ─── ON THE PITCH ─────────────────────────────────────────
  │  Slot 1: GK          │  ✅ Alisson     42 chips  FRESH │
  │  Slot 2: CB [DEF≥7]  │  [EMPTY]                        │
  │  Slot 3: CB [DEF≥6]  │  [EMPTY]                        │
  │                                                         │
  │  Running total: 42 pts  (1/3 cards placed)             │
  ──────────────────────────────────────────────────────────
```

**Key changes:**
- **Persistent context bar** at top (round, score, target, phase #) — always visible
- **Pitch zone** shows slots as fillable slots with status (empty ✅ filled)
- **Eligible players** scoped to current slot only (not all slots at once)
- **Running total** shown inline after each placement
- **No "Press Enter" between slots** — flow naturally from slot to slot
- **Synergy hints** per player (what they'd unlock)

---

### 7. Phase Result ⭐ (HIGH PRIORITY — core feedback loop)
**Current problems:**
- Math breakdown is useful but visually dense
- Synergy info is tacked on at the bottom
- No visual emphasis on the total vs target
- Hard to quickly see "did this phase do well?"

**Proposed layout:**

```
  ┌─────────────────────────────────────────────────────────┐
  │  R1/3  │  Score: 187/500  │  0-0  │  Phase 1/6 done   │
  └─────────────────────────────────────────────────────────┘

  🛡️ GOAL KICK RESULT
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Player          Pos   Base  +Syn  ×Mult  ×Fat  = Sub
  ─────────────────────────────────────────────────────────
  Alisson         GK      42    +25  ×1.00  ×1.00    67
  Van Dijk        CB      37    +25  ×1.00  ×1.00    62
  Rudiger         CB      33    +0   ×1.00  ×0.70    23
  ─────────────────────────────────────────────────────────
  Subtotal                                          152

  ⚡ SYNERGIES FIRED
  ┌──────────────────────────────────────────────────────┐
  │  Clean Sheet          Alisson + Van Dijk             │
  │  "GK+CB DEF ≥ 17"     → both +25 chips              │
  │                                                      │
  │  Organised Defence    Van Dijk + Rudiger             │
  │  "2 CB DEF ≥ 15"     → ... (didn't fire, Rudiger fat)│
  └──────────────────────────────────────────────────────┘

  ══════════════════════════════════════════════════════
  PHASE TOTAL:  152
  ══════════════════════════════════════════════════════

  Press Enter for next phase...
```

**Key changes:**
- **Table alignment** — proper columns for the math breakdown
- **Synergies get their own zone** with contributor names and rule text
- **Phase total** is BIG and centered
- **Color coding:** green if above par, yellow if close, red if below
- **Fatigue shown inline** — ×0.70 in red for fatigued players

---

### 8. Round Result
**Current:** Won/lost + phase-by-phase breakdown. Decent.
**Proposed:** Add a momentum indicator and fatigue summary.

```
  ┌─────────────────────────────────────────────────────────┐
  │  ROUND 1 COMPLETE                                       │
  └─────────────────────────────────────────────────────────┘

  🎉 ROUND WON!   687 / 500

  Phase Breakdown:
  ┌──────────────────────────────────────────────────────┐
  │  1. Goal Kick         152 pts  ████████░░            │
  │  2. Build-Up          134 pts  ███████░░░            │
  │  3. Counter-Attack    178 pts  █████████░  ⚡×2 syn  │
  │  4. Defensive Block   101 pts  █████░░░░░            │
  │  5. Tiki-Taka          89 pts  ████░░░░░░            │
  │  6. Set Piece          33 pts  ██░░░░░░░░            │
  └──────────────────────────────────────────────────────┘
  Total: 687 / 500

  📊 Squad Fatigue:
  ████████████████████ 8 players fresh
  ████░░░░░░░░░░░░░░░░ 3 players at 70%
  ██░░░░░░░░░░░░░░░░░░ 1 player at 49%

  Match: 1-0 (need 2 to win)

  Press Enter for next round...
```

---

### 9. Match Result / Campaign End
**Current:** Functional. Campaign bracket is good.
**Proposed:** Add match stats summary.

```
  ╔═══════════════════════════════════════════════════╗
  ║     GROUP STAGE — WON!                           ║
  ╚═══════════════════════════════════════════════════╝

  🏆 FC Rivals defeated  2-1

  Match Stats:
  ┌──────────────────────────────────────────────────────┐
  │  Rounds:  W-L-W (2-1)                                │
  │  Best phase:  Counter-Attack (178 pts)               │
  │  Best synergy: Counter-Attack ×2 fires               │
  │  MVP:  Mbappé (3 phases, 210 total chips)            │
  │  Fatigue remaining: 6 fresh, 4 tired                 │
  └──────────────────────────────────────────────────────┘

  Campaign: 1/5 matches won
  Next: Round of 16 vs Real Sociedad

  Press Enter to continue...
```

---

## Implementation Priority

| Priority | Screen | Effort | Impact |
|----------|--------|--------|--------|
| 🔴 P0 | Phase Placement (screen 6) | High | Most-played, biggest UX win |
| 🔴 P0 | Phase Result (screen 7) | Medium | Core feedback, every phase |
| 🟡 P1 | Squad Builder (screen 2) | High | First impression, complex |
| 🟡 P1 | Round Result (screen 8) | Medium | Momentum feel |
| 🟢 P2 | Round Start / Synergies (screen 5) | Low | Informational |
| 🟢 P2 | Formation Select (screen 3) | Low | One-time choice |
| 🟢 P2 | Match Intro (screen 4) | Low | One-time per match |
| ⚪ P3 | Title, Campaign End | Minimal | Already fine |

---

## Technical Approach

### Shared Components (extract to `src/ui/`)

```
src/ui/
├── __init__.py
├── context_bar.py    # Persistent top bar (round/score/target/phase)
├── pitch.py          # ASCII pitch visualization for slot filling
├── player_card.py    # Compact player display with fatigue color
├── synergy_box.py    # Synergy info panel (name, contributors, rule)
├── table.py          # Aligned column table renderer
└── colors.py         # Color constants and semantic color helpers
```

### Key Refactors

1. **Extract `show_phase_header` into a `ContextBar` component** that takes match state and renders consistently everywhere
2. **Replace sequential slot filling with a loop** that shows the pitch state + eligible players for current slot
3. **Create a `PhaseResultView` class** that formats the scoring breakdown as a proper table
4. **Add `color_for_value(val, thresholds)`** helper for semantic coloring (green/yellow/red based on context)

### What NOT to Change

- Game logic (scoring, phases, synergies) — untouched
- Data structures (MatchState, Phase, PlayerCard) — untouched
- Terminal I/O pattern (cprint, input) — keep Rich abstraction
- Test suite — existing tests should still pass

---

## Open Questions

1. **Do we want a visual pitch diagram** (ASCII art showing player positions on a field)?
   - Pro: Immersive, football-themed
   - Con: Takes vertical space, might not fit narrow terminals

2. **Should the squad builder show one position group at a time** (paginated) or all at once?
   - Current: all at once (scrollable)
   - Alternative: tab through GK → CB → FB → ... with left/right arrows

3. **Do we want sound/haptic feedback** for synergy triggers? (Probably out of scope for terminal)

4. **Minimum terminal width?** Should we design for 80-col, 120-col, or auto-adapt?

---

## Next Steps

1. Review this plan — agree on priorities and any layout changes
2. Create `src/ui/` module with shared components
3. Start with P0: Phase Placement + Phase Result screens
4. Playtest after each screen refactor
5. Move to P1: Squad Builder + Round Result
