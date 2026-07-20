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
  // Screen routing
  currentScreen: 'title', // 'title'|'squad'|'formation'|'phases'|'match'|'phase-result'|'shop'|'round-result'|'campaign-complete'

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

  // Match-level modifiers
  phaseFatigue: {},    // {phaseId: multiplier} — starts at 1.0, ×0.85 when reused in a match
  opponentAdjustments: {}, // {phaseId: multiplier} — scouting buffs/nerfs for this round

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
  { name:"Group Stage",          opponent:"Wolves FC",            targets:[400,650,900], tier:"Match 1/5", intro:"Relegation battlers. Forwards can't finish — exploit set pieces." },
  { name:"Round of 16",         opponent:"Inter Your-Nan",       targets:[450,700,950], tier:"Match 2/5", intro:"Mid-table side. Solid defence but slow at the back." },
  { name:"Quarter Final",       opponent:"Borussia Mönchen-flapjack", targets:[550,800,1100], tier:"Match 3/5", intro:"European contenders. Press hard." },
  { name:"Semi Final",          opponent:"Man City Oilers",      targets:[650,950,1300], tier:"Match 4/5", intro:"Title favourites. No obvious weakness." },
  { name:"THE FINAL",           opponent:"Galácticos FC",        targets:[800,1150,1500], tier:"Match 5/5", intro:"The best in the world. Leave nothing on the pitch." },
];

/* ===================================================================
   SECTION 10 — CORE FUNCTIONS
   =================================================================== */

// --- Utility: get player by id ---
function getPlayerById(id) {
  for (var i = 0; i < PLAYERS.length; i++) {
    if (PLAYERS[i].id === id) return PLAYERS[i];
  }
  return null;
}

// --- get squad player objects from selectedIds ---
function getSquad() {
  var squad = [];
  for (var i = 0; i < G.selectedIds.length; i++) {
    var p = getPlayerById(G.selectedIds[i]);
    if (p) squad.push(p);
  }
  return squad;
}

// --- Resolve a slot spec to a field position string ---
function resolveSlot(slotSpec) {
  if (typeof slotSpec === 'string') return slotSpec;
  if (Array.isArray(slotSpec)) return slotSpec[0]; // first = primary
  return 'ST';
}

// --- resolve field position for a player in a given slot ---
function slotFieldPosition(slot) {
  return resolveSlot(slot);
}

/**
 * calculateChips(playerId, fieldPosition)
 * Returns base chips for a player in a given field position.
 * Uses CHIPS_FORMULA for the position.
 */
function calculateChips(playerId, fieldPosition) {
  var player = (typeof playerId === 'object') ? playerId : getPlayerById(playerId);
  if (!player) return 0;
  var fn = CHIPS_FORMULA[fieldPosition];
  if (!fn) {
    // Fallback: average all stats
    return Math.round((player.atk + player.pac + player.pas + player.def_ + player.spc) * 2);
  }
  return fn(player);
}

/**
 * getPositionPenalty(playerId, fieldPosition)
 * Returns a multiplier (0–1) for OOP penalty:
 *   natural = 1.0, adjacent = 0.85, different = 0.70
 * Trait fit bonuses add 0.10 per matching trait (capped at 0.95).
 * Key stat ≥9 adds 0.05.
 */
function getPositionPenalty(playerId, fieldPosition) {
  var player = (typeof playerId === 'object') ? playerId : getPlayerById(playerId);
  if (!player) return 0.7;
  var playerPos = player.position;

  // GK can only play GK, GK can only be played by GK
  if (playerPos === 'GK' && fieldPosition === 'GK') return 1.0;
  if (playerPos === 'GK' || fieldPosition === 'GK') return 0.0;

  var adj = POSITION_ADJACENCY[playerPos];
  if (!adj) return 0.7;

  // Natural position
  if (playerPos === fieldPosition || adj.natural.indexOf(fieldPosition) >= 0) return 1.0;

  // Base penalty
  var base = (adj.adjacent.indexOf(fieldPosition) >= 0) ? 0.85 : 0.70;

  // Trait fit bonuses: each matching trait adds 0.10
  var bonus = 0;
  if (player.traits && player.traits.length) {
    for (var ti = 0; ti < player.traits.length; ti++) {
      var t = player.traits[ti];
      var fits = TRAIT_SLOT_FIT[t];
      if (fits && fits.indexOf(fieldPosition) >= 0) bonus += 0.10;
    }
  }

  // Key stat ≥ 9 bonus
  var statMap = {
    'GK':  'def_', 'CB': 'def_', 'FB': 'def_', 'CDM': 'def_',
    'CM':  'pas',  'CAM':'pas',  'LW': 'pac',  'RW':  'pac',
    'ST':  'atk'
  };
  var keyStat = statMap[fieldPosition];
  if (keyStat && player[keyStat] !== undefined && player[keyStat] >= 9) bonus += 0.05;

  return Math.min(base + bonus, 0.95);
}

/**
 * detectSynergies(field)
 * field = [{player, position}, ...] where player is a player object
 * Returns { fired:[], chips:0, addMult:0, xMult:1, carryover:0, details:[] }
 */
