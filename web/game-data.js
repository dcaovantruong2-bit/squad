/**
 * SQUAD — Game Engine (pure logic, no DOM)
 *
 * Shared game state + logic module loaded by ALL screens.
 * Pure JS, no external dependencies — works in a browser.
 *
 * ARCHITECTURE:
 *   game-engine.js  — Game state, data, scoring, synergy, campaign logic
 *   game-ui.js      — Rendering, event handlers, screen management
 *   game.html       — HTML screens + script loader
 *
 * CONTENTS:
 *   G                  — Global game state object
 *   PLAYERS            — 33-player roster with stats and traits
 *   CHIPS_FORMULA      — Position-specific stat-weight formulas
 *   FORMATIONS         — 6 formations with slot definitions and bonuses
 *   ALL_PHASES         — 8 tactical phases with slot definitions
 *   SYNERGIES          — Phase-level synergy definitions
 *   COMBO_CHAINS       — Phase tag sequence bonus effects
 *   POSITION_ADJACENCY — Out-of-position penalty mapping
 *   CAMPAIGN_MATCHES   — 5-match campaign config
 *   calculateChips()   getPositionPenalty()   detectSynergies()
 *   calculatePhaseScore()   checkRoundWin()   autoFillSquad()
 *   autoRecommendFormation()   dealPhases()   evaluateComboChains()
 *   applyFatigue()   recoverFatigue()   buyShopItem()
 *   resetRound()   saveGame()   loadGame()
 */

/* ===================================================================
   SECTION 1 — GLOBAL GAME STATE (G)
   =================================================================== */

var G = {
  // Screen routing (stale — set by engine but SPA shell uses Game._current() instead)
  currentScreen: 'title', // 'squad'|'formation'|'phases'|'match'|'phase-result'|'shop'|'round-result'|'campaign-complete'

  // Squad
  playerPool: [],    // all 33 players (populated on init)
  selectedIds: [],   // player IDs in squad (11-12)

  // Formation
  formation: null,   // formation id (e.g. '4-4-2')

  // Match state
  matchIdx: 0,       // current match (0-4)
  roundIdx: 0,       // current round (0-2)
  phaseIdx: 0,       // current phase (0-2)
  dealtPhases: [],   // all 8 phase ids (shuffled order for this round)
  pickedPhases: [],  // 3 picked phase ids (ordered, played in sequence)
  field: [],         // [{playerId, slotId}] — current phase placements

  // Scoring
  roundScore: 0,       // running round total
  phaseResults: [],    // [{phaseId, score, breakdown}]
  roundResults: [],    // [{roundIdx, score, target, won}]
  matchResults: [],    // [{matchIdx, opponent, roundsWon, roundsLost}]

  // Fatigue
  fatigue: {},         // {playerId: multiplier} 1.0 = fresh

  // Economy
  morale: 0,           // shop currency
  shopBuffs: [],       // active buffs [{id, effect, duration}]

  // Match-level modifiers (Python-compat, not yet wired in SPA flow)
  phaseFatigue: {},    // {phaseId: multiplier} — starts at 1.0, ×0.85 when reused in a match (Python feature)
  opponentAdjustments: {}, // {phaseId: multiplier} — scouting buffs/nerfs for this round (Python feature)

  // Campaign
  campaignWon: false,
  bestRun: {wins: 4, score: 4200000}
};

/* ===================================================================
   SECTION 2 — PLAYER DATA (33 players)
   =================================================================== */

