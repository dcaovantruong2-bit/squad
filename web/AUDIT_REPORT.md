# Squad Web Frontend — Audit Report

**Date:** 2026-07-16  
**Scope:** Read-only audit of `~/games/squad/web/`  
**Files examined:** game.html, game-engine.js, game-ui.js, game.css, index.html, index.html.old, sw.js, manifest.json, server.py, cors-proxy.py, DESIGN.md, README.md, screens/*.html, .od-skills/

---

## 🔴 CRITICAL: Cross-file Formula Inconsistency

### `FORMULA_TEXT` / `FORMULA_PARTS` (game-ui.js:884-906) ≠ `CHIPS_FORMULA` (game-engine.js:45-55)

The displayed formula strings in the player picker do NOT match the actual chip calculations. This means **users see wrong formula descriptions** while the engine uses different math.

| Position | CHIPS_FORMULA (actual) | FORMULA_TEXT (displayed) | Discrepancy |
|----------|----------------------|------------------------|-------------|
| **ST**   | ATK×4 + PAC×1.5      | ATK×4 + PAC×2 + SPC×1  | PAC coef 1.5≠2; SPC not in actual formula |
| **LW**   | PAC×3 + ATK×2        | ATK×2 + PAC×3 + PAS×1  | PAS not in actual formula |
| **RW**   | PAC×3 + ATK×2        | ATK×2 + PAC×3 + PAS×1  | PAS not in actual formula |
| **CM**   | PAS×4 + DEF×1        | PAS×3 + ATK×2 + DEF×1  | PAS coef 4≠3; ATK not in actual formula |
| **CAM**  | PAS×3.5 + ATK×2 + SPC×1 | PAS×3 + ATK×2 + SPC×1 | PAS coef 3.5≠3 |
| **CDM**  | DEF×4 + PAS×1        | DEF×2 + PAS×3 + ATK×1  | DEF 4≠2, PAS 1≠3, ATK not in actual |
| **CB**   | DEF×5                | DEF×3 + PAC×2 + ATK×1  | DEF 5≠3; PAC+ATK not in actual formula |
| **FB**   | DEF×3 + PAC×1.5      | DEF×2 + PAC×3 + PAS×1  | DEF 3≠2, PAC 1.5≠3, PAS not in actual |
| **GK**   | DEF×3 + SPC×2        | DEF×3 + SPC×1          | SPC coef 2≠1 |

**Fix:** Update `FORMULA_TEXT` and `FORMULA_PARTS` in `game-ui.js` (lines 884-906) to match `CHIPS_FORMULA` in `game-engine.js` (lines 46-55).

---

## 🟠 MEDIUM Issues

### 1. `index.html.old` — Completely Stale/Dead (198KB)

- **File:** `~/games/squad/web/index.html.old` (3,895 lines, 198,938 bytes)
- **Evidence:** Zero references anywhere in the codebase (grep for `index.html.old` returns 0 results)
- **Nature:** Old monolithic version containing all game logic inline. Replaced by the modular split: `game.html` (961 lines) + `game-engine.js` (333 lines) + `game-ui.js` (2,042 lines)
- **Suggestion:** Archive or delete this file — it's not referenced by anything and adds noise.

### 2. Missing `case 'phase-select'` in `showScreen()` Switch

- **File:** `game-ui.js`, lines 102-111
- **Issue:** The `showScreen()` function has cases for `title`, `squad`, `formation`, `match`, `phase-result`, `round-result`, `shop`, and `campaign`, but **not** `phase-select`. 
- **Impact:** Line 773 (`startPhaseSelection()` at line 773) calls `showScreen('phase-select')`, which works because the DOM ID lookup succeeds, but the render function `renderPhaseCards()` was already called manually on line 772. This works but breaks the encapsulation pattern used by every other screen.
- **Fix:** Add `case 'phase-select': renderPhaseCards(); break;` to the switch.

### 3. Service Worker Caches Wrong Entry Point

- **File:** `sw.js`, lines 2-5
- **Code:** `urlsToCache = ['/', '/index.html', '/manifest.json']`
- **Issue:** The actual SPA entry point is `game.html`, not `index.html`. `index.html` is a 109-byte meta-refresh redirect to `game.html`. The SW will cache the redirect page, not the actual app.
- **Fix:** Change to `urlsToCache = ['/', '/game.html', '/manifest.json']`.
- **Note:** Also lacks caching of `game-engine.js`, `game-ui.js`, and `game.css` — these won't be cached for offline use.

### 4. Misleading HTML Comment

- **File:** `game.html`, line 954
- **Text:** `<!-- GAME ENGINE (inline for SPA reliability) -->`
- **Issue:** Comment claims scripts are "inline", but lines 956-958 show external `<script src="...">` tags. This is misleading for maintainers.
- **Fix:** Update comment to reflect reality: `<!-- GAME SCRIPTS: game-engine.js must load before game-ui.js -->`

### 5. `screens/` Directory — 9 Stale Design Artifacts

- **File:** `screens/` directory
- **Stale files (design iterations, not in use):**
  - `title-formation-iter1-whiteboard.html` (165 lines) + `.artifact.json`
  - `title-formation-iter2-datapanel.html` (191 lines) + `.artifact.json`
  - `title-formation-iter3-minimal.html` (124 lines) + `.artifact.json`
  - `title-formation-iter4-tactical.html` (754 lines, 32KB) + `.artifact.json`
  - `title-mockup-1-teamsheet.html` (83 lines) + `.artifact.json`
  - `title-mockup-2-terminal.html` (115 lines) + `.artifact.json`
  - `title-mockup-3-floodlights.html` (76 lines) + `.artifact.json`
  - `title-mockup-4-formation.html` (145 lines) + `.artifact.json`
  - `title-mockup-5-cards.html` (179 lines) + `.artifact.json`
- **Active screens (used by the current app):**
  - `title.html`, `squad.html`, `formation.html`, `phase-select.html`, `match.html`, `phase-result.html`, `round-result.html`, `campaign.html`, `shop.html`
- **Suggestion:** Move the 9 iter/mockup files into an `archive/` subdirectory. Keep only the 9 active screen stubs.

### 6. `server.py` — Legacy Terminal Wrapper, Not Current Game

- **File:** `server.py` (159 lines)
- **Issue:** This is a Flask server that wraps a Python terminal game via subprocess (line 2 refers to `main.py`). It runs on port 8081 and serves a VT100 terminal UI. This is **NOT** the current HTML/JS web frontend. It's a leftover from an earlier architecture.
- **Note:** `cors-proxy.py` (port 8082) is similarly a design tool proxy, not app code. These are useful as-is but may confuse new contributors.

### 7. `var` in `game-engine.js` — Inconsistent with `let`/`const` in `game-ui.js`

- **File:** `game-engine.js` — all 23 `for` loops use `var` (function-scoped)
- **File:** `game-ui.js` — mixed: uses `const`/`let` in modern code (lines 48-89, 152-220, 726-728, etc.) but `var` in 11 places (lines 266, 710, 734, 742, etc.)
- **Issue:** Mixed scope semantics. Function-level `var` hoisting can cause subtle bugs if variables are reused. For example, `game-engine.js` line 324-329 has nested `for(var gi=0;...for(var ci=0;...)` in else-if branches that all share the function scope.
- **Risk:** Low (all in separate branches), but inconsistent style.
- **Fix:** Convert `var` to `let`/`const` in both files for consistency.

---

## 🟡 MINOR Issues

### 8. `manifest.json` Background Color Mismatch

- **File:** `manifest.json`, line 7: `"background_color": "#0d1a2e"`
- **File:** `game.css`, line 13: `--bg: #161120`
- **Issue:** PWA splash/theme color doesn't match the actual CSS background. `#0d1a2e` is a darker blue-grey; `#161120` is a purple-black. Also `theme_color` (`#1a3a1a`, dark green) doesn't match any CSS variable.
- **Fix:** Set `background_color` to `#161120` and `theme_color` to `#231a3a` (matching `--surface`).

### 9. `README.md` References Wrong Entry Point

- **File:** `README.md`, lines 7, 11: `Open index.html` / `Open index.html in Safari`
- **Issue:** The actual app entry is `game.html`. `index.html` is just a 109-byte redirect. Instructions should reference `game.html` directly.
- **Fix:** Update README to say `Open game.html` or `Open index.html (redirects to game.html)`.

### 10. `DESIGN.md` Font Size Contradiction

- **File:** `DESIGN.md`, line 84: Display font size set to **10px**
- **File:** `game.html`, line 15: `.title-logo` uses **48px**
- **File:** `game.css`, lines 60-67: text scale ranges from 11px to 76px
- **Issue:** The DESIGN.md says display font is only 10px, but actual usage varies widely. The 10px spec appears to be for labels only, but the guide doesn't clarify this.
- **Fix:** Clarify DESIGN.md to specify label size vs. heading/title sizes.

### 11. `getShirtNum()` Unusual Mapping

- **File:** `game-ui.js`, line 918
- **Code:** `{ GK:1, CB:4, CB1:5, CB2:5, FB:2, FB1:2, FB2:3, CDM:6, CM:8, CM1:8, CM2:11, CAM:10, LW:7, RW:11, ST:9, ST1:9, ST2:12 }`
- **Issue:** Keys like `CB1`, `CB2`, `CM1`, `CM2`, `ST1`, `ST2` exist in the mapping but no code generates these keys. The `slotFieldPosition()` function only returns bare position strings like `"CB"`, `"CM"`, `"ST"`, or the first element of an array. The suffixed variants are dead code.
- **Fix:** Remove unused suffixed keys or add a `slotNumber` -> shirt number mapping if intended.

### 12. `roundWins` vs `roundsWon` Naming Inconsistency

- **File:** `game-ui.js`
- **Issue:** `G.roundWins` (array of booleans, line 59) vs. `G.roundsWon` (counter, line 60). The singular `Wins` vs. plural `Wins` + `Won` is inconsistent and confusing. `roundWins` reads like a verb ("round wins") but is a noun (array of win states).
- **Fix:** Rename `roundWins` → `roundResults` or `roundOutcomes` for clarity.

### 13. `_psHand` / `_psPicked` Module-level `let` Variables

- **File:** `game-ui.js`, lines 727-728
- **Code:** `let _psPicked = []; let _psHand = [];`
- **Issue:** These are defined at module scope (as `let` in what's essentially a global script) but are really local state for `startPhaseSelection` / `selectPhaseCard`. They persist between rounds and could accumulate stale data if `startPhaseSelection()` isn't called to reset them (it does reset at line 736, but the coupling is fragile).
- **Fix:** Consider wrapping phase selection state in a closure or object.

### 14. No `ARCHITECTURE` Comment in `game-engine.js`

- **File:** `game-engine.js`
- **Issue:** The audit checklist item #12 asked for ARCHITECTURE comments explaining the engine/UI split. The file has only a one-line header `/* SQUAD — Game Engine (clean rebuild) */` at line 1. No architecture documentation.
- **Fix:** Add a comment block at the top of `game-engine.js` explaining: "Pure game logic — no DOM references. Depends on: nothing. Used by: game-ui.js. Contains: PLAYERS, FORMATIONS, SYNERGIES, scoring, synergy detection."

---

## ✅ ITEMS PASSED (No Issues Found)

| Check | Result |
|-------|--------|
| 3. Orphaned DOM IDs | **PASS** — All 50+ `getElementById()` calls match existing HTML `id` attributes |
| 4. Deprecated patterns (`__global__`, `__carryover__`, `min_atk`, `min_pac`) | **PASS** — Only found in `index.html.old`, not in current code |
| 5. `var` shadowing causing infinite loops | **PASS** — No nested `for` loops use the same variable name in overlapping scopes |
| 6. Cross-file function references (SYNERGIES, detectSquadSynergies, etc.) | **PASS** — All referenced names exist in game-engine.js |
| 9. Game.html has 9 screens properly | **PASS** — 9 `screen-*` IDs found: title, squad, formation, phase-select, match, phase-result, round-result, campaign, shop |
| Inline onclick handlers | **PASS** — All 9 HTML onclick-attributed functions exist in game-ui.js global scope |

---

## File-by-File Summary

### `game-engine.js` (333 lines)
- No ARCHITECTURE comment explaining the split → **MINOR**
- Uses `var` everywhere instead of `let`/`const` → **MINOR**
- CHIPS_FORMULA is the source of truth but visually misrepresented → **CRITICAL**

### `game-ui.js` (2,042 lines)
- FORMULA_TEXT/FORMULA_PARTS mismatch with engine → **CRITICAL**
- Missing `case 'phase-select'` in `showScreen()` → **MEDIUM**
- Mix of `var`/`let`/`const` → **MINOR**
- `roundWins` naming oddity → **MINOR**
- `getShirtNum()` has dead suffixed keys → **MINOR**
- `_psHand`/`_psPicked` at module scope → **MINOR**

### `game.html` (961 lines)
- Misleading "inline" comment at line 954 → **MEDIUM**
- Clean screen structure, all 9 screens present → **PASS**

### `index.html.old` (198KB)
- **DEAD FILE** — Zero references anywhere → **MEDIUM**

### `sw.js` (20 lines)
- Caches `/index.html` instead of `/game.html` → **MEDIUM**
- Missing JS/CSS assets from cache → **MINOR**

### `manifest.json` (17 lines)
- Wrong `background_color` and `theme_color` → **MINOR**

### `server.py` (159 lines)
- Legacy terminal-wrapper server, not current game → **INFO**

### `screens/` directory
- 9 stale design artifacts (iter1-4 + mockup1-5) → **MEDIUM**
- 9 active screen stubs (correct) → **PASS**

### `DESIGN.md`
- Font size spec contradicted by actual usage → **MINOR**

### `README.md`
- References `index.html` as entry point → **MINOR**

---

## Recommended Fixes Priority

1. **🔴 CRITICAL** — Fix `FORMULA_TEXT` and `FORMULA_PARTS` in `game-ui.js:884-906` to match `CHIPS_FORMULA` in `game-engine.js:46-55`
2. **🟠 MEDIUM** — Delete or archive `index.html.old`
3. **🟠 MEDIUM** — Add `case 'phase-select'` to `showScreen()` switch
4. **🟠 MEDIUM** — Fix `sw.js` to cache `game.html` and assets
5. **🟠 MEDIUM** — Move stale `screens/` design artifacts to archive
6. **🟠 MEDIUM** — Fix misleading comment in `game.html:954`
7. **🟡 MINOR** — Fix `manifest.json` colors
8. **🟡 MINOR** — Normalize `var` → `let`/`const` in both JS files
9. **🟡 MINOR** — Update README.md entry point reference