function detectSynergies(field) {
  var result = {
    fired: [],
    chips: 0,
    addMult: 0,
    xMult: 1,
    carryover: 0,
    details: []
  };

  // Filter out persistent synergies (handled separately)
  var phaseSyns = [];
  for (var si = 0; si < SYNERGIES.length; si++) {
    if (!SYNERGIES[si].persistent) phaseSyns.push(SYNERGIES[si]);
  }

  for (var si = 0; si < phaseSyns.length; si++) {
    var syn = phaseSyns[si];
    var tr = syn.trigger;
    var eff = syn.effect;
    var contributors = [];
    var fired = false;

    function addContrib(p) {
      if (contributors.indexOf(p.name) < 0) contributors.push(p.name);
    }

    // --- Clean Sheet: GK DEF + CB DEF ≥ threshold ---
    if (syn.id === 'clean_sheet') {
      var gk = null, cb = null;
      for (var fi = 0; fi < field.length; fi++) {
        var p = field[fi][0], pos = field[fi][1];
        if (pos === 'GK') gk = p;
        if (pos === 'CB') cb = p;
      }
      if (gk && cb && (gk.def_ + cb.def_ >= tr.threshold)) {
        addContrib(gk); addContrib(cb);
        fired = true;
      }
    }

    // --- Organised Defence: 2 CBs DEF sum ≥ threshold ---
    else if (syn.id === 'organised_defence') {
      var cbs = [];
      for (var fi = 0; fi < field.length; fi++) {
        if (field[fi][1] === 'CB') cbs.push(field[fi][0]);
      }
      if (cbs.length >= 2) {
        cbs.sort(function(a,b) { return b.def_ - a.def_; });
        if (cbs[0].def_ + cbs[1].def_ >= tr.threshold) {
          addContrib(cbs[0]); addContrib(cbs[1]);
          fired = true;
        }
      }
    }

    // --- Wingback Overlap: FB PAC + CM PAS ≥ threshold ---
    else if (syn.id === 'wingback_overlap') {
      var fb = null, cm = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'FB') fb = field[fi][0];
        if (pos === 'CM') cm = field[fi][0];
      }
      if (fb && cm && (fb.pac + cm.pas >= tr.threshold)) {
        addContrib(fb); addContrib(cm);
        fired = true;
      }
    }

    // --- Overload: 2+ of same position on field ---
    else if (syn.id === 'overload') {
      var posCount = {};
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (!posCount[pos]) posCount[pos] = [];
        posCount[pos].push(field[fi][0]);
      }
      var minDup = tr.minDuplicates || 2;
      for (var pk in posCount) {
        if (posCount[pk].length >= minDup) {
          for (var ci = 0; ci < posCount[pk].length; ci++) addContrib(posCount[pk][ci]);
          fired = true;
        }
      }
    }

    // --- Stretch Backline: FB PAC + LW PAC ≥ threshold ---
    else if (syn.id === 'stretch_backline') {
      var fb = null, lw = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'FB') fb = field[fi][0];
        if (pos === 'LW') lw = field[fi][0];
      }
      if (fb && lw && (fb.pac + lw.pac >= tr.threshold)) {
        addContrib(fb); addContrib(lw);
        fired = true;
      }
    }

    // --- Route One: CB PAS + ST PAC ≥ threshold ---
    else if (syn.id === 'route_one') {
      var cb = null, st = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'CB') cb = field[fi][0];
        if (pos === 'ST') st = field[fi][0];
      }
      if (cb && st && (cb.pas + st.pac >= tr.threshold)) {
        addContrib(cb); addContrib(st);
        fired = true;
      }
    }

    // --- Battering Ram: CB DEF + ST ATK ≥ threshold ---
    else if (syn.id === 'battering_ram') {
      var cb = null, st = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'CB') cb = field[fi][0];
        if (pos === 'ST') st = field[fi][0];
      }
      if (cb && st && (cb.def_ + st.atk >= tr.threshold)) {
        addContrib(cb); addContrib(st);
        fired = true;
      }
    }

    // --- Defensive Duo: 2 highest DEF on field sum ≥ threshold ---
    else if (syn.id === 'defensive_duo') {
      var sorted = field.slice().sort(function(a,b) { return b[0].def_ - a[0].def_; });
      if (sorted.length >= 2 && sorted[0][0].def_ + sorted[1][0].def_ >= tr.threshold) {
        addContrib(sorted[0][0]); addContrib(sorted[1][0]);
        fired = true;
      }
    }

    // --- Back Three: All 3 on field have DEF ≥ threshold ---
    else if (syn.id === 'back_three') {
      var defPlayers = [];
      for (var fi = 0; fi < field.length; fi++) {
        defPlayers.push(field[fi][0]);
      }
      if (defPlayers.length >= (tr.count || 3)) {
        var allMet = true;
        for (var di = 0; di < (tr.count || 3); di++) {
          if (defPlayers[di].def_ < tr.threshold) { allMet = false; break; }
        }
        if (allMet) {
          for (var di = 0; di < (tr.count || 3); di++) addContrib(defPlayers[di]);
          fired = true;
        }
      }
    }

    // --- Midfield Engine: CM PAS + CM DEF ≥ threshold ---
    else if (syn.id === 'midfield_engine') {
      var cms = [];
      for (var fi = 0; fi < field.length; fi++) {
        if (field[fi][1] === 'CM') cms.push(field[fi][0]);
      }
      if (cms.length >= 2) {
        var sortedPas = cms.slice().sort(function(a,b) { return b.pas - a.pas; });
        var bestPas = sortedPas[0];
        var remaining = cms.filter(function(p) { return p.id !== bestPas.id; });
        var bestDef = remaining.slice().sort(function(a,b) { return b.def_ - a.def_; })[0];
        if (bestDef && bestPas.pas + bestDef.def_ >= tr.threshold) {
          addContrib(bestPas); addContrib(bestDef);
          fired = true;
        }
      }
    }

    // --- Double Pivot: 2 CMs PAS sum ≥ threshold, carryover to next phase ---
    else if (syn.id === 'double_pivot') {
      var cms = [];
      for (var fi = 0; fi < field.length; fi++) {
        if (field[fi][1] === 'CM') cms.push(field[fi][0]);
      }
      if (cms.length >= 2) {
        cms.sort(function(a,b) { return b.pas - a.pas; });
        if (cms[0].pas + cms[1].pas >= tr.threshold) {
          addContrib(cms[0]); addContrib(cms[1]);
          result.carryover += (eff.carryover || 40);
          result.details.push({
            name: syn.name,
            type: 'carryover',
            value: eff.carryover || 40,
            contributors: contributors.slice()
          });
          fired = true;
        }
      }
    }

    // --- Covering Defender: fast CB + different strong CB ---
    else if (syn.id === 'covering_defender') {
      var cbs = [];
      for (var fi = 0; fi < field.length; fi++) {
        if (field[fi][1] === 'CB') cbs.push(field[fi][0]);
      }
      var pacCb = null, defCb = null;
      for (var ci = 0; ci < cbs.length; ci++) {
        if (!pacCb && cbs[ci].pac >= tr.thresholdA) pacCb = cbs[ci];
        if (!defCb && cbs[ci].def_ >= tr.thresholdB) defCb = cbs[ci];
      }
      if (pacCb && defCb && pacCb.id !== defCb.id) {
        addContrib(pacCb);
        addContrib(defCb);
        fired = true;
      }
    }

    // --- Target Man Release: ST ATK + winger PAC ≥ threshold ---
    else if (syn.id === 'target_man_release') {
      var st = null, winger = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'ST') st = field[fi][0];
        if (pos === 'LW' || pos === 'RW') winger = field[fi][0];
      }
      if (st && winger && (st.atk + winger.pac >= tr.threshold)) {
        addContrib(st); addContrib(winger);
        fired = true;
      }
    }

    // --- Near Post Flick: CAM SPC + ST ATK ≥ threshold ---
    else if (syn.id === 'near_post_flick') {
      var cam = null, st = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'CAM') cam = field[fi][0];
        if (pos === 'ST') st = field[fi][0];
      }
      if (cam && st && (cam.spc + st.atk >= tr.threshold)) {
        addContrib(cam); addContrib(st);
        fired = true;
      }
    }

    // --- One-Two: CM PAS + ST PAC ≥ threshold ---
    else if (syn.id === 'one_two') {
      var cm = null, st = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'CM') cm = field[fi][0];
        if (pos === 'ST') st = field[fi][0];
      }
      if (cm && st && (cm.pas + st.pac >= tr.threshold)) {
        addContrib(cm); addContrib(st);
        fired = true;
      }
    }

    // --- Overlap: FB PAC + LW PAS ≥ threshold ---
    else if (syn.id === 'overlap') {
      var fb = null, lw = null;
      for (var fi = 0; fi < field.length; fi++) {
        var pos = field[fi][1];
        if (pos === 'FB') fb = field[fi][0];
        if (pos === 'LW') lw = field[fi][0];
      }
      if (fb && lw && (fb.pac + lw.pas >= tr.threshold)) {
        addContrib(fb); addContrib(lw);
        fired = true;
      }
    }

    // --- Set Piece Threat: needs DEF≥8 and SPC≥7 on different players ---
    else if (syn.id === 'set_piece_threat') {
      var defHi = [], spcHi = [];
      for (var fi = 0; fi < field.length; fi++) {
        var p = field[fi][0];
        if (p.def_ >= tr.thresholdA) defHi.push(p);
        if (p.spc >= tr.thresholdB) spcHi.push(p);
      }
      // Need at least one DEF≥8 and one SPC≥7 on different players
      if (defHi.length > 0 && spcHi.length > 0) {
        var matched = false;
        for (var di = 0; di < defHi.length; di++) {
          for (var spi = 0; spi < spcHi.length; spi++) {
            if (defHi[di].id !== spcHi[spi].id) {
              addContrib(defHi[di]);
              addContrib(spcHi[spi]);
              fired = true;
              matched = true;
              break;
            }
          }
          if (matched) break;
        }
      }
    }

    // Apply effect if fired
    if (fired) {
      result.fired.push(syn.name);
      var effChips = eff.chips || 0;
      var effAddMult = eff.addMult || 0;
      var effXMult = eff.xMult || 1;

      if (effChips > 0) {
        result.chips += effChips;
        result.details.push({
          name: syn.name,
          type: 'chips',
          value: effChips,
          contributors: contributors.slice()
        });
      }
      if (effAddMult > 0) {
        result.addMult += effAddMult;
        result.details.push({
          name: syn.name,
          type: 'addMult',
          value: effAddMult,
          contributors: contributors.slice()
        });
      }
      if (effXMult > 1) {
        result.xMult *= effXMult;
        result.details.push({
          name: syn.name,
          type: 'xMult',
          value: effXMult,
          contributors: contributors.slice()
        });
      }
    }
  }

  return result;
}