var PLAYERS = [
  { id:"terry_henri", name:"Terry Henri", position:"ST", atk:9, pac:9, pas:6, def_:1, spc:8, traits:["pacey","clinical"], description:"The clinical speedster." },
  { id:"big_zlat", name:"Big Zlat", position:"ST", atk:8, pac:5, pas:7, def_:2, spc:10, traits:["physical","technical"], description:"Acrobatic target man." },
  { id:"kun_kun", name:"El Caníbal", position:"ST", atk:8, pac:8, pas:5, def_:1, spc:7, traits:["pacey","poacher"], description:"Low center of gravity." },
  { id:"the_waz", name:"The Waz", position:"ST", atk:8, pac:6, pas:7, def_:5, spc:6, traits:["physical","leader"], description:"Bulldog forward." },
  { id:"flash_forward", name:"Theo Walk-not", position:"ST", atk:5, pac:7, pas:2, def_:1, spc:3, traits:["pacey","poacher"], description:"All pace." },
  { id:"lewan_goalski", name:"Lewan-goal-ski", position:"ST", atk:9, pac:5, pas:2, def_:1, spc:5, traits:["poacher","clinical"], description:"Six-yard box." },
  { id:"rob_cutter", name:"Arjen Cutback", position:"RW", atk:8, pac:9, pas:6, def_:1, spc:8, traits:["pacey","clinical"], description:"Cut inside." },
  { id:"rabona_ron", name:"El Shaa-ra-wrong", position:"RW", atk:5, pac:6, pas:5, def_:1, spc:6, traits:["pacey","clinical"], description:"Fancy flicks." },
  { id:"riyad_mahrizzle", name:"Riyad Mah-rizzle", position:"RW", atk:7, pac:7, pas:8, def_:2, spc:9, traits:["technical","playmaker"], description:"Silky dribbler." },
  { id:"bale_out", name:"Bale Out", position:"LW", atk:8, pac:10, pas:6, def_:3, spc:7, traits:["pacey","physical"], description:"Pace AND power." },
  { id:"kylian_express", name:"Dictator Kylian", position:"LW", atk:7, pac:10, pas:5, def_:2, spc:7, traits:["pacey","clinical"], description:"Lightning." },
  { id:"cult_carl", name:"Wilfried Za-ha-ha", position:"LW", atk:5, pac:7, pas:5, def_:2, spc:3, traits:["pacey","clinical"], description:"Fans love him." },
  { id:"maestro_xav", name:"The Puppet Master", position:"CM", atk:3, pac:4, pas:10, def_:6, spc:7, traits:["playmaker","technical"], description:"Pulls the strings." },
  { id:"don_andres", name:"Don Andres", position:"CM", atk:6, pac:7, pas:9, def_:3, spc:10, traits:["technical","playmaker"], description:"Dribbling illusionist." },
  { id:"captain_stevie", name:"Captain Stevie", position:"CM", atk:8, pac:6, pas:8, def_:6, spc:8, traits:["leader","physical"], description:"Box-to-box." },
  { id:"jimmy_journey", name:"Park Ji-zoom", position:"CM", atk:3, pac:4, pas:7, def_:4, spc:2, traits:["physical","leader","journeyman"], description:"Does a job." },
  { id:"yaya_too_strong", name:"Yaya Too Strong", position:"CM", atk:4, pac:6, pas:5, def_:9, spc:4, traits:["destroyer","physical","leader"], description:"Towering." },
  { id:"el_mago", name:"Juan Maestro", position:"CAM", atk:6, pac:5, pas:10, def_:2, spc:9, traits:["technical","playmaker"], description:"Final third wizard." },
  { id:"mesut_assist", name:"Mesut Assist", position:"CAM", atk:6, pac:6, pas:9, def_:4, spc:7, traits:["playmaker","technical"], description:"Orchestrator." },
  { id:"bruno_penandes", name:"Bruno Penandes", position:"CAM", atk:8, pac:5, pas:8, def_:3, spc:10, traits:["playmaker","clinical"], description:"Stats monster." },
  { id:"wall_claude", name:"N'Golo Kanteen", position:"CDM", atk:2, pac:4, pas:6, def_:10, spc:3, traits:["destroyer","technical"], description:"The destroyer." },
  { id:"frenkie_de_con", name:"Toni Cruise", position:"CDM", atk:4, pac:7, pas:10, def_:7, spc:7, traits:["technical","playmaker"], description:"Deep-lying conductor." },
  { id:"bog_bob", name:"Nigel de Wrong", position:"CDM", atk:2, pac:4, pas:5, def_:7, spc:2, traits:["destroyer","physical"], description:"Dirty work." },
  { id:"il_capitano", name:"El Capitán", position:"CB", atk:3, pac:6, pas:7, def_:10, spc:5, traits:["leader","technical"], description:"Elegant reader." },
  { id:"jt_rock", name:"Campbell-Soup", position:"CB", atk:4, pac:3, pas:4, def_:10, spc:4, traits:["physical","aerial"], description:"Eats attackers." },
  { id:"rolls_royce", name:"The Rolls Royce", position:"CB", atk:2, pac:8, pas:6, def_:9, spc:6, traits:["technical","leader"], description:"Composed." },
  { id:"old_man_dan", name:"Per Merterslower", position:"CB", atk:2, pac:2, pas:5, def_:8, spc:2, traits:["leader","aerial"], description:"Reads the game." },
  { id:"el_tren", name:"Dani Elvis", position:"FB", atk:5, pac:9, pas:7, def_:7, spc:5, traits:["pacey","physical"], description:"Brazilian train." },
  { id:"mr_reliable", name:"Lahm-burger", position:"FB", atk:3, pac:7, pas:8, def_:9, spc:4, traits:["technical","leader"], description:"Two-footed." },
  { id:"cafu_express", name:"Kyle Jogger", position:"FB", atk:6, pac:10, pas:7, def_:6, spc:5, traits:["pacey","physical"], description:"Relentless." },
  { id:"the_crab", name:"The Tank", position:"FB", atk:2, pac:6, pas:4, def_:7, spc:1, traits:["destroyer","leader"], description:"Tank." },
  { id:"no_look_dave", name:"Dave", position:"FB", atk:3, pac:8, pas:7, def_:8, spc:5, traits:["technical","playmaker"], description:"No-look Dave." },
  { id:"gigi_wall", name:"Gigi The Wall", position:"GK", atk:1, pac:2, pas:4, def_:10, spc:8, traits:["leader","aerial"], description:"The Wall." },
  { id:"saint_lloris", name:"Saint Lloris", position:"GK", atk:1, pac:2, pas:3, def_:10, spc:5, traits:["leader","aerial"], description:"Lightning reflexes." },
  { id:"rocket_raya", name:"Rocket Raya", position:"GK", atk:1, pac:5, pas:8, def_:6, spc:8, traits:["playmaker","technical"], description:"Sweeper keeper." },
  { id:"claudio_bravoops", name:"Claudio Bra-voops", position:"GK", atk:1, pac:5, pas:4, def_:7, spc:3, traits:["leader","technical"], description:"Solid shot-stopper." },
];

