# Squad — Synergy Visual Information Architecture

> How to make synergies clear and understandable at every decision point.
> Three layers, three colors, one unified visual language.

---

## 1. THE THREE LAYERS — Colour & Iconography

Each synergy layer gets a **unique visual identity** — colour, icon, and spatial treatment — so players instantly know what type of synergy they're seeing.

### 1.1 Layer Key

```
┌──────────────────────────────────────────────────────────────┐
│  LAYER           COLOR        ICON      SHAPE               │
├──────────────────────────────────────────────────────────────┤
│  Persistent      #FFD700      ◆  (diamond)  Top bar badge,  │
│  (squad-level)   gold                   always visible       │
│                                                              │
│  Phase-Specific  #39FF14      ◆  (diamond)  Slot-level badge │
│  (stats/pos)     neon green               per phase          │
│                                                              │
│  Combo Chain     #FFA500      ◆  (diamond)  Sequence preview │
│  (tag order)     orange                   between phases     │
└──────────────────────────────────────────────────────────────┘
```

**Why these colors:**
- **Gold** = squad-level, permanent, "premium" — you earned this in the draft, it's yours
- **Neon green** = phase-level, tactical, "activated" — the primary game accent, signals execution
- **Orange** = sequencing, momentum, "prediction" — warm, suggests forward planning

### 1.2 Effect Type Sub-Taxonomy (within each layer)

Each synergy fires an **effect type**. These get distinct visual treatments on the value badge:

| Effect Type   | Value Display    | Badge Style                          | Usage          |
|---------------|------------------|--------------------------------------|----------------|
| `chips`       | `+20 ♣`          | Gold text, no border, `♣` suffix    | Flat chips add |
| `add_mult`    | `+4 mult`        | Cyan/blue bg, `mult` label           | Additive mult  |
| `x_mult`      | `×1.5`           | Purple/magenta bg, `×` prefix        | Multiplicative |
| `carryover`   | `→+40 ♣`         | Orange border, `→` prefix, dashed    | Next-phase     |
| `special`     | `⚡`              | Rainbow/gradient, icon-only          | Rare unique    |

**Why this matters:** A player seeing `+20 ♣` vs `×1.5` needs to immediately understand the difference in impact. Chips are additive (weak early, scale with mult), x_mult is exponential (strong with high chips). These deserve different visual weight.

---

## 2. COMPONENT LIBRARY — Synergy Primitives

### 2.1 Synergy Badge (compact, inline)

The smallest synergy atom. Appears on player cards, slot cards, live score bar.

```
┌──────────────────────┐
│ ◆ Clean Sheet  +20 ♣ │  ← gold badge (persistent)
│ ◆ One-Two     ×1.5   │  ← green badge (phase)
│ ◆ Def→Trans   ×1.5   │  ← orange badge (combo)
└──────────────────────┘
```

**Spec:**
- Height: 20px
- Padding: 2px 8px
- Left icon: filled diamond (8×8) in layer color
- Text: synergy name in VT323 14px, truncated to 18 chars if needed
- Right: value badge (see §1.2) right-aligned
- Background: transparent, 1px border in layer color at 15% opacity
- Hover: border opacity → 40%, subtle glow in layer color

**CSS tokens to add:**
```css
--syn-persistent: #FFD700;
--syn-phase: #39FF14;
--syn-combo: #FFA500;
--syn-chips: #FFD700;
--syn-add-mult: #00CCFF;
--syn-x-mult: #C084FC;
--syn-carryover: #FFA500;
```

### 2.2 Synergy Row (explanatory, for panels/accordions)

The medium-sized format. Shows WHY and with WHOM.

```
┌──────────────────────────────────────────────────────────────┐
│ ◆ Clean Sheet                                    +20 ♣      │
│   GK DEF + CB DEF ≥ 18                                      │
│   Gigi The Wall [GK] · El Capitán [CB]                      │
│                                                              │
│ ◆ Stretch the Backline                         ×1.5         │
│   FB PAC + LW PAC ≥ 17                                       │
│   Dani Elvis [FB] · Bale Out [LW]                            │
│                                                              │
│ ◆ Pace & Power (PERSISTENT)                     ×1.3         │
│   3+ pacey+physical players in squad                         │
│   All pacey+physical get ×1.3 per phase                      │
└──────────────────────────────────────────────────────────────┘
```