/**
 * detectSquadSynergies(squad)
 * squad = array of player objects
 * Returns persistent buffs object: { playerMult, playerAdd, positionMult, positionAdd,
 *   globalMult, globalAdd, firedSynergies }
 */
function detectSquadSynergies(squad) {
  var buffs = {
    playerMult: {},
    playerAdd: {},
    positionMult: {},
    positionAdd: {},
    globalMult: 1.0,
    globalAdd: 0,
    fatiguePenalty: 0.7,
    firedSynergies: [],
    journeymanAvailable: false
  };

  var traitToPlayers = {};
  for (var pi = 0; pi < squad.length; pi++) {
    var p = squad[pi];
    for (var ti = 0; ti < p.traits.length; ti++) {
      var t = p.traits[ti];
      if (!traitToPlayers[t]) traitToPlayers[t] = [];
      traitToPlayers[t].push(p);
    }
  }

  // Only persistent synergies
  for (var si = 0; si < SYNERGIES.length; si++) {
    var syn = SYNERGIES[si];
    if (!syn.persistent) continue;

    var tr = syn.trigger;
    var eff = syn.effect;
    var matching = [];

    // Check trigger conditions
    if (tr.trait && tr.minCount) {
      var m = traitToPlayers[tr.trait] || [];
      if (m.length >= tr.minCount) matching = m;
    } else if (tr.traits && tr.minCount) {
      // Combo trait: players with ALL specified traits
      for (var pi = 0; pi < squad.length; pi++) {
        var p = squad[pi];
        var hasAll = true;
        for (var ti = 0; ti < tr.traits.length; ti++) {
          if (p.traits.indexOf(tr.traits[ti]) < 0) { hasAll = false; break; }
        }
        if (hasAll) matching.push(p);
      }
      if (matching.length < (tr.minCount || 1)) matching = [];
    } else if (tr.trait && tr.minCount === undefined) {
      // Trait present (e.g. journeyman)
      var m = traitToPlayers[tr.trait] || [];
      if (m.length > 0) matching = m;
    }

    if (matching.length === 0) continue;

    buffs.firedSynergies.push(syn.name);

    // Apply effect
    if (eff.playerMult) {
      var mult = eff.playerMult;
      if (eff.targetTrait) {
        for (var pi = 0; pi < squad.length; pi++) {
          var p = squad[pi];
          if (p.traits.indexOf(eff.targetTrait) >= 0) {
            buffs.playerMult[p.id] = (buffs.playerMult[p.id] || 1.0) * mult;
          }
        }
      }
    }

    if (eff.positionMult) {
      var mult = eff.positionMult;
      if (eff.targetPositions) {
        for (var ti = 0; ti < eff.targetPositions.length; ti++) {
          var pos = eff.targetPositions[ti];
          buffs.positionMult[pos] = (buffs.positionMult[pos] || 1.0) * mult;
        }
      }
    }

    if (eff.addChips) {
      var chips = eff.addChips;
      if (eff.target === 'all') {
        buffs.globalAdd += chips;
      } else if (eff.targetPositions) {
        for (var ti = 0; ti < eff.targetPositions.length; ti++) {
          var pos = eff.targetPositions[ti];
          buffs.positionAdd[pos] = (buffs.positionAdd[pos] || 0) + chips;
        }
      }
    }

    if (eff.special === 'fatigue_reset') {
      buffs.journeymanAvailable = true;
    }

    if (syn.id === 'iron_wall') {
      buffs.fatiguePenalty = 0.6;
    }
  }

  return buffs;
}