// Helper: sum of all 5 stats = player cost
function calcCost(p) {
  return p.atk + p.pac + p.pas + p.def_ + p.spc;
}

// Add cost to each player
(function() {
  for (var i = 0; i < PLAYERS.length; i++) {
    PLAYERS[i].cost = calcCost(PLAYERS[i]);
  }
})();

// Populate G.playerPool on load
G.playerPool = PLAYERS.slice();

// V3-FIX: Add screen-format fields to every player
(function() {
  for (var i = 0; i < PLAYERS.length; i++) {
    var p = PLAYERS[i];
    p.pos = p.position;
    p.def = p.def_;
    p.ovr = Math.round((p.atk + p.pac + p.pas + p.def_ + p.spc) / 5);
    p.fatigue = 1.0;
  }
})();

/* ===================================================================
   SECTION 3 — CHIPS FORMULA (position-specific stat weights)
   =================================================================== */

var CHIPS_FORMULA = {
  GK:  function(p) { return Math.round(p.def_ * 3 + p.spc * 1); },
  CB:  function(p) { return Math.round(p.def_ * 3 + p.pac * 2 + p.atk * 1); },
  FB:  function(p) { return Math.round(p.def_ * 2 + p.pac * 3 + p.pas * 1); },
  CDM: function(p) { return Math.round(p.def_ * 2 + p.pas * 3 + p.atk * 1); },
  CM:  function(p) { return Math.round(p.pas * 3 + p.atk * 2 + p.def_ * 1); },
  CAM: function(p) { return Math.round(p.pas * 3 + p.atk * 2 + p.spc * 1); },
  LW:  function(p) { return Math.round(p.atk * 2 + p.pac * 3 + p.pas * 1); },
  RW:  function(p) { return Math.round(p.atk * 2 + p.pac * 3 + p.pas * 1); },
  ST:  function(p) { return Math.round(p.atk * 4 + p.pac * 2 + p.spc * 1); }
};

/* ===================================================================
   SECTION 4 — POSITION ADJACENCY (OOP penalties)
   =================================================================== */

