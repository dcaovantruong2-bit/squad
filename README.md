# Squad ⚽

**Football card roguelike — Slay the Spire × Balatro with tactical synergies.**

Build your squad within budget, pick a formation, and play 3 rounds of 6 random phases of play. Fatigue stacks. Rotate smart. Beat the target.

---

## How to Play

```bash
cd ~/games/squad
source .venv/bin/activate
python3 main.py
```

---

## Game Flow

### 1. Squad Builder

Pick 10+ players from **36** within a **360 coin budget**.
- Each player costs ATK+PAC+PAS+DEF+SPC (stat sum, range 15–36)
- Role-group minimums: **1 GK** · **3+ Defenders** (CB/FB) · **3+ Midfielders** (CM/CDM/CAM) · **2+ Attackers** (ST/LW/RW)
- Build creatively — no more rigid per-position quotas. Want 5 CBs and 3 CMs? Go for it.
- **⚡N tags** show synergy potential per player
- Commands: `<number>` to pick, `drop <#>` to remove, `done` to finalize

### 2. Formation Pick

6 formations, all at **×1.0 global mult**. Differentiated by **position bonuses and penalties** — green means boost, red means penalty. ⭐ = recommended for your squad.

| Formation | Boosts | Penalises | Identity |
|-----------|--------|-----------|----------|
| **4-4-2** | — | — | Safe. No surprises. |
| **4-3-3** | LW+20, RW+20 | ST-15, CDM-10 | Wingers thrive. |
| **5-3-2** | CB+25, FB+12 | LW-20, RW-20 | Defence wins. |
| **3-4-3** | ST+20, LW+15, RW+15 | CB-25 | All-out attack. |
| **4-2-3-1** | CM+10, CAM+25 | ST-15 | CAM formation. |
| **4-5-1** | CDM+15, LW+20, RW+20 | ST-20, CB-5 | Counter. |

### 3. Match — 3 Rounds × 6 Phases

Each round draws **6 random phases** from a pool of 11. Each phase you field a subset of your squad using **stat-based slots** instead of rigid positions:

| Phase | Weight | Slots | Description |
|-------|--------|-------|-------------|
| **Goal Kick** | DEF | GK, DEF≥7, DEF≥6 | Keeper + best defenders |
| **Build-Up** | PAS | PAS≥6, PAS≥6, PAS≥7 | Best passers play out |
| **Wing Attack** | PAC | PAC≥7, PAC≥7 | Fastest players overlap |
| **Long Ball** | ATK | DEF≥6+PAC≥5, ATK≥6 | Defender + attacker combo |
| **Defensive Block** | DEF | DEF≥8, DEF≥7, DEF≥6 | Toughest players dig in |
| **Tiki-Taka** | PAS | PAS≥8, PAS≥7, PAS≥6 | Best passers control |
| **Counter-Attack** | PAC | PAC≥7, ATK≥7, PAC≥7 | Pacey break + finisher |
| **Set Piece** | SPC | SPC≥7, ATK≥7+physical | Specialist + target |
| **High Press** | PAC | PAC≥7, PAC≥7, PAC≥6 | All need pace |
| **Through Ball** | ATK | PAS≥7, PAC≥7 | Passer meets runner |
| **Wingback Push** | PAC | PAC≥7, PAS≥6 | FB + winger link-up |

Slot requirements:
- `"GK"` → must be a GK (position-locked)
- `→CB [DEF≥7]` → any player with DEF≥7 scores as CB
- `→ST [ATK≥7, physical]` → ATK≥7 AND physical trait required
- **Fatigue**: Used players get ×0.7 for subsequent phases (resets per round)
- **Synergies re-rolled each round**: 5 fresh random phase synergies per round

### 4. Scoring

```
(base_chips + formation_bonus + synergy_add) × synergy_mult × fatigue
                            ↓
                  Σ(players) × formation_mult
```

Each phase result shows a full math breakdown per player and which synergies fired with contributing players.

---

## The 36 Players

### Strikers (6)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Terry Henri | 33 | pacey, clinical | Stretch Backline, Route One, Battering Ram |
| Big Zlat | 32 | physical, technical | Battering Ram, Set Piece |
| Kun Kun | 29 | pacey, poacher | Route One |
| The Waz | 32 | physical, leader | Battering Ram |
| **Lewan-goal-ski** | 22 | poacher, clinical | Route One, Battering Ram |
| Theo Walk-not | 15 | pacey, poacher | Route One |

### Wingers (6: 3 LW, 3 RW)
| Player | Pos | Cost | Traits | Notable Synergies |
|--------|-----|------|--------|-------------------|
| Bale Out | LW | 34 | pacey, physical | Stretch Backline |
| Dictator Kylian | LW | 31 | pacey, clinical | Stretch Backline |
| Wilfried Za-ha-ha | LW | 18 | pacey, clinical | Stretch Backline |
| **Riyad Mah-rizzle** | RW | 33 | technical, playmaker | Set Piece Threat |
| Arjen Cutback | RW | 32 | pacey, clinical | Stretch Backline |
| El Shaa-ra-wrong | RW | 19 | pacey, clinical | Stretch Backline |

### Midfielders (5 CM)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Captain Stevie | 36 | leader, physical | Midfield Engine, Double Pivot, Trio |
| Don Andres | 35 | technical, playmaker | Midfield Engine, Trio, Set Piece Threat |
| Maestro Xav | 30 | playmaker, technical | Midfield Engine, Double Pivot, Trio |
| **Yaya Too Strong** | 28 | destroyer, physical, leader | Midfield Engine |
| Park Ji-zoom | 16 | physical, leader, journeyman | Journeyman |