/**
 * ATTACKER_POSITIONS set for carryover targeting
 */
var ATTACKER_POSITIONS = { LW: true, RW: true, ST: true, CAM: true };

/**
 * calculatePhaseScore(field, phaseId)
 * field = [{playerId, slotId}] — current phase placements
 * phaseId = the phase being played
 * Returns { score, breakdown, synergies }
 *
 * FINAL = (chips + synergy_chips) × (1 + add_mult) × x_mult × formation_mult × momentum × fatigue_avg
 */
function calculatePhaseScore(field, phaseId) {
  // Resolve field from playerIds to player objects
  var resolvedField = [];
  for (var fi = 0; fi < field.length; fi++) {
    var player = (typeof field[fi].playerId === 'object')
      ? field[fi].playerId
      : getPlayerById(field[fi].playerId);
    if (player) {
      resolvedField.push([player, field[fi].slotId]);
    }
  }

  if (resolvedField.length === 0) {
    return { score: 0, breakdown: [], synergies: { chips:0, addMult:0, xMult:1 }, phaseMult:1.0 };
  }

  // Get formation
  var formation = null;
  if (G.formation) {
    for (var fi = 0; fi < FORMATIONS.length; fi++) {
      if (FORMATIONS[fi].id === G.formation) { formation = FORMATIONS[fi]; break; }
    }
  }

  // Get persistent squad buffs
  var squad = getSquad();
  var persistentBuffs = detectSquadSynergies(squad);

  // Calculate per-player chips (match Python: no globalAdd per player, no fatigue double-count)
  var totalChips = 0;
  var breakdown = [];

  for (var fi = 0; fi < resolvedField.length; fi++) {
    var player = resolvedField[fi][0];
    var pos = resolvedField[fi][1];

    var baseChips = calculateChips(player, pos);
    var formBonus = 0;
    if (formation && formation.bonuses && formation.bonuses[pos]) {
      formBonus = formation.bonuses[pos];
    }

    var ppMult = persistentBuffs.playerMult[player.id] || 1.0;
    var ppAdd = persistentBuffs.playerAdd[player.id] || 0;
    var posMult = persistentBuffs.positionMult[pos] || 1.0;
    var posAdd = persistentBuffs.positionAdd[pos] || 0;
    var fatigue = G.fatigue[player.id] !== undefined ? G.fatigue[player.id] : 1.0;
    var oop = getPositionPenalty(player, pos);

    var effective = Math.round(
      (baseChips + formBonus + posAdd + ppAdd) * fatigue * oop * ppMult * posMult
    );

    totalChips += effective;

    breakdown.push({
      playerId: player.id,
      playerName: player.name,
      position: pos,
      baseChips: baseChips,
      formBonus: formBonus,
      fatigue: fatigue,
      oopPenalty: oop,
      persMult: ppMult * posMult,
      persAdd: ppAdd + posAdd,
      subtotal: effective
    });
  }

  var synResult = detectSynergies(resolvedField);
  var synChips = synResult.chips || 0;
  var addMult = synResult.addMult || 0;
  var xMult = synResult.xMult || 1;
  var carryover = synResult.carryover || 0;

  var momentumValues = [1.0, 1.2, 1.5];
  var momentum = momentumValues[G.phaseIdx] || 1.0;
  var formationMult = formation ? formation.global : 1.0;

  var phaseMult = 1.0;
  if (G.pickedPhases.length > G.phaseIdx && G.phaseIdx > 0) {
    var prevPhaseId = G.pickedPhases[G.phaseIdx - 1];
    var currPhaseId = G.pickedPhases[G.phaseIdx];
    var prevPhase = null, currPhase = null;
    for (var pi = 0; pi < ALL_PHASES.length; pi++) {
      if (ALL_PHASES[pi].id === prevPhaseId) prevPhase = ALL_PHASES[pi];
      if (ALL_PHASES[pi].id === currPhaseId) currPhase = ALL_PHASES[pi];
    }
    if (prevPhase && currPhase) {
      var chainKey = prevPhase.tag + '_' + currPhase.tag;
      var chainFallback = 'Specialist_Any';
      var chain = COMBO_CHAINS[chainKey];
      if (!chain && prevPhase.tag === 'Specialist') {
        chain = COMBO_CHAINS[chainFallback];
      }
      if (chain) {
        if (chain.effect === 'xMult') {
          phaseMult = chain.value;
        } else if (chain.effect === 'addChips') {
          synChips += chain.value;
          synResult.details.push({
            name: 'Combo: ' + chain.desc,
            type: 'combo_chips',
            value: chain.value,
            contributors: []
          });
        }
      }
    }
  }

  var persistentChips = persistentBuffs.globalAdd || 0;
  var persistentXMult = persistentBuffs.globalMult || 1.0;
  var totalBeforeMult = totalChips + synChips + carryover + persistentChips;
  var totalAddMult = 1 + addMult;
  var totalXMult = xMult * persistentXMult;
  var finalScore = Math.round(totalBeforeMult * totalAddMult * totalXMult * formationMult * momentum * phaseMult);

  return {
    score: finalScore,
    playerChips: totalChips,
    synergyChips: synChips,
    carryoverChips: carryover,
    totalBeforeMult: totalBeforeMult,
    addMult: totalAddMult,
    xMult: totalXMult,
    formationMult: formationMult,
    momentum: momentum,
    fatigueAvg: null,
    phaseMult: phaseMult,
    breakdown: breakdown,
    synergies: synResult,
    persistentBuffs: persistentBuffs.firedSynergies
  };
}