var POSITION_ADJACENCY = {
  GK:  { natural:['GK'],                  adjacent:[],                                  different:['CB','FB','CDM','CM','CAM','LW','RW','ST'] },
  CB:  { natural:['CB'],                  adjacent:['FB','CDM'],                        different:['CM','CAM','LW','RW','ST'] },
  FB:  { natural:['FB'],                  adjacent:['CB','CDM','CM','LW','RW'],          different:['CAM','ST'] },
  CDM: { natural:['CDM'],                 adjacent:['CB','FB','CM','CAM'],               different:['LW','RW','ST'] },
  CM:  { natural:['CM'],                  adjacent:['CDM','CAM','FB'],                    different:['CB','LW','RW','ST'] },
  CAM: { natural:['CAM'],                 adjacent:['CM','ST','LW','RW'],                different:['CDM','CB','FB'] },
  LW:  { natural:['LW'],                  adjacent:['RW','ST','CAM','FB'],               different:['CM','CDM','CB'] },
  RW:  { natural:['RW'],                  adjacent:['LW','ST','CAM','FB'],               different:['CM','CDM','CB'] },
  ST:  { natural:['ST'],                  adjacent:['LW','RW','CAM'],                    different:['CM','CDM','CB','FB'] }
};

var TRAIT_SLOT_FIT = {
  'pacey':     ['LW','RW','ST','FB'],
  'clinical':  ['LW','RW','ST','CAM'],
  'technical': ['CM','CAM','CDM','CB'],
  'playmaker': ['CM','CAM','LW','RW'],
  'physical':  ['ST','CB','CDM','FB','CM'],
  'destroyer': ['CDM','CB','CM'],
  'aerial':    ['CB','ST','GK'],
  'poacher':   ['ST','LW','RW'],
  'leader':    ['CB','CM','GK']
};

/* ===================================================================
   SECTION 5 — FORMATIONS (6)
   Each formation defines outfield slots (GK is implicit).
   global = global multiplier for scoring.
   bonuses = position-specific chip bonuses (additive).
   =================================================================== */

var FORMATIONS = [
  { id:"4-4-2", name:"4-4-2", handSize:11, global:1.0,
    slots:["CB","CB","FB","FB","CM","CM","ST","ST"],
    bonuses:{}, description:"Balanced. No frills. Classic." },
  { id:"4-3-3", name:"4-3-3", handSize:11, global:1.05,
    slots:["CB","CB","FB","FB","CDM","CM","CM","LW","RW","ST"],
    bonuses:{LW:20,RW:20,ST:-15,CDM:-10}, description:"Attacking. Wingers thrive." },
  { id:"5-3-2", name:"5-3-2", handSize:11, global:0.95,
    slots:["CB","CB","CB","FB","FB","CM","CM","CDM","ST","ST"],
    bonuses:{CB:25,FB:12,LW:-20,RW:-20}, description:"Defence wins. CBs+25." },
  { id:"3-4-3", name:"3-4-3", handSize:11, global:1.08,
    slots:["CB","CB","CB","FB","FB","CM","CM","LW","ST","RW"],
    bonuses:{ST:20,LW:15,RW:15,CB:-25}, description:"All-out attack." },
  { id:"4-2-3-1", name:"4-2-3-1", handSize:11, global:1.02,
    slots:["CB","CB","FB","FB","CM","CM","CAM","LW","RW","ST"],
    bonuses:{CM:10,CAM:25,ST:-15}, description:"Possession. CAM+25." },
  { id:"4-5-1", name:"4-5-1", handSize:11, global:0.98,
    slots:["CB","CB","FB","FB","CDM","CM","CM","LW","RW","ST"],
    bonuses:{CDM:15,LW:20,RW:20,ST:-20,CB:-5}, description:"Counter. Wingers+20." }
];

/* ===================================================================
   SECTION 6 — PHASES (8 tactical focuses)
   Each phase has a weight (primary stat category), slots,
   and a description.
   =================================================================== */