**Spec:**
- Height: auto (60-80px per row)
- Left: 10px tall filled diamond in layer color (16px × 16px at left edge)
- Name: VT323 18px bold, layer color
- Tag: (PERSISTENT) or (CARRYOVER) in muted, 11px, uppercase
- Description: VT323 14px, fg-dim
- Contributors: VT323 13px, muted, with position badges [POS] in their stat color
- Value badge: far right, see §1.2
- Background: surface (#231a3a), 1px border-left in layer color (4px wide accent bar)
- Separated by 4px gap

### 2.3 Synergy Summary Card (overview, for squad builder)

The squad builder shows a summary of ALL persistent synergies that WILL fire with the current squad.

```
┌──────────────────────────────────────────────────────────────┐
│  ◆ SQUAD SYNERGIES (Persistent — always active)    5 firing  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ◆ Pace in Behind    ×1.15    5/5 pacey players in squad     │
│     ◆ ◆ ◆ ◆ ◆      (Mbappé, Bale Out, El Caníbal...)        │
│                                                              │
│  ◆ Iron Wall         ×1.2     4/3 physical players           │
│     ◆ ◆ ◆ ◆         + fatigue penalty ×0.6                   │
│                                                              │
│  ◆ Clinical Edge     +15 ♣    3/2 clinical players           │
│     ◆ ◆ ◆           attackers only (LW/RW/ST)                │
│                                                              │
│  ◆ Two Up Top        ×1.3     2/2 poachers                   │
│     ◆ ◆             STs only                                 │
│                                                              │
│  ◆ Playmaker Net.    ×1.15    3/3 playmakers                 │
│     ◆ ◆ ◆           midfield only (CM/CAM/CDM)               │
│                                                              │
│  ── NOT TRIGGERED ─────────────────────────────────────────── │
│                                                              │
│  ◇ Pace & Power     ×1.3     1/2 pacey+physical     (need 1) │
│  ◇ Silent Killers   ×1.25    0/2 clinical+pacey      (need 2)│
│  ◇ Leadership Cncl  +15 ♣    2/3 leaders              (need 1)│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Spec:**
- Section header: gold text, displays count of triggered vs. total
- Triggered: filled gold diamond `◆`, gold text, progress "N/M" indicator
- Untriggered: hollow diamond `◇`, muted text, shows what's missing
- Each row: compact version of SynergyRow
- Sort: triggered first (by effect type: x_mult > add_mult > chips), then untriggered (by how close to triggering)
- Scrollable if > 5 rows

### 2.4 Combo Chain Preview (phase picker)

The most important NEW component. Shows predicted combos BEFORE the player commits.

```
┌──────────────────────────────────────────────────────────────┐
│  ⛓ PHASE ORDER — Combo Preview                               │
│                                                              │
│  Your picks:                                                 │
│  ┌──────────┐  →  ┌──────────┐  →  ┌──────────┐            │
│  │ 1. Goal   │     │ 2. Direct│     │ 3. Counter│            │
│  │   Kick    │     │   Play   │     │   Attack  │            │
│  │ Defensive │     │Transition│     │Transition │            │
│  └──────────┘     └──────────┘     └──────────┘            │
│                                                              │
│  Combos detected:                                            │
│  ◆ Def→Trans   ×1.5   "Absorb pressure, hit on break"      │
│  ◆ Trans→Trans +35 ♣  "Rapid succession"                    │
│                                                              │
│  No combo (End): last phase has no tag after it              │
│                                                              │
│  ⚠ If you swapped pick 2 to "Build-Up" (Possession):        │
│     ◇ Def→Poss    NO COMBO   (check COMBO_CHAINS)            │
│                                                              │
│  Total combo bonus: ×1.5 mult + 35 chips                     │
└──────────────────────────────────────────────────────────────┘
```

**Spec:**
- Header: orange text `⛓ PHASE ORDER`
- Phase cards: mini 80px-wide cards showing pick #, name, tag color
- Arrows between cards: thick `→` in orange if combo fires, thin `→` in muted if not
- Combo rows: SynergyRow format in orange
- "What if" hint: shows alternative picks and whether they'd combo
- Total combo bonus: summarized at bottom
- **Empty slots:** show "Pick 3 phases to preview combos" with pulsing placeholder cards

### 2.5 Live Synergy Bar (match screen, always visible)

Replaces the current `live-synergy-badges`. Three sections side by side.

```
┌──────────────────────────────────────────────────────────────┐
│  ◆ 5 Persistent  │  ⬡ 2 Phase Syn  │  ⛓ Combo: +35 ♣  ×1.5 │
│  ◆ ◆ ◆ ◆ ◆      │  ⬡ ⬡            │  (Def→Trans→Trans)     │
└──────────────────────────────────────────────────────────────┘
```

**Spec:**
- Position: below live score bar, full width
- Three equal sections with vertical dividers
- Persistent section: gold icons, "N Persistent" label, hover to reveal names
- Phase section: green icons, shows count of currently-fired synergies based on placed players (live-updating)
- Combo section: orange, shows the current chain bonus if phase sequence applies
- Compact: 32px tall, font VT323 13px
- Background: bg-deep (#0d0a18), border 1px solid border (#3d2d5c)

### 2.6 Phase Result Synergy Breakdown (accordion redesign)

Current accordion is collapsed and vague. Redesigned with categories and real math.

```
┌──────────────────────────────────────────────────────────────┐
│  ▸▸ SYNERGIES FIRED THIS PHASE                       [▼]     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ═══ PHASE-SPECIFIC (stats-based) ════════════════════════   │
│                                                              │
│  ⬡ Clean Sheet                          +20 ♣               │
│    GK DEF + CB DEF ≥ 18                                       │
│    Gigi The Wall [GK] DEF:10 + El Capitán [CB] DEF:10 = 20 ✓ │
│                                                              │
│  ⬡ Overload (CM)                        +3 mult              │
│    2+ players at same position                               │
│    Don Andres [CM] · Captain Stevie [CM]                     │
│                                                              │
│  ⬡ One-Two                              ×1.5                │
│    CM PAS + ST PAC ≥ 15                                       │
│    Puppet Master [CM] PAS:10 + Mbappé [ST] PAC:9 = 19 ✓     │
│                                                              │
│  ── DID NOT FIRE ──────────────────────────────────────────  │
│                                                              │
│  ◇ Route One                          (+30 ♣ missed)        │
│    CB PAS + ST PAC ≥ 14                                       │
│    Best: CB PAS:6 + ST PAC:9 = 15 ✓ but CB is NOT ON FIELD   │
│    All your CBs played but couldn't find ST pair              │
│                                                              │
│  ═══ COMBO CHAIN (phase order) ═══════════════════════════   │
│                                                              │
│  ⛓ Defensive → Transition              ×1.5                 │
│    Goal Kick (Defensive) ◆ Direct Play (Transition)          │
│    "Absorb pressure, hit on break"                            │
│                                                              │
│  ═══ PERSISTENT (always active) ══════════════════════════   │
│                                                              │
│  ◆ Pace in Behind (PERSISTENT)          ×1.15                │
│    Applied to: Mbappé, Bale Out, El Caníbal, Dani Elvis...   │
│    5 pacey players in squad                                  │
│                                                              │
│  ◆ Iron Wall (PERSISTENT)              ×1.2 + fatigue ×0.6  │
│    Applied to: The Waz, Bale Out, Captain Stevie, Yaya...    │
│    4 physical players in squad                               │
│                                                              │
│  ─────────────────────────────────────────────────────────── │
│  TOTAL SYNERGY IMPACT:  +45 ♣  |  +3 mult  |  ×2.73 mult    │
│  (chips add) (add mult) (×mult product: 1.5×1.5×1.15×1.2)   │
└──────────────────────────────────────────────────────────────┘
```

**Spec:**
- Collapsed state: `▸▸ 7 SYNERGIES FIRED (+45 chips, ×2.73 mult) [▼]`
- Expanded: three sections with colored headers
- Each triggered synergy shows the ACTUAL math (stat values that met the threshold)
- "Did not fire" section is collapsed by default (secondary accordion), toggleable
- Shows WHY a synergy didn't fire — positional awareness
- Total synergy impact summary at bottom: sums chips, add_mult, product of all x_mult
- Background sections alternate: phase=surface, combo=surface darker, persistent=surface

---

## 3. DECISION-POINT FLOWS

### 3.1 Squad Builder → "What synergies will I have?"

```
┌──────────────────────────────────────────────────────────────┐
│                    SQUAD BUILDER                             │
│                                                              │
│  ┌─────────────────────┐   ┌──────────────────────────────┐ │
│  │ Your Squad (8/11)   │   │ ◆ PERSISTENT SYNERGIES       │ │
│  │                     │   │                               │ │
│  │ [player cards]      │   │ ◆ Pace in Behind  ×1.15  3/5 │ │
│  │                     │   │ ◆ Clinical Edge  +15 ♣  2/2  │ │
│  │                     │   │                               │ │
│  │                     │   │ ── Near misses ──             │ │
│  │                     │   │ ◇ Leadership (need 1 leader)  │ │
│  │                     │   │                               │ │
│  │                     │   │ ⚠ Budget remaining: 120      │ │
│  │                     │   │ Tip: Add 1 leader for +15♣   │ │
│  └─────────────────────┘   └──────────────────────────────┘ │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ ◆ PHASE SYNERGY POTENTIAL (with current draft)          │ │
│  │                                                         │ │
│  │ This squad can potentially trigger 12 phase synergies:  │ │
│  │ ⬡ Clean Sheet (GK+CB), ⬡ Stretch Backline (FB+LW)...  │ │
│  │ [show 5 most promising, rest in expandable]             │ │
│  └─────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

**Key interactions:**
- Right panel updates LIVE as you add/drop players
- Shows persistent synergies that ARE triggered vs. near-misses
- Shows phase synergy POTENTIAL (what COULD fire based on squad positions)
- Near-miss section shows what you're close to unlocking — with a TIP
- Total budget: 360, spent: 240

### 3.2 Phase Picker → "What combos will my picks create?"

```
┌──────────────────────────────────────────────────────────────┐
│  ROUND 1/3 — PICK 3 PHASES IN ORDER                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ ⛓ COMBO PREVIEW BAR (sticky, persists while picking)     ││
│  │                                                          ││
│  │  [  ⬜  ]  →  [  ⬜  ]  →  [  ⬜  ]                      ││
│  │  Pick 1       Pick 2       Pick 3                        ││
│  │                                                          ││
│  │  Combos: —         —         —                           ││
│  │  (pick phases to see chain bonuses)                      ││
│  └──────────────────────────────────────────────────────────┘│
│                                                              │
│  AVAILABLE PHASES (6 of 12, drawn from deck)                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│  │Goal Kick │ │Build-Up  │ │Direct Play│   ...               │
│  │Defensive │ │Possession│ │Transition │                     │
│  │🛡️        │ │🔄        │ │⚡         │                     │
│  └──────────┘ └──────────┘ └──────────┘                     │
│                                                              │
│  ── After picking 2 phases ──                                │
│                                                              │
│  [Goal Kick] → [Direct Play] → [  ⬜  ]                      │
│    Defensive      Transition      ???                         │
│       │               │                                      │
│       └──◆ ×1.5 ────┘                                        │
│       ◆ Def→Trans fires!                                     │
│                                                              │
│  SUGGESTED 3rd PICKS (to extend the chain):                  │
│  ⭐ Counter-Attack (Transition) → adds +35 ♣ Trans→Trans    │
│     Direct Play (Transition)  → adds +35 ♣ Trans→Trans     │
│     (both create a 2-chain combo)                            │
│                                                              │
│  ── Hover/focus interaction ──                               │
│  When hovering a potential 3rd phase:                        │
│  ⛓ Predicted: Def→Trans ×1.5 + Trans→??? see below          │
│  Shows LIVE what the chain would become                      │
└──────────────────────────────────────────────────────────────┘
```

**Key interactions:**
- Sticky combo preview bar at top, updates with each pick
- Phase cards show their tag color-coded (Defensive=info, Possession=fg-dim, Transition=warn, Attacking=danger, Specialist=purple)
- After picking 2 phases, shows SUGGESTED 3rd picks
- Hover shows predicted combo outcome
- Combo arrow between picks animates (glow pulse) when a chain fires

### 3.3 Match Screen → "What's firing RIGHT NOW?"

```
┌──────────────────────────────────────────────────────────────┐
│  ═══════════════════ CONTEXT BAR ════════════════════════════ │
│  R1/3  Phase 2/3  Score: 342/500  ◆5 ⬡3 ⛓×1.5             │
│  ════════════════════════════════════════════════════════════ │
│                                                              │
│  ┌────────────────────┐  ┌──────────────────────────────────┐│
│  │ ▶ PHASE SLOTS      │  │ ▶ ELIGIBLE PLAYERS              ││
│  │                    │  │                                  ││
│  │ [Slot 1: CM] ✅   │  │ For slot: CAM                    ││
│  │  Puppet Master    │  │                                  ││
│  │  42 ♣  ⬡2 syn    │  │ Don Andres  42♣ S2  ⬡One-Two   ││
│  │                    │  │ Juan Maestro 38♣ S1  ⬡N.Post   ││
│  │ [Slot 2: CAM] ⬜   │  │ Bruno Penandes 35♣ S0          ││
│  │  ▸ Tap to fill    │  │                                  ││
│  │  ← active slot     │  │ ⬡ Preview: Adding Don Andres   ││
│  │                    │  │   would trigger:                 ││
│  │ [Slot 3: ST] ⬜    │  │   ⬡ One-Two (CM PAS+ST PAC≥15) ││
│  │  ▸ Tap to fill    │  │   ⬡ Trio (all 3 CMs PAS≥7)      ││
│  └────────────────────┘  └──────────────────────────────────┘│
│                                                              │
│  ┌──────────────────────────────────────────────────────────┐│
│  │ ▶ LIVE SYNERGIES (collapsible)                          ││
│  │                                                          ││
│  │ ◆ Persistent (5): Pace in Behind, Iron Wall, ...        ││
│  │ ⬡ Phase (2): One-Two, Midfield Engine                   ││
│  │   ⬡ One-Two: Puppet Master [CM] + Mbappé [ST]           ││
│  │      PAS:10 + PAC:9 = 19 ≥ 15 ✓ → ×1.5 mult             ││
│  │   ⬡ Midfield Engine: Puppet Master + Captain Stevie      ││
│  │ ⛓ Combo: Def→Trans ×1.5  (Goal Kick→Direct Play)        ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────┘
```

**Key interactions:**
- Context bar shows mini synergy summary: `◆5 ⬡3 ⛓×1.5` (persistent count, phase count, combo multiplier)
- Slot cards show synergy contribution count on filled slots
- When selecting eligible player, shows preview of what synergies would fire if you placed them
- Live synergy panel is collapsible but defaults to open during first few plays, then remembers preference
- Phase synergy badges pulse when a new one fires during placement

### 3.4 Phase Result → "What happened and WHY?"

(See §2.6 for the full accordion design)

**Key interactions:**
- Hero score cascades up with animation
- Synergy accordion starts collapsed, shows `▸▸ 7 SYNERGIES FIRED (+45 chips, ×2.73 mult)`
- Click to expand for full breakdown
- "Did not fire" section helps players LEARN the system
- Total synergy impact summary at bottom

---

## 4. VISUAL HIERARCHY & SPATIAL RULES

### 4.1 Z-Order (what grabs attention)

1. **Score** (gold, largest) — the number that matters
2. **x_mult effects** (purple, prominent) — exponential, highest impact
3. **add_mult effects** (cyan) — additive scaling
4. **chips effects** (gold, smaller) — base addition
5. **Synergy names** (colored text) — context
6. **Trigger conditions** (dim, small) — detail on demand

### 4.2 Spatial Zones (every screen)

```
┌──────────────────────────────────────────────────────────────┐
│  ZONE A: Context Bar (sticky top, 36px)                      │
│  Score · Round · Phase · Mini synergy summary                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ZONE B: Primary Action (center, 60% height)                 │
│  Slots, picker, phase cards, pitch diagram                   │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  ZONE C: Synergy Context (bottom or side panel, 25% height) │
│  Persistent bar + Live preview + Combo bar                   │
│  Collapsible, progressive disclosure                         │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 Progressive Disclosure Strategy

**Level 0 — Always visible:**
- Context bar mini badges: `◆5 ⬡3 ⛓×1.5`
- Slot card synergy contribution count (`⬡2 syn`)

**Level 1 — One tap:**
- Live synergy bar (three sections, compact)
- Hover tooltip on badges

**Level 2 — Expand:**
- Full synergy panel (match screen sidebar)
- Phase result accordion

**Level 3 — Debug / Learning:**
- "Why didn't this fire?" section
- Stat math breakdown

---

## 5. IMPLEMENTATION NOTES

### 5.1 New CSS Variables to Add

```css
/* Synergy layer colors */
--syn-persistent: #FFD700;         /* Gold — squad-level */
--syn-persistent-dim: rgba(255,215,0,0.15);
--syn-persistent-glow: rgba(255,215,0,0.4);

--syn-phase: #39FF14;              /* Neon green — phase-level */
--syn-phase-dim: rgba(57,255,20,0.15);
--syn-phase-glow: rgba(57,255,20,0.4);

--syn-combo: #FFA500;              /* Orange — combo chains */
--syn-combo-dim: rgba(255,165,0,0.15);
--syn-combo-glow: rgba(255,165,0,0.4);

/* Effect type colors */
--syn-chips: #FFD700;              /* +chips */
--syn-add-mult: #00CCFF;           /* +mult */
--syn-x-mult: #C084FC;             /* ×mult */
--syn-carryover: #FFA500;          /* →next phase */
--syn-special: linear-gradient(135deg, #FFD700, #39FF14); /* special */

/* Synergy badges */
--syn-badge-h: 20px;
--syn-badge-padding: 2px 8px;
--syn-badge-gap: 4px;
--syn-diamond-size: 8px;
```

### 5.2 New DOM Components Needed

| Component | File | Replaces |
|-----------|------|----------|
| `SynergyBadge` | `.synergy-badge--persistent`, `--phase`, `--combo` | Current flat `.synergy-badge` |
| `SynergyRow` | `.synergy-row` (extended) | Current simple `.synergy-row` |
| `SynergySummaryCard` | `.synergy-summary-card` | NEW — for squad builder |
| `ComboChainPreview` | `.combo-chain-preview` | NEW — for phase picker |
| `LiveSynergyBar` | `.live-synergy-bar` | Current `.live-synergy-badges` |
| `PhaseResultSynergyAccordion` | `.pr-syn-section` (redesigned) | Current `.pr-syn-section` |

### 5.3 Data Changes Needed (game-engine.js)

1. **COMBO_CHAINS lookup needs a utility function** for computing predicted chains from partial phase selections
2. **Synergy effect type** must be stored in `fired_details` and surfaced through `synergy_descriptions` in the round result
3. **`getAvailableSynergies` needs enhancement** to return effect type and trigger details (not just name+desc)
4. **Phase tag (Defensive/Possession/Transition/Attacking/Specialist) needs to be readable** from ALL_PHASES during combo preview

### 5.4 Icon Mapping

| Icon | Unicode | Meaning |
|------|---------|---------|
| ◆ | U+25C6 | Persistent synergy (filled diamond, gold) |
| ◇ | U+25C7 | Persistent synergy not triggered (hollow) |
| ⬡ | U+2B21 | Phase-specific synergy (hexagon, green) |
| ⬢ | U+2B22 | Phase synergy not triggered (hollow hexagon) |
| ⛓ | U+26D3 | Combo chain |
| ♣ | U+2663 | Chips |
| × | U+00D7 | Multiplier |
| → | U+2192 | Carryover / chain link |

---

## 6. QUICK REFERENCE — Cheat Sheet

### For Players: "What color means what?"
- **Gold** = your squad, always on, drafted well
- **Green** = this moment, right now, tactics paying off
- **Orange** = sequencing, planning ahead, momentum

### For Designers/Devs: Component Checklist
- [ ] `.synergy-badge` with `--persistent`, `--phase`, `--combo` variants
- [ ] `.synergy-row` with layer color left-border, contributors, math
- [ ] `.synergy-summary-card` for squad builder
- [ ] `.combo-chain-preview` for phase picker
- [ ] `.live-synergy-bar` with three sections
- [ ] `.pr-syn-section` redesigned with categories + did-not-fire
- [ ] Context bar mini badges
- [ ] Tooltip on hover for any synergy badge

---

*Version 1.0 — Designed against Squad commit current*
*Design System: Dark Neon Pixel (see web/DESIGN.md)*