/**
 * checkRoundWin(score, target)
 * Returns boolean — did the player meet or exceed the target?
 */
function checkRoundWin(score, target) {
  return score >= target;
}

/**
 * autoFillSquad()
 * Returns [playerIds] — best 11 by sum of stats, with minimum role coverage.
 */
function autoFillSquad() {
  // Sort all players by total cost (sum of stats) descending
  var sorted = PLAYERS.slice().sort(function(a, b) {
    return (b.atk + b.pac + b.pas + b.def_ + b.spc) - (a.atk + a.pac + a.pas + a.def_ + a.spc);
  });

  var selected = [];
  var posCounts = {};

  // Must have: 1 GK
  function addBestAt(pos) {
    for (var i = 0; i < sorted.length; i++) {
      var p = sorted[i];
      if (p.position === pos && selected.indexOf(p.id) < 0) {
        selected.push(p.id);
        posCounts[pos] = (posCounts[pos] || 0) + 1;
        return p;
      }
    }
    return null;
  }

  // Force minimum role coverage
  addBestAt('GK');            // 1 GK

  // 3 defenders (CB/FB) — pick best 3
  var defCount = 0;
  for (var i = 0; i < sorted.length && defCount < 3; i++) {
    var p = sorted[i];
    if ((p.position === 'CB' || p.position === 'FB') && selected.indexOf(p.id) < 0) {
      selected.push(p.id);
      posCounts[p.position] = (posCounts[p.position] || 0) + 1;
      defCount++;
    }
  }

  // 3 midfielders (CM/CDM/CAM) — pick best 3
  var midCount = 0;
  for (var i = 0; i < sorted.length && midCount < 3; i++) {
    var p = sorted[i];
    if ((p.position === 'CM' || p.position === 'CDM' || p.position === 'CAM') && selected.indexOf(p.id) < 0) {
      selected.push(p.id);
      posCounts[p.position] = (posCounts[p.position] || 0) + 1;
      midCount++;
    }
  }

  // 2 attackers (ST/LW/RW) — pick best 2
  var atkCount = 0;
  for (var i = 0; i < sorted.length && atkCount < 2; i++) {
    var p = sorted[i];
    if ((p.position === 'ST' || p.position === 'LW' || p.position === 'RW') && selected.indexOf(p.id) < 0) {
      selected.push(p.id);
      posCounts[p.position] = (posCounts[p.position] || 0) + 1;
      atkCount++;
    }
  }

  // Fill remaining to 11 with best available
  var posPriority = ['CB', 'FB', 'CM', 'CDM', 'CAM', 'ST', 'LW', 'RW'];
  while (selected.length < 11) {
    for (var pi = 0; pi < posPriority.length; pi++) {
      if (selected.length >= 11) break;
      var pos = posPriority[pi];
      for (var i = 0; i < sorted.length; i++) {
        var p = sorted[i];
        if (p.position === pos && selected.indexOf(p.id) < 0) {
          selected.push(p.id);
          break;
        }
      }
    }
  }

  return selected;
}

/**
 * autoRecommendFormation(squadIds)
 * Returns formation id that best fits the squad composition.
 */
function autoRecommendFormation(squadIds) {
  // Count positions in squad
  var posCount = {};
  for (var i = 0; i < squadIds.length; i++) {
    var p = getPlayerById(squadIds[i]);
    if (p) {
      posCount[p.position] = (posCount[p.position] || 0) + 1;
    }
  }

  // Score each formation by how well the squad fills its slots
  var bestFormation = null;
  var bestScore = -1;

  for (var fi = 0; fi < FORMATIONS.length; fi++) {
    var form = FORMATIONS[fi];
    var slots = form.slots;
    var tempCount = {};
    for (var k in posCount) tempCount[k] = posCount[k];

    var filled = 0;
    for (var si = 0; si < slots.length; si++) {
      var slot = slots[si];
      if (tempCount[slot] && tempCount[slot] > 0) {
        tempCount[slot]--;
        filled++;
      }
    }

    // Bonus for matching CB count (back 3 vs back 4)
    var cbNeeded = 0;
    for (var si = 0; si < slots.length; si++) {
      if (slots[si] === 'CB') cbNeeded++;
    }
    var cbHave = posCount['CB'] || 0;
    var cbFit = Math.min(cbNeeded, cbHave) / Math.max(cbNeeded, 1);

    var score = filled + (cbFit * 2);

    if (score > bestScore) {
      bestScore = score;
      bestFormation = form.id;
    }
  }

  return bestFormation || '4-4-2';
}