var ALL_PHASES = [
  { id:"goal_kick",       name:"Goal Kick",     tag:"Defensive",   weight:"DEF", slots:["GK","CB","CB"], desc:"Keeper launches long — defenders win the header" },
  { id:"build_up",        name:"Build-Up",      tag:"Possession",  weight:"PAS", slots:["FB","FB","CM"], desc:"Play out from the back — fullbacks into midfield" },
  { id:"wide_attack",     name:"Wide Attack",   tag:"Attacking",   weight:"PAC", slots:["FB","LW","RW"], desc:"Overload the flanks — fullback supports wingers" },
  { id:"direct_play",     name:"Direct Play",   tag:"Transition",  weight:"ATK", slots:[["LW","RW"],"ST","CM"], desc:"Quick transition — bypass midfield" },
  { id:"defensive_block", name:"Defensive Block", tag:"Defensive", weight:"DEF", slots:["CB","CB","CDM"], desc:"Compact defensive shape — protect the centre" },
  { id:"tiki_taka",       name:"Tiki-Taka",     tag:"Possession",  weight:"PAS", slots:["CM","CM","CAM"], desc:"Pass, move, repeat — creative midfield control" },
  { id:"counter",         name:"Counter",       tag:"Transition",  weight:"PAC", slots:["LW","ST","RW"], desc:"Explosive break — pacey attackers in behind" },
  { id:"set_piece",       name:"Set Piece",     tag:"Specialist",  weight:"SPC", slots:["CAM","CB","ST"], desc:"Dead ball specialist — aerial threat" }
];

/* ===================================================================
   SECTION 7 — SYNERGIES (phase-level)
   =================================================================== */