### Defensive Mids (3 CDM)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Toni Cruise | 35 | technical, playmaker | Set Piece Threat |
| N'Golo Kanteen | 25 | destroyer, technical | Organised Defence (at CB), Set Piece Threat |
| Nigel de Wrong | 16 | destroyer, physical | Organised Defence (at CB) |

### CAMs (3)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Juan Maestro | 32 | technical, playmaker | Set Piece Threat, Trio (at CM) |
| **Mesut Assist** | 32 | playmaker, technical | Set Piece Threat, Trio (at CM) |
| **Bruno Penandes** | 31 | playmaker, clinical | Set Piece Threat |

### Centre Backs (4)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Van Aura | 31 | leader, technical | Clean Sheet, Organised Defence, Battering Ram, Route One |
| The Rolls Royce | 31 | technical, leader | Clean Sheet, Organised Defence, Battering Ram, Route One |
| JT The Rock | 25 | physical, aerial | Clean Sheet, Organised Defence, Battering Ram |
| Per Merterslower | 15 | leader, aerial | Clean Sheet, Organised Defence |

### Full Backs (5)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Cafu Express | 34 | pacey, physical | Wingback Overlap, Stretch Backline |
| Jordi Overlap | 33 | pacey, physical | Wingback Overlap, Stretch Backline |
| Lahm-burger | 31 | technical, leader | Wingback Overlap |
| **David Alaba-daba** | 31 | technical, leader | Wingback Overlap |
| Kola-sin-wreck | 16 | destroyer, leader | — |

### Goalkeepers (4)
| Player | Cost | Traits | Notable Synergies |
|--------|------|--------|-------------------|
| Gigi The Wall | 27 | leader, aerial | Clean Sheet |
| **Rocket Raya** | 28 | technical, leader | Clean Sheet |
| Thibaut Courteeth | 21 | destroyer, leader | Clean Sheet |
| Claudio Bra-voops | 17 | aerial | Clean Sheet |

---

## The 13 Phase Synergies (5 random per round)

| Synergy | Rarity | Trigger | Effect |
|---------|--------|---------|--------|
| **Clean Sheet** | common | GK DEF + CB DEF ≥ 18 | +20 chips to both |
| **Organised Defence** | common | CB DEF + CB DEF ≥ 18 | +20 chips to both CBs |
| **Wingback Overlap** | common | FB PAC + CM PAS ≥ 15 | +25 chips to both |
| **Overload** | common | 2+ same field position | +15 chips to each |
| **Stretch the Backline** | common | FB PAC + LW PAC ≥ 17 | ×1.5 mult to both |
| **Route One** | uncommon | CB PAS + ST PAC ≥ 14 | +30 chips to ST |
| **Battering Ram** | common | CB DEF + ST ATK ≥ 17 | +20 chips to both |
| **Defensive Duo** | uncommon | 2 highest DEF sum ≥ 18 | +25 chips to all |
| **Back Three** | rare | All 3 DEF ≥ 7 | ×1.3 mult to all |
| **Midfield Engine** | common | CM PAS + CM DEF ≥ 15 | +25 chips to both |
| **Double Pivot** | uncommon | 2 CMs PAS ≥ 17 | Next phase +40 to first attacker |
| **Trio** | rare | All 3 CMs PAS ≥ 7 | ×1.3/×1.5/×1.3 chain |
| **Set Piece Threat** | uncommon | DEF≥9 + SPC≥8 (diff) | +50 global chips |

## The 10 Persistent Synergies (squad-trait based, auto-checked at match start)

| Synergy | Rarity | Squad Check | Effect |
|---------|--------|-------------|--------|
| Pace in Behind | uncommon | 4+ pacey players | All pacey get ×1.1 mult |
| Iron Wall | uncommon | 3+ physical players | Fatigue ×0.8 instead of ×0.7 |
| Leadership Council | common | 3+ leaders | All players get +3 chips/phase |
| Tiki-Taka | uncommon | 3+ technical players | Midfielders get +5 chips/phase |
| Clinical Edge | common | 2+ clinical players | Attackers get +5 chips/phase |
| Double Destroyer | common | 2+ destroyers | Defenders get +5 chips/phase |
| Two Up Top | rare | 2+ poachers | STs get ×1.3 mult |
| Journeyman | rare | 1+ journeyman | Once per match: restore one player's fatigue |
| Pace & Power | rare | 2+ pacey+physical | Those players get ×1.3 mult |
| Silent Killers | uncommon | 2+ clinical+pacey | Those players get +5 chips/phase |

---

## Tips

- **Bonuses/penalties on formation screen**: Green = boost, Red = penalty. ⚠️ in fit reasons shows which players the formation hurts.
- **Per-round synergy re-roll**: Each round gets 5 fresh random phase synergies. Adapt your strategy.
- **6 random phases from 11**: No two rounds are the same. Build a versatile squad.
- **Cheap players** (15-19 cost) let you afford stars like Captain Stevie (36) or Toni Cruise (35)
- **Fatigue ×0.7 stacks** — a player used in 3 consecutive phases is at 34% effectiveness
- **Phase synergy display** shows which player(s) enabled each synergy and the rule threshold met

---

## Running Tests

```bash
cd ~/games/squad
source .venv/bin/activate
python3 -m pytest tests/ -v
```

107 tests covering phases, fatigue, stat-based slot eligibility, scoring formulas, all 13 phase synergies, all 10 persistent synergies, and main module display functions.