/**
 * dealPhases()
 * Randomly picks 6 phases from ALL_PHASES (no repeats).
 * Returns array of phase ids.
 */
function dealPhases() {
  var shuffled = ALL_PHASES.slice();
  for (var i = shuffled.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = shuffled[i];
    shuffled[i] = shuffled[j];
    shuffled[j] = tmp;
  }
  // Python/tests: all 8 phases are available every round; only order is shuffled
  return shuffled.map(function(p) { return p.id; });
}

/**
 * evaluateComboChains(pickedPhases)
 * pickedPhases = array of phase ids in order (typically 3)
 * Returns array of { from, to, effect } describing chain effects.
 */
function evaluateComboChains(pickedPhases) {
  var results = [];

  for (var i = 1; i < pickedPhases.length; i++) {
    var prevId = pickedPhases[i - 1];
    var currId = pickedPhases[i];

    var prevPhase = null, currPhase = null;
    for (var pi = 0; pi < ALL_PHASES.length; pi++) {
      if (ALL_PHASES[pi].id === prevId) prevPhase = ALL_PHASES[pi];
      if (ALL_PHASES[pi].id === currId) currPhase = ALL_PHASES[pi];
    }

    if (!prevPhase || !currPhase) continue;

    var chainKey = prevPhase.tag + '_' + currPhase.tag;
    var chain = COMBO_CHAINS[chainKey];

    // Fallback for Specialist
    if (!chain && prevPhase.tag === 'Specialist') {
      chain = COMBO_CHAINS['Specialist_Any'];
    }

    if (chain) {
      results.push({
        from: prevPhase.name,
        to: currPhase.name,
        fromTag: prevPhase.tag,
        toTag: currPhase.tag,
        effect: chain.effect,
        value: chain.value,
        description: chain.desc
      });
    }
  }

  return results;
}

/**
 * applyFatigue(playerId)
 * Reduces fatigue after a player is used in a phase.
 * Fatigue multiplier decays multiplicatively (×0.7 each use by default).
 */
function applyFatigue(playerId) {
  var current = G.fatigue[playerId] !== undefined ? G.fatigue[playerId] : 1.0;
  G.fatigue[playerId] = current * 0.7;
  return G.fatigue[playerId];
}

/**
 * recoverFatigue(amount)
 * Global fatigue recovery between rounds.
 * amount = fraction of lost fatigue to recover (default 0.5).
 */
function recoverFatigue(amount) {
  var recovery = (amount !== undefined) ? amount : 0.5;
  for (var pid in G.fatigue) {
    if (G.fatigue.hasOwnProperty(pid)) {
      G.fatigue[pid] = G.fatigue[pid] + (1.0 - G.fatigue[pid]) * recovery;
    }
  }
}

/**
 * buyShopItem(itemId)
 * Deducts morale, adds buff to shopBuffs.
 * Item definitions are inline.
 * Returns true if purchased, false if insufficient morale.
 */
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

function buyShopItem(itemId) {
  var item = SHOP_ITEMS[itemId];
  if (!item) return false;
  if (G.morale < item.cost) return false;

  G.morale -= item.cost;

  // Apply immediate effect
  var eff = item.effect;
  G.shopBuffs.push({
    id: itemId,
    name: item.name,
    effect: eff,
    duration: 1 // single-use for next phase
  });

  // Handle recovery/instant effects
  if (eff.type === 'fullReset') {
    G.fatigue = {};
  }
  if (eff.type === 'morale') {
    G.morale += eff.value;
  }

  return true;
}

/**
 * resetRound()
 * Resets phase state for a new round, keeps fatigue and squad.
 */
function resetRound() {
  G.roundIdx = 0;
  G.phaseIdx = 0;
  G.roundScore = 0;
  G.dealtPhases = [];
  G.pickedPhases = [];
  G.field = [];
  G.phaseResults = [];

  // Consume shop buffs with duration
  G.shopBuffs = G.shopBuffs.filter(function(b) {
    b.duration--;
    return b.duration > 0;
  });

  // Recover fatigue between rounds
  recoverFatigue(0.5);
}

/**
 * saveGame()
 * Serializes G state to localStorage (minus playerPool to save space).
 */