var SYNERGIES = [
  // === Position-pair synergies ===
  { id:"clean_sheet",         name:"Clean Sheet",       tag:"defensive",  trigger:{posA:"GK",posB:"CB",stat:"def_",threshold:18},   effect:{chips:20},   description:"GK DEF + CB DEF ≥ 18: +20 chips" },
  { id:"organised_defence",   name:"Organised Defence", tag:"defensive",  trigger:{positions:["CB","CB"],stat:"def_",threshold:18},  effect:{chips:20},   description:"2 CBs DEF ≥ 18: +20 chips" },
  { id:"wingback_overlap",    name:"Wingback Overlap",  tag:"attacking",  trigger:{posA:"FB",statA:"pac",posB:"CM",statB:"pas",threshold:15}, effect:{chips:25}, description:"FB PAC + CM PAS ≥ 15: +25 chips" },
  { id:"overload",            name:"Overload",          tag:"attacking",  trigger:{minDuplicates:2},                                  effect:{addMult:15}, description:"2+ same position: +15 mult each" },
  { id:"stretch_backline",    name:"Stretch Backline",  tag:"attacking",  trigger:{posA:"FB",statA:"pac",posB:"LW",statB:"pac",threshold:17}, effect:{xMult:1.5}, description:"FB PAC + LW PAC ≥ 17: ×1.5 mult" },
  { id:"route_one",           name:"Route One",         tag:"transition", trigger:{posA:"CB",statA:"pas",posB:"ST",statB:"pac",threshold:14}, effect:{chips:30}, description:"CB PAS + ST PAC ≥ 14: +30 chips" },
  { id:"battering_ram",       name:"Battering Ram",     tag:"transition", trigger:{posA:"CB",statA:"def_",posB:"ST",statB:"atk",threshold:17}, effect:{chips:20}, description:"CB DEF + ST ATK ≥ 17: +20 chips" },
  { id:"defensive_duo",       name:"Defensive Duo",     tag:"defensive",  trigger:{stat:"def_",threshold:18},                         effect:{addMult:10}, description:"2 highest DEF ≥ 18: +10 add mult" },
  { id:"back_three",          name:"Back Three",        tag:"defensive",  trigger:{stat:"def_",threshold:7,count:3},                  effect:{xMult:1.3}, description:"All 3 DEF ≥ 7: ×1.3 mult" },
  { id:"midfield_engine",     name:"Midfield Engine",   tag:"possession", trigger:{positions:["CM","CM"],statA:"pas",statB:"def_",threshold:15}, effect:{addMult:10}, description:"CM PAS + CM DEF ≥ 15: +10 add mult" },
  { id:"double_pivot",        name:"Double Pivot",      tag:"possession", trigger:{positions:["CM","CM"],stat:"pas",threshold:17},    effect:{carryover:40}, description:"2 CMs PAS ≥ 17: carryover +40 chips next phase" },
  { id:"covering_defender",   name:"Covering Defender", tag:"defensive",  trigger:{position:"CB",statA:"pac",thresholdA:7,statB:"def_",thresholdB:9}, effect:{addMult:10}, description:"Fast CB + strong CB: +10 add mult" },
  { id:"target_man_release",  name:"Target Man Release",tag:"attacking",  trigger:{posA:"ST",statA:"atk",wingerPos:["LW","RW"],statB:"pac",threshold:17}, effect:{xMult:1.5}, description:"ST ATK + winger PAC ≥ 17: ×1.5 mult" },
  { id:"near_post_flick",     name:"Near Post Flick",   tag:"attacking",  trigger:{posA:"CAM",statA:"spc",posB:"ST",statB:"atk",threshold:16}, effect:{xMult:1.5}, description:"CAM SPC + ST ATK ≥ 16: ×1.5 mult" },
  { id:"one_two",             name:"One-Two",           tag:"possession", trigger:{posA:"CM",statA:"pas",posB:"ST",statB:"pac",threshold:15}, effect:{xMult:1.5}, description:"CM PAS + ST PAC ≥ 15: ×1.5 mult" },
  { id:"overlap",             name:"Overlap",           tag:"attacking",  trigger:{posA:"FB",statA:"pac",posB:"LW",statB:"pas",threshold:15}, effect:{xMult:1.5}, description:"FB PAC + LW PAS ≥ 15: ×1.5 mult" },
  { id:"set_piece_threat",    name:"Set Piece Threat",  tag:"specialist", trigger:{statA:"def_",thresholdA:8,statB:"spc",thresholdB:7}, effect:{chips:35}, description:"DEF≥8 + SPC≥7: +35 chips" },
  { id:"trio",                name:"Trio",              tag:"possession", trigger:{position:"CM",stat:"pas",threshold:7,count:3}, effect:{xMult:2.535}, description:"3 CMs PAS ≥ 7: ×2.535 mult" },

  // === Persistent squad synergies (trait-count based) ===
  { id:"pace_in_behind",      name:"Pace in Behind",    persistent:true, trigger:{trait:"pacey",minCount:5},    effect:{playerMult:1.15,targetTrait:"pacey"},   description:"5+ pacey: all pacey ×1.15 per phase" },
  { id:"iron_wall",           name:"Iron Wall",         persistent:true, trigger:{trait:"physical",minCount:3},  effect:{playerMult:1.2,targetTrait:"physical"}, description:"3+ physical: ×1.2 mult" },
  { id:"leadership_council",  name:"Leadership Council",persistent:true, trigger:{trait:"leader",minCount:3},    effect:{addChips:15,target:"all"},              description:"3+ leaders: all get +15 chips per phase" },
  { id:"tiki_taka_persistent",name:"Tiki-Taka",         persistent:true, trigger:{trait:"technical",minCount:3}, effect:{positionMult:1.15,targetPositions:["CM","CDM","CAM"]}, description:"3+ technical: midfielders ×1.15" },
  { id:"clinical_edge",       name:"Clinical Edge",     persistent:true, trigger:{trait:"clinical",minCount:2},  effect:{addChips:15,targetPositions:["LW","RW","ST"]}, description:"2+ clinical: attackers +15 chips" },
  { id:"double_destroyer",    name:"Double Destroyer",  persistent:true, trigger:{trait:"destroyer",minCount:2}, effect:{positionMult:1.2,targetPositions:["CB","FB","CDM"]}, description:"2+ destroyers: defenders ×1.2" },
  { id:"two_up_top",          name:"Two Up Top",        persistent:true, trigger:{trait:"poacher",minCount:2},   effect:{positionMult:1.3,targetPositions:["ST"]}, description:"2+ poachers: STs ×1.3" },
  { id:"playmaker_network",   name:"Playmaker Network", persistent:true, trigger:{trait:"playmaker",minCount:3}, effect:{positionMult:1.15,targetPositions:["CM","CAM","CDM"]}, description:"3+ playmakers: midfield ×1.15" },
  { id:"aerial_fortress",     name:"Aerial Fortress",   persistent:true, trigger:{trait:"aerial",minCount:3},    effect:{positionMult:1.2,targetPositions:["ST","CB","GK"]}, description:"3+ aerial: ST/CB/GK ×1.2" },
  { id:"pace_and_power",      name:"Pace & Power",      persistent:true, trigger:{traits:["pacey","physical"],minCount:2}, effect:{playerMult:1.3,targetTrait:"pacey"}, description:"2+ pacey+physical: ×1.3" },
  { id:"silent_killers",      name:"Silent Killers",    persistent:true, trigger:{traits:["clinical","pacey"],minCount:2}, effect:{playerMult:1.25,targetTrait:"clinical"}, description:"2+ clinical+pacey: ×1.25" },
  { id:"journeyman",          name:"Journeyman",        persistent:true, trigger:{trait:"journeyman",minCount:1}, effect:{special:"fatigue_reset"}, description:"Journeyman: once-per-match fatigue reset" },
];

