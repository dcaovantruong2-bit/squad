# Archify Prompt — Squad Game Codebase Visualization

> Copy and paste this entire block into Archify to generate a comprehensive visualization of the Squad football card roguelike codebase.

```text
Visualize the Squad football card roguelike game codebase. This is a single-page web app with a Python backend for testing.

## FILE TREE

```
squad/
├── web/
│   ├── game.html              # SPA shell — routing, screen loader, nav
│   ├── game-data.js            # All game data — players, phases, synergies, formations
│   ├── game-engine.js          # All game logic — scoring, campaign, shop, persistence
│   ├── game-motion.js          # Animation functions (screen transitions)
│   ├── game-motion.css         # Animation keyframes (CRT scanlines, neon glow)
│   └── screens/
│       ├── title-screen.html   # Title + onboarding + Quick Start / Draft / Continue
│       ├── squad-builder.html  # Player draft under budget
│       ├── formation-select.html # Formation carousel with pitch diagram
│       ├── phase-select.html   # Pick 3 of 8 phases in order
│       ├── match-screen-fixed.html # Live match — place players in slots, synergy feedback
│       ├── phase-result.html   # Score breakdown (Balatro-style formula viz)
│       ├── round-result.html   # Round verdict + campaign map
│       ├── shop-screen.html    # Spend morale on items between rounds
│       ├── campaign-complete.html # Final stats + Hall of Fame
│       └── index.html          # Screen hub
├── src/
│   ├── cards.py                # PlayerCard, SynergyCard, FormationCard data models
│   ├── phases.py               # Phase definitions, OOP penalty system
│   ├── scoring.py              # Chips formula, synergy detection, round scoring
│   ├── match.py                # MatchState, round management, campaign config
│   ├── shop.py                 # Shop items, morale economy
│   └── loader.py               # Data loading from TOML
├── main.py                     # Python CLI game loop
├── tests/
│   ├── test_phases.py
│   ├── test_scoring.py
│   ├── test_synergy.py
│   ├── test_playtest.py
│   └── conftest.py
└── README.md
```

## ARCHITECTURE

The SPA shell (game.html) loads game-data.js → game-engine.js → game-motion.js. It then starts by fetching and injecting title-screen.html via DOMParser. The shell exposes `window.Game.navigate(screenId)` which all screens call to transition.

Game state lives in `var G = { ... }` (global, declared in game-data.js). All screens read/write G directly. The engine provides pure functions that mutate G.

## DATA FLOW

```
game-data.js declares:           game-engine.js mutates:
  G = { selectedIds, matchIdx,     submitPhase(placements) → scores, advances phaseIdx
        roundIdx, phaseIdx,        finishRound() → checks target, awards morale
        roundScore, morale,        finishMatch() → checks match won, advances matchIdx
        fatigue, shopBuffs }       buyShopItem(id) → deducts morale, applies buff
  PLAYERS[33]                      saveGame() / loadGame() → localStorage
  FORMATIONS[6]
  ALL_PHASES[8]
  SYNERGIES[30]
  COMBO_CHAINS[8]
  CAMPAIGN_MATCHES[5]
  SHOP_ITEMS[10]
```

## SCREEN ROUTING

```
title → squad → formation → phases → match → phase-result → (repeat 3×) →
round-result → shop → (repeat for rounds 2-3) → round-result →
campaign-complete (last match) OR back to shop (next opponent)
```

## SCREEN INJECTION

game.html fetches each screen file, parses it with DOMParser, inlines styles (kept in cached) and appends a <script> tag for each found script. Scripts execute synchronously in an appended DOM node. All exposed globals (G, Game, functions) persist — screens share the same namespace.

## KEY ENGINE FUNCTIONS

| Function | Purpose |
|----------|---------|
| submitPhase(placements) | Score phase, advance phaseIdx, apply fatigue |
| finishRound() | Check target, return 'next-round' or 'match-done' |
| finishMatch() | Determine winner, return 'next-match' or 'campaign-won' |
| calculatePhaseScore(field) | Balatro: chips × addMult × xMult × formation × momentum |
| detectSynergies(field) | Check 18 phase synergies from current placements |
| detectSquadSynergies(squad) | Check 12 persistent trait-based synergies |
| applyFatigue(playerId) | ×0.7 per use (multiplicative) |
| recoverFatigue(amount) | 30% of lost fatigue between rounds |
| startRound() / startMatch() | Reset state, deal phases |
| dealPhases() | Shuffle all 8 phases, return IDs |
| autoFillSquad() / autoFillAll() | Best-fit squad/phase placement |
| saveGame() / loadGame() | localStorage persistence |

## GAME DESIGN SUMMARY

- Genre: Football card roguelike — build squad (11 from 33), pick 3 tactical phases, assign players to slots, stack synergies, beat round targets across 5 escalating matches
- Scoring: Balatro-style CHIPS × ADD MULT × ×MULT × formation × momentum × combo chain
- Fatigue: ×0.7 per use, 30% recovery between rounds — forces rotation across 9 phase slots per match
- Campaign: 5 matches, win 2 of 3 rounds each. Targets: [4000,6500,9000] → [8500,12000,16000]
- Morale: +1 phase win, +3 round win, +2 beat ×1.5 target, +5 match win, +3 clean sweep
- Synergies: 18 phase (position/stat) + 12 persistent (trait-count based)
- Auto-win: roundScore ≥ target = skip remaining phases (from Python original)
- Momentum: ×1.0 → ×1.2 → ×1.5 across phases 1-3
- Shop: 10 items between rounds, single-use or per-round buffs
```

**Archify output URL (if available):** [Will be generated after you paste]

**Saved to:** `~/games/squad/web/ARCHIFY_PROMPT.md`