function saveGame() {
  try {
    var saveData = {
      currentScreen: G.currentScreen,
      selectedIds: G.selectedIds,
      formation: G.formation,
      matchIdx: G.matchIdx,
      roundIdx: G.roundIdx,
      phaseIdx: G.phaseIdx,
      dealtPhases: G.dealtPhases,
      pickedPhases: G.pickedPhases,
      roundScore: G.roundScore,
      phaseResults: G.phaseResults,
      roundResults: G.roundResults,
      matchResults: G.matchResults,
      fatigue: G.fatigue,
      morale: G.morale,
      shopBuffs: G.shopBuffs,
      campaignWon: G.campaignWon,
      bestRun: G.bestRun
    };
    localStorage.setItem('squad_game_save', JSON.stringify(saveData));
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * loadGame()
 * Deserializes G state from localStorage.
 * Returns true if save loaded, false otherwise.
 */
function loadGame() {
  try {
    var raw = localStorage.getItem('squad_game_save');
    if (!raw) return false;
    var saveData = JSON.parse(raw);

    G.currentScreen = saveData.currentScreen || 'title';
    G.selectedIds = saveData.selectedIds || [];
    G.formation = saveData.formation || null;
    G.matchIdx = saveData.matchIdx || 0;
    G.roundIdx = saveData.roundIdx || 0;
    G.phaseIdx = saveData.phaseIdx || 0;
    G.dealtPhases = saveData.dealtPhases || [];
    G.pickedPhases = saveData.pickedPhases || [];
    G.roundScore = saveData.roundScore || 0;
    G.phaseResults = saveData.phaseResults || [];
    G.roundResults = saveData.roundResults || [];
    G.matchResults = saveData.matchResults || [];
    G.fatigue = saveData.fatigue || {};
    G.morale = (saveData.morale !== undefined) ? saveData.morale : 0;
    G.shopBuffs = saveData.shopBuffs || [];
    G.campaignWon = saveData.campaignWon || false;
    G.bestRun = saveData.bestRun || {wins: 0, score: 0};

    // Re-populate playerPool
    G.playerPool = PLAYERS.slice();

    return true;
  } catch (e) {
    return false;
  }
}

/* ===================================================================
   SECTION 12 — INITIALIZATION
   =================================================================== */

// Ensure playerPool is populated
G.playerPool = PLAYERS.slice();

/* ===================================================================
   SECTION 12 — BRIDGE / INTEGRATION FUNCTIONS
   Screen-to-screen game flow orchestrators.
   =================================================================== */

/**
 * initNewGame()
 * Fully reset G to defaults and prepare a fresh campaign.
 * Shuffles player pool, deals initial phases, sets title screen.
 */
function initNewGame() {
  // Reset to a fresh G state
  G.currentScreen = 'title';
  G.playerPool = PLAYERS.slice();
  G.selectedIds = [];
  G.formation = null;
  G.matchIdx = 0;
  G.roundIdx = 0;
  G.phaseIdx = 0;
  G.dealtPhases = [];
  G.pickedPhases = [];
  G.field = [];
  G.roundScore = 0;
  G.phaseResults = [];
  G.roundResults = [];
  G.matchResults = [];
  G.fatigue = {};
  G.morale = 0;
  G.shopBuffs = [];
  G.campaignWon = false;
  G.bestRun = G.bestRun || {wins: 4, score: 4200000};

  // Shuffle PLAYERS into playerPool for variety
  var shuffled = PLAYERS.slice();
  for (var i = shuffled.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var tmp = shuffled[i];
    shuffled[i] = shuffled[j];
    shuffled[j] = tmp;
  }
  G.playerPool = shuffled;

  // Deal initial phases
  G.dealtPhases = dealPhases();
}

/**
 * getCurrentMatch()
 * Returns the CAMPAIGN_MATCHES entry for the current match index.
 * Returns null if matchIdx is out of bounds.
 */
function getCurrentMatch() {
  if (G.matchIdx < 0 || G.matchIdx >= CAMPAIGN_MATCHES.length) return null;
  return CAMPAIGN_MATCHES[G.matchIdx];
}

/**
 * getSquadPlayers()
 * Returns full player objects for all ids in G.selectedIds.
 * Always returns an array (empty if no selections).
 */
function getSquadPlayers() {
  var result = [];
  if (!G.selectedIds || !G.selectedIds.length) return result;
  for (var i = 0; i < G.selectedIds.length; i++) {
    var p = getPlayerById(G.selectedIds[i]);
    if (p) result.push(p);
  }
  return result;
}

/**
 * getSquadCost()
 * Returns the total cost (sum of all stats) for the selected squad.
 * Returns 0 if no squad selected.
 */
function getSquadCost() {
  if (!G.selectedIds || !G.selectedIds.length) return 0;
  var total = 0;
  for (var i = 0; i < G.selectedIds.length; i++) {
    var p = getPlayerById(G.selectedIds[i]);
    if (p) total += (p.cost || calcCost(p));
  }
  return total;
}

/**
 * commitSquad(playerIds, formationId)
 * Locks in the squad selection and formation, initializes fatigue,
 * and advances to the formation/squad-confirmed screen.
 *
 * @param {Array}  playerIds   — Array of player id strings (11-12)
 * @param {string} formationId — Formation id (e.g. '4-4-2')
 */
function commitSquad(playerIds, formationId) {
  if (!playerIds || !playerIds.length) {
    G.selectedIds = [];
  } else {
    G.selectedIds = playerIds.slice();
  }

  G.formation = formationId || null;

  // Initialize all squad players' fatigue to 1.0 (fresh)
  G.fatigue = {};
  for (var i = 0; i < G.selectedIds.length; i++) {
    G.fatigue[G.selectedIds[i]] = 1.0;
  }

  G.currentScreen = 'formation';
}

/**
 * startMatch()
 * Initialize match-level state: reset round/phase indices and deal phases.
 * Advances to the phases screen.
 */
function startMatch() {
  G.roundIdx = 0;
  G.phaseIdx = 0;
  G.roundScore = 0;
  G.phaseResults = [];
  G.roundResults = [];
  G.pickedPhases = [];
  G.field = [];
  G.dealtPhases = dealPhases();
  G.currentScreen = 'phases';
}

/**
 * startRound()
 * Reset round-level state and deal fresh phases.
 */
function startRound() {
  G.roundScore = 0;
  G.phaseIdx = 0;
  G.pickedPhases = [];
  G.field = [];
  G.phaseResults = [];
  recoverFatigue(0.5);
  G.dealtPhases = dealPhases();
}

/**
 * commitPhases(phaseIds)
 * Locks in the 3 picked phases for this round.
 * Evaluates combo chains and stores the result for later display.
 *
 * @param {Array} phaseIds — Array of 3 phase id strings
 */
function commitPhases(phaseIds) {
  if (!phaseIds || !phaseIds.length) {
    G.pickedPhases = [];
    return;
  }
  G.pickedPhases = phaseIds.slice(0, 3);

  // Evaluate combo chains and attach to pickedPhases metadata
  G._comboChains = evaluateComboChains(G.pickedPhases);
}

/**
 * submitPhase(placements)
 * Submit player placements for the current phase, score it,
 * apply fatigue to used players, and return the score breakdown.
 *
 * @param {Array} placements — [{playerId, slotId}, ...]
 * @returns {object} score breakdown from calculatePhaseScore
 */
function submitPhase(placements) {
  if (!placements || !placements.length) {
    G.field = [];
    return { score: 0, breakdown: [], synergies: { chips: 0, addMult: 0, xMult: 1 }, phaseMult: 1.0 };
  }

  G.field = placements.slice();

  // Determine current phase id
  var phaseId = null;
  if (G.pickedPhases && G.pickedPhases.length > G.phaseIdx) {
    phaseId = G.pickedPhases[G.phaseIdx];
  }

  // Score the phase
  var result = calculatePhaseScore(G.field, phaseId);

  // Store result — full breakdown for phase-result screen
  G.phaseResults.push({
    phaseIdx: G.phaseIdx,
    phaseId: phaseId,
    score: result.score,
    breakdown: result.breakdown,
    playerChips: result.playerChips,
    synergyChips: result.synergyChips,
    carryoverChips: result.carryoverChips,
    totalBeforeMult: result.totalBeforeMult,
    addMult: result.addMult,
    xMult: result.xMult,
    formationMult: result.formationMult,
    momentum: result.momentum,
    fatigueAvg: result.fatigueAvg,
    phaseMult: result.phaseMult,
    synergies: result.synergies,
    persistentBuffs: result.persistentBuffs
  });

  // Accumulate round score
  G.roundScore += result.score;

  var match = getCurrentMatch();
  var target = (match && match.targets && match.targets.length > G.roundIdx) ? match.targets[G.roundIdx] : null;
  if (target !== null && result.score >= target * 0.7) {
    G.morale += 1;
  }

  // Apply fatigue to every player used in this phase
  for (var i = 0; i < placements.length; i++) {
    applyFatigue(placements[i].playerId);
  }

  // Advance phase index
  G.phaseIdx++;

  G.currentScreen = 'phase-result';

  return result;
}

/**
 * finishRound()
 * Check round win/loss against the match target, update morale,
 * and determine the next game step.
 *
 * @returns {string} 'next-phase' | 'next-round' | 'match-done'
 */
function finishRound() {
  var match = getCurrentMatch();
  var target = null;
  if (match && match.targets && match.targets.length > G.roundIdx) {
    target = match.targets[G.roundIdx];
  }

  var won = target !== null ? checkRoundWin(G.roundScore, target) : false;

  // Store round result
  G.roundResults.push({
    roundIdx: G.roundIdx,
    score: G.roundScore,
    target: target,
    won: won
  });

  // Earn +3 morale for a round win, +2 more for beating target by 50%
  if (won) {
    G.morale += 3;
    if (target && G.roundScore >= target * 1.5) G.morale += 2;
  }

  // Determine next step
  return (G.roundIdx < 2) ? 'next-round' : 'match-done';
}

/**
 * finishMatch()
 * Store final match result, update morale based on round wins,
 * and determine campaign progression.
 *
 * @returns {string} 'next-match' | 'campaign-won'
 */
function finishMatch() {
  var match = getCurrentMatch();
  if (!match) return 'campaign-won';

  // Count won rounds
  var roundsWon = 0;
  var roundsLost = 0;
  for (var i = 0; i < G.roundResults.length; i++) {
    if (G.roundResults[i].won) roundsWon++;
    else roundsLost++;
  }

  // Store match result
  G.matchResults.push({
    matchIdx: G.matchIdx,
    name: match.name,
    opponent: match.opponent,
    roundsWon: roundsWon,
    roundsLost: roundsLost,
    totalScore: G.roundScore
  });

  var matchWon = roundsWon >= 2;
  if (matchWon) G.morale += 5;
  if (roundsWon === 3) G.morale += 3;

  // Advance match
  G.matchIdx++;

  // Check best run
  var totalWins = 0;
  var totalScore = 0;
  for (var mi = 0; mi < G.matchResults.length; mi++) {
    totalWins += G.matchResults[mi].roundsWon;
    totalScore += G.matchResults[mi].totalScore || 0;
  }
  if (totalScore > (G.bestRun.score || 0)) {
    G.bestRun = { wins: totalWins, score: totalScore };
  }

  if (G.matchIdx < CAMPAIGN_MATCHES.length) {
    return 'next-match';
  }

  G.campaignWon = true;
  G.currentScreen = 'campaign-complete';
  return 'campaign-won';
}

/**
 * getActivePhase()
 * Returns the ALL_PHASES object for the current phase.
 * Returns null if no phase is active.
 */
function getActivePhase() {
  if (!G.pickedPhases || G.pickedPhases.length === 0) return null;
  if (G.phaseIdx < 0 || G.phaseIdx >= G.pickedPhases.length) return null;

  var phaseId = G.pickedPhases[G.phaseIdx];
  for (var i = 0; i < ALL_PHASES.length; i++) {
    if (ALL_PHASES[i].id === phaseId) return ALL_PHASES[i];
  }
  return null;
}

/**
 * getFatigueForPlayer(playerId)
 * Returns the fatigue multiplier for a player.
 * Defaults to 1.0 (fresh) if not set.
 *
 * @param {string} playerId
 * @returns {number} fatigue multiplier (0.3 – 1.0)
 */
function getFatigueForPlayer(playerId) {
  if (!playerId) return 1.0;
  if (G.fatigue && G.fatigue[playerId] !== undefined) {
    return G.fatigue[playerId];
  }
  return 1.0;
}

/**
 * getCampaignProgress()
 * Returns an overview of campaign state for UI rendering.
 *
 * @returns {object} { matches, results, current, campaignWon, morale }
 */
function getCampaignProgress() {
  return {
    matches: CAMPAIGN_MATCHES,
    results: G.matchResults || [],
    current: G.matchIdx,
    campaignWon: G.campaignWon || false,
    morale: G.morale || 0
  };
}