/* ===================================================================
   SECTION 8 — COMBO CHAINS (phase tag sequence bonuses)
   Key format: "PrevTag_NextTag"
   =================================================================== */

var COMBO_CHAINS = {
  'Defensive_Transition':    { effect:'xMult', value:1.5, desc:'Absorb pressure, hit on break — ×1.5' },
  'Possession_Attacking':    { effect:'xMult', value:1.3, desc:'Switch of play — patient build to incision ×1.3' },
  'Possession_Possession':   { effect:'addChips', value:25, desc:'Keep the ball — wear them down +25 chips' },
  'Transition_Transition':   { effect:'addChips', value:35, desc:'Rapid succession — no time to reset +35 chips' },
  'Defensive_Defensive':     { effect:'fatigueRecovery', value:0.1, desc:'Rest while defending — fatigue recovery 0.1' },
  'Specialist_Any':          { effect:'addChips', value:30, desc:'Set piece leads to a chance — +30 chips carryover' },
  'Attacking_Defensive':     { effect:'oppPenalty', value:0.9, desc:'Suck them in, then hold firm — opp ×0.9' },
  'Possession_Transition':   { effect:'xMult', value:1.2, desc:'Unexpected speed shift — ×1.2' },
};

/* ===================================================================
   SECTION 9 — CAMPAIGN (5 matches)
   Each match has a name, opponent, and 3 round targets
   (round 0, 1, 2 must be met to win the round).
   =================================================================== */

var CAMPAIGN_MATCHES = [
  { name:"Group Stage",          opponent:"Wolves FC",            targets:[4000,6500,9000], tier:"Match 1/5", intro:"Relegation battlers. Forwards can't finish — exploit set pieces." },
  { name:"Round of 16",         opponent:"Inter Your-Nan",       targets:[5000,7500,10000], tier:"Match 2/5", intro:"Mid-table side. Solid defence but slow at the back." },
  { name:"Quarter Final",       opponent:"Borussia Mönchen-flapjack", targets:[6000,8500,11500], tier:"Match 3/5", intro:"European contenders. Press hard." },
  { name:"Semi Final",          opponent:"Man City Oilers",      targets:[7000,10000,13500], tier:"Match 4/5", intro:"Title favourites. No obvious weakness." },
  { name:"THE FINAL",           opponent:"Galácticos FC",        targets:[8500,12000,16000], tier:"Match 5/5", intro:"The best in the world. Leave nothing on the pitch." },
];


var ATTACKER_POSITIONS = { LW: true, RW: true, ST: true, CAM: true };
var SHOP_ITEMS = {
  'energy_drink':     { name:"Energy Drink",      cost:2, effect:{type:'fullReset', value:1},       desc:"Restore one player's fatigue to 100%" },
  'tactical_upgrade': { name:"Tactical Upgrade",  cost:3, effect:{type:'placeholder', value:1},      desc:"+1 to a chosen stat on one player" },
  'set_piece_drill':  { name:"Set Piece Drill",   cost:4, effect:{type:'chipsBuff', value:40},       desc:"Next round: all phases get +40 chips" },
  'super_sub':        { name:"Super Sub",         cost:2, effect:{type:'superSub', value:1.3},       desc:"Next round: fresh player gets ×1.3" },
  'tactical_shift':   { name:"Tactical Shift",    cost:5, effect:{type:'addMultBuff', value:5},      desc:"Next round: +5 add_mult on all phases" },
  'formation_tweak':  { name:"Formation Tweak",   cost:3, effect:{type:'formMult', value:0.05},      desc:"+0.05 formation mult for next match" },
  'momentum_injector':{ name:"Momentum Injector", cost:4, effect:{type:'momentumBoost', value:1.5},  desc:"Next phase starts at ×1.5 momentum" },
  'scout_report':     { name:"Scout Report",      cost:2, effect:{type:'scout', value:1},            desc:"See all 8 phases this round" },
  'double_session':   { name:"Double Training Session", cost:4, effect:{type:'fatiguePenalty', value:0.8}, desc:"This round fatigue penalty ×0.8 instead of ×0.7" },
  'morale_boost':     { name:"Morale Boost",      cost:1, effect:{type:'morale', value:5},           desc:"+5 morale" },
};

