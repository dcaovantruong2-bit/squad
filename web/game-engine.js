// PLAYER DATA (from data/players.toml)
// ═══════════════════════════════════════════════════════════════════════

const PLAYERS = [
  // ST
  { id:"terry_henri", name:"Terry Henri", position:"ST", atk:9, pac:9, pas:6, def_:1, spc:8, traits:["pacey","clinical"], description:"The clinical speedster. One touch, one goal." },
  { id:"big_zlat", name:"Big Zlat", position:"ST", atk:8, pac:5, pas:7, def_:2, spc:10, traits:["physical","technical"], description:"Acrobatic target man. Impossible is nothing." },
  { id:"kun_kun", name:"El Caníbal", position:"ST", atk:8, pac:8, pas:5, def_:1, spc:7, traits:["pacey","poacher"], description:"Low center of gravity. Never met a keester he wouldn't nibble." },
  { id:"the_waz", name:"The Waz", position:"ST", atk:8, pac:6, pas:7, def_:5, spc:6, traits:["physical","leader"], description:"Bulldog forward. Fights for every ball." },
  { id:"flash_forward", name:"Theo Walk-not", position:"ST", atk:5, pac:7, pas:2, def_:1, spc:3, traits:["pacey","poacher"], description:"All pace, half a finish." },
  { id:"lewan_goalski", name:"Lewan-goal-ski", position:"ST", atk:9, pac:5, pas:2, def_:1, spc:5, traits:["poacher","clinical"], description:"Lives in the six-yard box." },
  // RW
  { id:"rob_cutter", name:"Arjen Cutback", position:"RW", atk:8, pac:9, pas:6, def_:1, spc:8, traits:["pacey","clinical"], description:"Cut inside on his left." },
  { id:"rabona_ron", name:"El Shaa-ra-wrong", position:"RW", atk:5, pac:6, pas:5, def_:1, spc:6, traits:["pacey","clinical"], description:"Fancy flicks." },
  { id:"riyad_mahrizzle", name:"Riyad Mah-rizzle", position:"RW", atk:7, pac:7, pas:8, def_:2, spc:9, traits:["technical","playmaker"], description:"Silky dribbler on the wing." },
  // LW
  { id:"bale_out", name:"Bale Out", position:"LW", atk:8, pac:10, pas:6, def_:3, spc:7, traits:["pacey","physical"], description:"Pace AND power." },
  { id:"kylian_express", name:"Dictator Kylian", position:"LW", atk:7, pac:10, pas:5, def_:2, spc:7, traits:["pacey","clinical"], description:"Lightning in boots." },
  { id:"cult_carl", name:"Wilfried Za-ha-ha", position:"LW", atk:5, pac:7, pas:5, def_:2, spc:3, traits:["pacey","clinical"], description:"Fans love him." },
  // CM
  { id:"maestro_xav", name:"The Puppet Master", position:"CM", atk:3, pac:4, pas:10, def_:6, spc:7, traits:["playmaker","technical"], description:"Pulls the strings." },
  { id:"don_andres", name:"Don Andres", position:"CM", atk:6, pac:7, pas:9, def_:3, spc:10, traits:["technical","playmaker"], description:"Dribbling illusionist." },
  { id:"captain_stevie", name:"Captain Stevie", position:"CM", atk:8, pac:6, pas:8, def_:6, spc:8, traits:["leader","physical"], description:"Box-to-box thunder." },
  { id:"jimmy_journey", name:"Park Ji-zoom", position:"CM", atk:3, pac:4, pas:7, def_:4, spc:2, traits:["physical","leader","journeyman"], description:"Does a job." },
  { id:"yaya_too_strong", name:"Yaya Too Strong", position:"CM", atk:4, pac:6, pas:5, def_:9, spc:4, traits:["destroyer","physical","leader"], description:"Towering presence." },
  // CAM
  { id:"el_mago", name:"Juan Maestro", position:"CAM", atk:6, pac:5, pas:10, def_:2, spc:9, traits:["technical","playmaker"], description:"Wizard of the final third." },
  { id:"mesut_assist", name:"Mesut Assist", position:"CAM", atk:6, pac:6, pas:9, def_:4, spc:7, traits:["playmaker","technical"], description:"Orchestrates from the hole." },
  { id:"bruno_penandes", name:"Bruno Penandes", position:"CAM", atk:8, pac:5, pas:8, def_:3, spc:10, traits:["playmaker","clinical"], description:"Stats monster." },
  // CDM
  { id:"wall_claude", name:"N'Golo Kanteen", position:"CDM", atk:2, pac:4, pas:6, def_:10, spc:3, traits:["destroyer","technical"], description:"The destroyer." },
  { id:"frenkie_de_con", name:"Toni Cruise", position:"CDM", atk:4, pac:7, pas:10, def_:7, spc:7, traits:["technical","playmaker"], description:"Deep-lying conductor." },
  { id:"bog_bob", name:"Nigel de Wrong", position:"CDM", atk:2, pac:4, pas:5, def_:7, spc:2, traits:["destroyer","physical"], description:"Does the dirty work." },
  // CB
  { id:"il_capitano", name:"El Capitán", position:"CB", atk:3, pac:6, pas:7, def_:10, spc:5, traits:["leader","technical"], description:"Elegant reader of the game. Also reads your last will." },
  { id:"jt_rock", name:"Campbell-Soup", position:"CB", atk:4, pac:3, pas:4, def_:10, spc:4, traits:["physical","aerial"], description:"Eats attackers for lunch." },
  { id:"rolls_royce", name:"The Rolls Royce", position:"CB", atk:2, pac:8, pas:6, def_:9, spc:6, traits:["technical","leader"], description:"Elegant, composed." },
  { id:"old_man_dan", name:"Per Merterslower", position:"CB", atk:2, pac:2, pas:5, def_:8, spc:2, traits:["leader","aerial"], description:"Reads the game." },
  // FB
  { id:"el_tren", name:"Dani Elvis", position:"FB", atk:5, pac:9, pas:7, def_:7, spc:5, traits:["pacey","physical"], description:"The Brazilian train." },
  { id:"mr_reliable", name:"Lahm-burger", position:"FB", atk:3, pac:7, pas:8, def_:9, spc:4, traits:["technical","leader"], description:"Two-footed, intelligent." },
  { id:"cafu_express", name:"Kyle Jogger", position:"FB", atk:6, pac:10, pas:7, def_:6, spc:5, traits:["pacey","physical"], description:"Relentless engine." },
  { id:"the_crab", name:"The Tank", position:"FB", atk:2, pac:6, pas:4, def_:7, spc:1, traits:["destroyer","leader"], description:"Tank on tracks." },
  { id:"david_albino", name:"Dave", position:"FB", atk:3, pac:8, pas:7, def_:8, spc:5, traits:["technical","leader"], description:"Never beaten." },
  // GK
  { id:"gigi_wall", name:"Gigi The Wall", position:"GK", atk:1, pac:3, pas:5, def_:10, spc:8, traits:["leader","aerial"], description:"Commanded the box for 20 years." },
  { id:"sergio_muro", name:"Saint Lloris", position:"GK", atk:1, pac:2, pas:3, def_:10, spc:5, traits:["destroyer","leader"], description:"World Cup winner." },
  { id:"sweaty_keeper", name:"Claudio Bra-voops", position:"GK", atk:1, pac:5, pas:4, def_:7, spc:3, traits:["aerial"], description:"Rushes out." },
  { id:"rocket_raya", name:"Rocket Raya", position:"GK", atk:1, pac:5, pas:8, def_:6, spc:8, traits:["technical","leader"], description:"Sweeper-keeper." },
];

// ═══════════════════════════════════════════════════════════════════════
// CHIPS FORMULA (from src/scoring.py)
// ═══════════════════════════════════════════════════════════════════════

const CHIPS_FORMULA = {
  ST:  (p) => p.atk * 4 + p.pac * 2 + p.spc * 1,
  LW:  (p) => p.atk * 2 + p.pac * 3 + p.pas * 1,
  RW:  (p) => p.atk * 2 + p.pac * 3 + p.pas * 1,
  CM:  (p) => p.pas * 3 + p.atk * 2 + p.def_ * 1,
  CAM: (p) => p.pas * 3 + p.atk * 2 + p.spc * 1,
  CDM: (p) => p.def_ * 2 + p.pas * 3 + p.atk * 1,
  CB:  (p) => p.def_ * 3 + p.pac * 2 + p.atk * 1,
  FB:  (p) => p.def_ * 2 + p.pac * 3 + p.pas * 1,
  GK:  (p) => p.def_ * 3 + p.spc * 1,
};

function calculateChips(player, fieldPosition) {
  const fn = CHIPS_FORMULA[fieldPosition];
  if (!fn) throw new Error('Unknown position: ' + fieldPosition);
  return fn(player);
}

// Cost = sum of all stats
function calcCost(p) { return p.atk + p.pac + p.pas + p.def_ + p.spc; }

// ═══════════════════════════════════════════════════════════════════════
// PHASE DEFINITIONS (from src/phases.py)
// ═══════════════════════════════════════════════════════════════════════

const ALL_PHASES = [
  { id:"goal_kick", name:"Goal Kick", weight:"DEF", icon:"GK", maxCards:3,
    desc:"Keeper launches long — defenders win the header",
    slots:["GK", "CB", "CB"] },
  { id:"build_up", name:"Build-Up", weight:"PAS", icon:"BLD", maxCards:3,
    desc:"Play out from the back — fullbacks push up, midfield controls tempo",
    slots:["FB", "FB", "CM"] },
  { id:"wide_attack", name:"Wide Attack", weight:"PAC", icon:"WNG", maxCards:3,
    desc:"Overload the flanks — pacey wingers stretch the defence",
    slots:["FB", "LW", "RW"] },
  { id:"direct_play", name:"Direct Play", weight:"ATK", icon:"DIR", maxCards:3,
    desc:"Quick transition — bypass midfield, hit the attackers",
    slots:[["LW","RW"], "ST", "CM"] },
  { id:"defensive_block", name:"Defensive Block", weight:"DEF", icon:"BLK", maxCards:3,
    desc:"Compact defensive shape — tough to break down",
    slots:["CB", "CB", "CDM"] },
  { id:"tiki_taka", name:"Tiki-Taka", weight:"PAS", icon:"TIK", maxCards:3,
    desc:"Pass, move, repeat — creative midfielders control the game",
    slots:["CM", "CM", "CAM"] },
  { id:"counter", name:"Counter", weight:"PAC", icon:"CNT", maxCards:3,
    desc:"Explosive break — pacey attackers in behind",
    slots:["LW", "ST", "RW"] },
  { id:"set_piece", name:"Set Piece", weight:"SPC", icon:"SET", maxCards:3,
    desc:"Dead ball specialist meets aerial threat — CAM, CB, ST",
    slots:["CAM", "CB", "ST"] },
];

// ═══════════════════════════════════════════════════════════════════════
// FORMATION DEFINITIONS (from src/formations.py)
// ═══════════════════════════════════════════════════════════════════════

const FORMATIONS = [
  { id:"4-4-2", name:"4-4-2", handSize:11, globalMult:1.0,
    slots:["CB","CB","FB","FB","CM","CM","ST","ST"],
    positionBonus:{}, description:"Balanced. No frills. Classic.",
    pitchPositions:[
      {pos:"GK",x:50,y:92},
      {pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},
      {pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},
      {pos:"CM",x:30,y:40},{pos:"CM",x:70,y:40},
      {pos:"ST",x:30,y:17},{pos:"ST",x:70,y:17}
    ] },
  { id:"4-3-3", name:"4-3-3", handSize:12, globalMult:1.05,
    slots:["CB","CB","FB","FB","CDM","CM","CM","LW","RW","ST"],
    positionBonus:{"LW":20,"RW":20,"ST":-15,"CDM":-10},
    description:"Attacking. Wingers thrive (+20). ST and CDM stretched (-15/-10). +5% global.",
    pitchPositions:[
      {pos:"GK",x:50,y:92},
      {pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},
      {pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},
      {pos:"CDM",x:50,y:50},{pos:"CM",x:30,y:34},{pos:"CM",x:70,y:34},
      {pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}
    ] },
  { id:"5-3-2", name:"5-3-2", handSize:11, globalMult:0.95,
    slots:["CB","CB","CB","FB","FB","CM","CM","CDM","ST","ST"],
    positionBonus:{"CB":25,"FB":12,"LW":-20,"RW":-20},
    description:"Defence wins. CBs+25, FBs+12. Wingers don't exist (-20). -5% global.",
    pitchPositions:[
      {pos:"GK",x:50,y:92},
      {pos:"CB",x:18,y:76},{pos:"CB",x:50,y:76},{pos:"CB",x:82,y:76},
      {pos:"FB",x:5,y:55},{pos:"FB",x:95,y:55},
      {pos:"CDM",x:50,y:50},{pos:"CM",x:30,y:36},{pos:"CM",x:70,y:36},
      {pos:"ST",x:30,y:17},{pos:"ST",x:70,y:17}
    ] },
  { id:"3-4-3", name:"3-4-3", handSize:12, globalMult:1.08,
    slots:["CB","CB","CB","FB","FB","CM","CM","LW","ST","RW"],
    positionBonus:{"ST":20,"LW":15,"RW":15,"CB":-25},
    description:"All-out attack. Front 3 +15-20. CBs exposed (-25). +8% global.",
    pitchPositions:[
      {pos:"GK",x:50,y:92},
      {pos:"CB",x:20,y:76},{pos:"CB",x:50,y:76},{pos:"CB",x:80,y:76},
      {pos:"FB",x:8,y:50},{pos:"FB",x:92,y:50},
      {pos:"CM",x:35,y:38},{pos:"CM",x:65,y:38},
      {pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}
    ] },
  { id:"4-2-3-1", name:"4-2-3-1", handSize:12, globalMult:1.02,
    slots:["CB","CB","FB","FB","CM","CM","CAM","LW","RW","ST"],
    positionBonus:{"CM":10,"CAM":25,"ST":-15},
    description:"Possession. CAM+25, CM+10. Lone ST isolated (-15). +2% global.",
    pitchPositions:[
      {pos:"GK",x:50,y:92},
      {pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},
      {pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},
      {pos:"CM",x:30,y:40},{pos:"CM",x:70,y:40},
      {pos:"CAM",x:50,y:30},
      {pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}
    ] },
  { id:"4-5-1", name:"4-5-1", handSize:12, globalMult:0.98,
    slots:["CB","CB","FB","FB","CDM","CM","CM","LW","RW","ST"],
    positionBonus:{"CDM":15,"LW":20,"RW":20,"ST":-20,"CB":-5},
    description:"Counter. CDM+15, wingers+20. Lone ST isolated (-20). -2% global.",
    pitchPositions:[
      {pos:"GK",x:50,y:92},
      {pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},
      {pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},
      {pos:"CDM",x:50,y:50},{pos:"CM",x:30,y:36},{pos:"CM",x:70,y:36},
      {pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}
    ] },
];

// ═══════════════════════════════════════════════════════════════════════
// CAMPAIGN DATA (from src/match.py)
// ═══════════════════════════════════════════════════════════════════════

const CAMPAIGN_MATCHES = [
  { name:"Group Stage", opponent:"Wolves FC", targets:[2000,2700,3600], tier:"Match 1/5 — Easy",
    intro:"Relegation battlers. Forwards can't finish — exploit set pieces." },
  { name:"Round of 16", opponent:"Inter Your-Nan", targets:[2700,3300,4500], tier:"Match 2/5 — Moderate",
    intro:"Mid-table side. Solid defence but slow at the back." },
  { name:"Quarter Final", opponent:"Borussia Mönchen-flapjack", targets:[3300,4200,5100], tier:"Match 3/5 — Challenging",
    intro:"European contenders. Press hard — their midfield can be overrun." },
  { name:"Semi Final", opponent:"Man City Oilers", targets:[4200,5100,6300], tier:"Match 4/5 — Elite",
    intro:"Title favourites. No obvious weakness — need every synergy firing." },
  { name:"THE FINAL", opponent:"Galácticos FC", targets:[5100,6300,7500], tier:"Match 5/5 — Final Boss",
    intro:"The best in the world. Maximum focus required. Leave nothing on the pitch." },
];

// ═══════════════════════════════════════════════════════════════════════
// ELIGIBILITY CHECKING (from src/phases.py)
// ═══════════════════════════════════════════════════════════════════════

function isPlayerEligible(player, slotSpec) {
  // GK can only play GK slots
  if (player.position === 'GK' && slotSpec !== 'GK') return false;
  if (slotSpec === 'GK') return player.position === 'GK';
  // Any outfield player can fill any outfield slot (OOP penalty applies)
  return true;
}

function slotFieldPosition(slot) {
  // Return what field position a slot represents
  if (typeof slot === 'string') return slot;
  if (Array.isArray(slot)) return slot[0];
  return slot.as || 'ST';
}

// OOP penalty system
const POSITION_GROUPS = {
  'GK':['GK'], 'CB':['CB','FB','CDM'], 'FB':['FB','CB','CDM'],
  'CDM':['CDM','CB','CM'], 'CM':['CM','CAM','CDM'], 'CAM':['CAM','CM','ST'],
  'LW':['LW','RW','ST'], 'RW':['RW','LW','ST'], 'ST':['ST','LW','RW'],
};
function getPositionPenalty(playerPos, fieldPos) {
  if (playerPos === fieldPos) return 1.0;
  if (playerPos === 'GK' || fieldPos === 'GK') return 0.0;
  // Same group = similar (0.9), different group = OOP (0.7)
  const group = POSITION_GROUPS[playerPos] || [];
  if (group.includes(fieldPos)) return 0.9;
  return 0.7;
}

function slotLabel(slot) {
  if (typeof slot === 'string') return slot;
  if (Array.isArray(slot)) return slot.join('/');
  return '?';
}

function slotFieldPosition(slot) {
  // Return what field position a slot represents
  if (typeof slot === 'string') return slot;
  if (Array.isArray(slot)) return slot[0];
  return slot.as || 'ST';
}
// ═══════════════════════════════════════════════════════════════════════

const SYNERGIES = [
  // Phase-specific synergies
  { id:"clean_sheet", name:"Clean Sheet", rarity:"common", persistent:false,
    triggerType:"clean_sheet", trigger:{pos_a:"GK",pos_b:"CB",stat:"def_",threshold:18},
    effectType:"add_chips", effect:{add_chips:20},
    description:"GK DEF + CB DEF ≥ 18: +20 chips to both" },
  { id:"organised_defence", name:"Organised Defence", rarity:"common", persistent:false,
    triggerType:"organised_defence", trigger:{positions:["CB","CB"],stat:"def_",threshold:18},
    effectType:"add_chips", effect:{add_chips:20},
    description:"CB DEF + CB DEF ≥ 18: +20 chips to both CBs" },
  { id:"wingback_overlap", name:"Wingback Overlap", rarity:"common", persistent:false,
    triggerType:"wingback_overlap", trigger:{pos_a:"FB",stat_a:"pac",pos_b:"CM",stat_b:"pas",threshold:15},
    effectType:"add_chips", effect:{add_chips:25},
    description:"FB PAC + CM PAS ≥ 15: +25 chips to both" },
  { id:"overload", name:"Overload", rarity:"common", persistent:false,
    triggerType:"overload", trigger:{min_duplicates:2},
    effectType:"add_chips", effect:{add_chips:15},
    description:"2+ players at same position: +15 chips to each" },
  { id:"stretch_backline", name:"Stretch the Backline", rarity:"common", persistent:false,
    triggerType:"stretch_backline", trigger:{pos_a:"FB",stat_a:"pac",pos_b:"LW",stat_b:"pac",threshold:17},
    effectType:"multiply", effect:{multiply:1.5},
    description:"FB PAC + LW PAC ≥ 17: ×1.5 mult to both" },
  { id:"route_one", name:"Route One", rarity:"uncommon", persistent:false,
    triggerType:"route_one", trigger:{pos_a:"CB",stat_a:"pas",pos_b:"ST",stat_b:"pac",threshold:14},
    effectType:"add_chips", effect:{add_chips:30,target:"ST"},
    description:"CB PAS + ST PAC ≥ 14: +30 chips to ST" },
  { id:"battering_ram", name:"Battering Ram", rarity:"common", persistent:false,
    triggerType:"battering_ram", trigger:{pos_a:"CB",stat_a:"def_",pos_b:"ST",stat_b:"atk",threshold:17},
    effectType:"add_chips", effect:{add_chips:20},
    description:"CB DEF + ST ATK ≥ 17: +20 chips to both" },
  { id:"defensive_duo", name:"Defensive Duo", rarity:"uncommon", persistent:false,
    triggerType:"defensive_duo", trigger:{stat:"def_",threshold:18},
    effectType:"add_chips", effect:{add_chips:25},
    description:"2 highest DEF sum ≥ 18: +25 chips to all 3" },
  { id:"back_three", name:"Back Three", rarity:"rare", persistent:false,
    triggerType:"back_three", trigger:{stat:"def_",threshold:7},
    effectType:"multiply", effect:{multiply:1.3},
    description:"All 3 DEF ≥ 7: ×1.3 mult to all 3" },
  { id:"midfield_engine", name:"Midfield Engine", rarity:"common", persistent:false,
    triggerType:"midfield_engine", trigger:{positions:["CM","CM"],stat_a:"pas",stat_b:"def_",threshold:15},
    effectType:"add_chips", effect:{add_chips:25},
    description:"CM PAS + CM DEF ≥ 15: +25 chips to both" },
  { id:"double_pivot", name:"Double Pivot", rarity:"uncommon", persistent:false,
    triggerType:"double_pivot", trigger:{positions:["CM","CM"],stat:"pas",threshold:17},
    effectType:"carryover", effect:{add_chips:40,target_role:"attacker"},
    description:"2 CMs PAS ≥ 17: Next phase +40 chips to first attacker" },
  { id:"trio", name:"Trio", rarity:"rare", persistent:false,
    triggerType:"trio", trigger:{position:"CM",stat:"pas",threshold:7},
    effectType:"chain_multiply", effect:{multipliers:[1.3,1.5,1.3]},
    description:"All 3 CMs PAS ≥ 7: ×1.3/×1.5/×1.3 chain" },
  { id:"covering_defender", name:"Covering Defender", rarity:"uncommon", persistent:false,
    triggerType:"covering_defender", trigger:{position:"CB",stat_a:"pac",threshold_a:7,stat_b:"def_",threshold_b:9,different_players:true},
    effectType:"add_chips", effect:{add_chips:25},
    description:"CB PAC≥7 + another CB DEF≥9: +25 chips to both" },
  { id:"target_man_release", name:"Target Man Release", rarity:"uncommon", persistent:false,
    triggerType:"target_man_release", trigger:{pos_a:"ST",stat_a:"atk",winger_positions:["LW","RW"],stat_b:"pac",threshold:17},
    effectType:"multiply", effect:{multiply:1.5},
    description:"ST ATK + winger PAC ≥ 17: ×1.5 mult to the pacy winger" },
  { id:"near_post_flick", name:"Near Post Flick", rarity:"common", persistent:false,
    triggerType:"near_post_flick", trigger:{pos_a:"CAM",stat_a:"spc",pos_b:"ST",stat_b:"atk",threshold:16},
    effectType:"multiply", effect:{multiply:1.5},
    description:"CAM SPC + ST ATK ≥ 16: ×1.5 mult to ST" },
  { id:"one_two", name:"One-Two", rarity:"common", persistent:false,
    triggerType:"one_two", trigger:{pos_a:"CM",stat_a:"pas",pos_b:"ST",stat_b:"pac",threshold:15},
    effectType:"multiply", effect:{multiply:1.5},
    description:"CM PAS + ST PAC ≥ 15: ×1.5 mult to both" },
  { id:"overlap", name:"Overlap", rarity:"common", persistent:false,
    triggerType:"overlap", trigger:{pos_a:"FB",stat_a:"pac",pos_b:"LW",stat_b:"pas",threshold:15},
    effectType:"multiply", effect:{multiply:1.5},
    description:"FB PAC + LW PAS ≥ 15: ×1.5 mult to FB" },
  { id:"set_piece_threat", name:"Set Piece Threat", rarity:"uncommon", persistent:false,
    triggerType:"set_piece_threat", trigger:{stat_a:"def_",threshold_a:8,stat_b:"spc",threshold_b:7,different_players:true},
    effectType:"add_chips", effect:{add_chips:35,global:true},
    description:"DEF≥8 + SPC≥7 (diff players): +35 global chips" },
  // Squad-persistent synergies
  { id:"pace_in_behind", name:"Pace in Behind", rarity:"uncommon", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"pacey",min_count:5},
    effectType:"persistent_multiply", effect:{multiply:1.15,target_trait:"pacey"},
    description:"5+ pacey players: all pacey get ×1.15 mult each phase" },
  { id:"iron_wall", name:"Iron Wall", rarity:"uncommon", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"physical",min_count:3},
    effectType:"persistent_multiply", effect:{multiply:1.2,target_trait:"physical",fatigue_penalty:0.6},
    description:"3+ physical: physical get ×1.2 mult + fatigue ×0.6" },
  { id:"leadership_council", name:"Leadership Council", rarity:"common", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"leader",min_count:3},
    effectType:"persistent_add", effect:{add_chips:15,target:"all"},
    description:"3+ leaders: all players get +15 chips per phase" },
  { id:"tiki_taka_persistent", name:"Tiki-Taka", rarity:"uncommon", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"technical",min_count:3},
    effectType:"persistent_multiply", effect:{multiply:1.15,target_position:["CM","CDM","CAM"]},
    description:"3+ technical: midfielders get ×1.15 mult each phase" },
  { id:"clinical_edge", name:"Clinical Edge", rarity:"common", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"clinical",min_count:2},
    effectType:"persistent_add", effect:{add_chips:15,target_position:["LW","RW","ST"]},
    description:"2+ clinical: attackers get +15 chips per phase" },
  { id:"double_destroyer", name:"Double Destroyer", rarity:"common", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"destroyer",min_count:2},
    effectType:"persistent_multiply", effect:{multiply:1.2,target_position:["CB","FB","CDM"]},
    description:"2+ destroyers: defenders get ×1.2 mult each phase" },
  { id:"two_up_top", name:"Two Up Top", rarity:"rare", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"poacher",min_count:2},
    effectType:"persistent_multiply", effect:{multiply:1.3,target_position:["ST"]},
    description:"2+ poachers: STs get ×1.3 mult each phase" },
  { id:"journeyman", name:"Journeyman", rarity:"rare", persistent:true,
    triggerType:"squad_trait_present", trigger:{trait:"journeyman"},
    effectType:"persistent_special", effect:{special:"fatigue_reset"},
    description:"Journeyman in squad: once per match, restore one player's fatigue" },
  { id:"pace_and_power", name:"Pace & Power", rarity:"rare", persistent:true,
    triggerType:"squad_trait_combo", trigger:{traits:["pacey","physical"],min_count:2},
    effectType:"persistent_multiply", effect:{multiply:1.3,target_trait_combo:["pacey","physical"]},
    description:"2+ pacey+physical: those players get ×1.3 mult" },
  { id:"silent_killers", name:"Silent Killers", rarity:"uncommon", persistent:true,
    triggerType:"squad_trait_combo", trigger:{traits:["clinical","pacey"],min_count:2},
    effectType:"persistent_multiply", effect:{multiply:1.25,target_trait_combo:["clinical","pacey"]},
    description:"2+ clinical+pacey: those players get ×1.25 mult each phase" },
  { id:"aerial_fortress", name:"Aerial Fortress", rarity:"uncommon", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"aerial",min_count:3},
    effectType:"persistent_multiply", effect:{multiply:1.2,target_position:["ST","CB","GK"]},
    description:"3+ aerial: STs, CBs, GKs get ×1.2 mult each phase" },
  { id:"playmaker_network", name:"Playmaker Network", rarity:"common", persistent:true,
    triggerType:"squad_trait_count", trigger:{trait:"playmaker",min_count:3},
    effectType:"persistent_multiply", effect:{multiply:1.15,target_position:["CM","CAM","CDM"]},
    description:"3+ playmakers: midfielders get ×1.15 mult each phase" },
];

// ═══════════════════════════════════════════════════════════════════════
// SYNERGY DETECTION (from src/scoring.py)
// ═══════════════════════════════════════════════════════════════════════

const ATTACKER_POSITIONS = new Set(["LW","RW","ST"]);

function _playersAt(field, position) {
  return field.filter(([p, pos]) => pos === position).map(([p]) => p);
}

function _bestAt(field, position, stat) {
  const candidates = _playersAt(field, position);
  if (candidates.length === 0) return null;
  return candidates.reduce((best, p) => (p[stat] > best[stat] ? p : best), candidates[0]);
}

function detectSynergies(field, synergyCards) {
  // Phase-level accumulators (Balatro-style)
  var result = {
    chips: 0,
    add_mult: 0,
    x_mult: 1.0,
    nextCarryover: null,
    fired_details: [],
  };

  for (var si = 0; si < synergyCards.length; si++) {
    var syn = synergyCards[si];
    if (syn.persistent) continue;
    var tr = syn.trigger;
    var eff = syn.effect;
    var firedName = syn.name;
    var contributors = [];

    function addContrib(p) {
      if (contributors.indexOf(p.name) < 0) contributors.push(p.name);
    }

    switch (syn.triggerType) {
      case 'clean_sheet': {
        var gk = _bestAt(field, tr.pos_a, tr.stat);
        var cb = _bestAt(field, tr.pos_b, tr.stat);
        if (gk && cb && gk[tr.stat] + cb[tr.stat] >= tr.threshold) {
          addContrib(gk); addContrib(cb);
          var val = eff.chips || eff.add_chips || 0;
          result.chips += val;
          result.fired_details.push({name:firedName, effect_type:'chips', value:val, contributors:contributors.slice()});
        }
        break;
      }
      case 'organised_defence': {
        var cbs = _playersAt(field, tr.positions[0]);
        if (cbs.length >= 2) {
          cbs.sort(function(a,b){return b[tr.stat]-a[tr.stat]});
          if (cbs[0][tr.stat] + cbs[1][tr.stat] >= tr.threshold) {
            addContrib(cbs[0]); addContrib(cbs[1]);
            var val = eff.chips || eff.add_chips || 0;
            result.chips += val;
            result.fired_details.push({name:firedName, effect_type:'chips', value:val, contributors:contributors.slice()});
          }
        }
        break;
      }
      case 'defensive_duo': {
        var players = field.map(function(p){return p[0]});
        if (players.length >= 2) {
          var sorted = players.slice().sort(function(a,b){return b[tr.stat]-a[tr.stat]});
          if (sorted[0][tr.stat] + sorted[1][tr.stat] >= tr.threshold) {
            sorted.forEach(function(p){addContrib(p)});
            var val = eff.add_mult || eff.add_chips || 0;
            result.add_mult += val;
            result.fired_details.push({name:firedName, effect_type:'add_mult', value:val, contributors:contributors.slice()});
          }
        }
        break;
      }
      case 'overload': {
        var posCounts = {};
        for (var fi = 0; fi < field.length; fi++) {
          var pos = field[fi][1];
          if (!posCounts[pos]) posCounts[pos] = [];
          posCounts[pos].push(field[fi][0]);
        }
        var posKeys = Object.keys(posCounts);
        for (var pi = 0; pi < posKeys.length; pi++) {
          if (posCounts[posKeys[pi]].length >= (tr.min_duplicates || 2)) {
            posCounts[posKeys[pi]].forEach(function(p){addContrib(p)});
            var val = eff.add_mult || eff.add_chips || 0;
            result.add_mult += val;
            result.fired_details.push({name:firedName + ' (' + posKeys[pi] + ')', effect_type:'add_mult', value:val, contributors:contributors.slice()});
          }
        }
        break;
      }
      case 'stretch_backline':
      case 'back_three':
      case 'target_man_release':
      case 'near_post_flick':
      case 'one_two':
      case 'overlap': {
        // All x_mult synergies
        var val = eff.x_mult || eff.multiply || 1.0;
        if (val > 1.0) {
          // Find relevant players
          var playersOnField = field.map(function(f){return f[0]});
          playersOnField.forEach(function(p){addContrib(p)});
          result.x_mult *= val;
          result.fired_details.push({name:firedName, effect_type:'x_mult', value:val, contributors:contributors.slice()});
        }
        break;
      }
      case 'route_one': {
        var cb = _bestAt(field, tr.pos_a, tr.stat_a);
        var st = _bestAt(field, tr.pos_b, tr.stat_b);
        if (cb && st && cb[tr.stat_a] + st[tr.stat_b] >= tr.threshold) {
          addContrib(st);
          var val = eff.chips || eff.add_chips || 0;
          result.chips += val;
          result.fired_details.push({name:firedName, effect_type:'chips', value:val, contributors:contributors.slice()});
        }
        break;
      }
      case 'battering_ram': {
        var cb = _bestAt(field, tr.pos_a, tr.stat_a);
        var st = _bestAt(field, tr.pos_b, tr.stat_b);
        if (cb && st && cb[tr.stat_a] + st[tr.stat_b] >= tr.threshold) {
          addContrib(cb); addContrib(st);
          var val = eff.chips || eff.add_chips || 0;
          result.chips += val;
          result.fired_details.push({name:firedName, effect_type:'chips', value:val, contributors:contributors.slice()});
        }
        break;
      }
      case 'midfield_engine':
      case 'covering_defender':
      case 'wingback_overlap': {
        var val = eff.add_mult || eff.add_chips || 0;
        if (val > 0) {
          var playersOnField = field.map(function(f){return f[0]});
          playersOnField.forEach(function(p){addContrib(p)});
          result.add_mult += val;
          result.fired_details.push({name:firedName, effect_type:'add_mult', value:val, contributors:contributors.slice()});
        }
        break;
      }
      case 'double_pivot': {
        var cms = _playersAt(field, tr.positions[0]);
        if (cms.length >= 2) {
          var sorted = cms.slice().sort(function(a,b){return b[tr.stat]-a[tr.stat]});
          if (sorted[0][tr.stat] + sorted[1][tr.stat] >= tr.threshold) {
            sorted.forEach(function(p){addContrib(p)});
            result.nextCarryover = {
              type: 'double_pivot',
              source_synergy: syn.name,
              chips: eff.chips || eff.add_chips || 40,
              target_role: eff.target_role || 'attacker',
            };
            result.fired_details.push({name:firedName + ' (carryover)', effect_type:'carryover', value:eff.chips || eff.add_chips || 40, contributors:contributors.slice()});
          }
        }
        break;
      }
      case 'set_piece_threat': {
        var val = eff.chips || eff.add_chips || 0;
        result.chips += val;
        result.fired_details.push({name:firedName, effect_type:'chips', value:val, contributors:contributors.slice()});
        break;
      }
      default: break;
    }
  }

  return result;
}

// ═══════════════════════════════════════════════════════════════════════
// SQUAD-PERSISTENT SYNERGY DETECTION
// ═══════════════════════════════════════════════════════════════════════
// SQUAD-PERSISTENT SYNERGY DETECTION
// ═══════════════════════════════════════════════════════════════════════

function detectSquadSynergies(squad, synergyCards) {
  const buffs = {
    fatigue_penalty: 0.7,
    player_mult: {},
    player_add: {},
    position_mult: {},
    position_add: {},
    global_mult: 1.0,
    global_add: 0,
    journeyman_available: false,
    fired_synergies: [],
  };

  // Index players by trait
  const traitToPlayers = {};
  for (const p of squad) {
    for (const t of p.traits) {
      if (!traitToPlayers[t]) traitToPlayers[t] = [];
      traitToPlayers[t].push(p);
    }
  }

  for (const syn of synergyCards) {
    if (!syn.persistent) continue;
    const tr = syn.trigger;
    const eff = syn.effect;

    let triggered = false;

    switch (syn.triggerType) {
      case 'squad_trait_count': {
        const matching = traitToPlayers[tr.trait] || [];
        if (matching.length >= (tr.min_count || 1)) {
          triggered = true;
          _applyPersistentEffect(buffs, syn, eff, matching, squad);
        }
        break;
      }
      case 'squad_trait_present': {
        const matching = traitToPlayers[tr.trait] || [];
        if (matching.length > 0) {
          triggered = true;
          _applyPersistentEffect(buffs, syn, eff, matching, squad);
        }
        break;
      }
      case 'squad_trait_combo': {
        const required = tr.traits;
        const matching = squad.filter(p => required.every(t => p.traits.includes(t)));
        if (matching.length >= (tr.min_count || 1)) {
          triggered = true;
          _applyPersistentEffect(buffs, syn, eff, matching, squad);
        }
        break;
      }
    }
  }

  return buffs;
}

function _applyPersistentEffect(buffs, syn, eff, matchingPlayers, squad) {
  buffs.fired_synergies.push(syn.name);
  const etype = syn.effectType;

  if (etype === 'persistent_multiply') {
    const mult = eff.multiply || 1.0;
    if (eff.target_trait) {
      for (const p of squad) {
        if (p.traits.includes(eff.target_trait)) {
          buffs.player_mult[p.id] = (buffs.player_mult[p.id] || 1.0) * mult;
        }
      }
    }
    if (eff.target_trait_combo) {
      for (const p of squad) {
        if (eff.target_trait_combo.every(t => p.traits.includes(t))) {
          buffs.player_mult[p.id] = (buffs.player_mult[p.id] || 1.0) * mult;
        }
      }
    }
    if (eff.target_position) {
      for (const pos of eff.target_position) {
        buffs.position_mult[pos] = (buffs.position_mult[pos] || 1.0) * mult;
      }
    }
    // Iron Wall also reduces fatigue penalty
    if (eff.fatigue_penalty !== undefined) buffs.fatigue_penalty = eff.fatigue_penalty;
  } else if (etype === 'persistent_add') {
    const chips = eff.add_chips || 0;
    if (eff.target === 'all') {
      buffs.global_add += chips;
    }
    if (eff.target_position) {
      for (const pos of eff.target_position) {
        buffs.position_add[pos] = (buffs.position_add[pos] || 0) + chips;
      }
    }
    if (eff.target_trait_combo) {
      for (const p of squad) {
        if (eff.target_trait_combo.every(t => p.traits.includes(t))) {
          buffs.player_add[p.id] = (buffs.player_add[p.id] || 0) + chips;
        }
      }
    }
  } else if (etype === 'persistent_special') {
    if (eff.special === 'fatigue_reset') buffs.journeyman_available = true;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// FULL PHASE SCORE CALCULATION (from src/scoring.py)
// ═══════════════════════════════════════════════════════════════════════

function calculateRoundScore(field, synergyCards, formation, fatigue, carryover, persistentBuffs, shopBuffs, momentum) {
  if (!fatigue) fatigue = {};
  if (!persistentBuffs) persistentBuffs = { player_mult:{}, player_add:{}, position_mult:{}, position_add:{}, global_mult:1.0, global_add:0, fired_synergies:[] };
  if (!shopBuffs) shopBuffs = {};
  if (!momentum) momentum = 1.0;

  // 1. Detect phase synergies → phase-level accumulators
  var synResult = detectSynergies(field, synergyCards);
  var synChips = synResult.chips || 0;
  var addMult = synResult.add_mult || 0;
  var xMult = synResult.x_mult || 1.0;
  var nextCarryover = synResult.nextCarryover || null;
  var firedDetails = synResult.fired_details || [];
  var allFiredNames = {};
  for (var di = 0; di < firedDetails.length; di++) {
    allFiredNames[firedDetails[di].name] = true;
  }

  // 2. Apply persistent buff synergy names to fired_details
  if (persistentBuffs.fired_synergies) {
    for (var pi = 0; pi < persistentBuffs.fired_synergies.length; pi++) {
      firedDetails.push({ name: persistentBuffs.fired_synergies[pi] + ' (persistent)', effect_type:'persistent', value:0, contributors:[] });
    }
  }

  // 3. Calculate player chip contributions (with fatigue, OOP, per-player buffs)
  var playerChips = 0;
  var breakdown = [];
  for (var fi = 0; fi < field.length; fi++) {
    var player = field[fi][0];
    var pos = field[fi][1];
    
    var baseChips = calculateChips(player, pos);
    var fatigueMult = fatigue[player.id] !== undefined ? fatigue[player.id] : 1.0;
    var oopPenalty = getPositionPenalty(player.position, pos);
    
    // Persistent per-player buffs
    var ppMult = persistentBuffs.player_mult && persistentBuffs.player_mult[player.id] ? persistentBuffs.player_mult[player.id] : 1.0;
    var ppAdd = persistentBuffs.player_add && persistentBuffs.player_add[player.id] ? persistentBuffs.player_add[player.id] : 0;
    
    // Position-based persistent buffs
    var posMult = (persistentBuffs.position_mult && persistentBuffs.position_mult[pos]) || 1.0;
    var posAdd = (persistentBuffs.position_add && persistentBuffs.position_add[pos]) || 0;
    
    // Formation bonus
    var fBonus = (formation && formation.positionBonus && formation.positionBonus[pos]) || 0;
    
    // Effective chips = base + bonus × fatigue × OOP × persistent
    var effChips = Math.round((baseChips + fBonus + posAdd + ppAdd) * fatigueMult * oopPenalty * ppMult * posMult);
    
    playerChips += effChips;
    
    breakdown.push({
      player: player.name,
      position: pos,
      base_chips: baseChips,
      add_chips: 0,  // legacy
      multiply: 1.0, // legacy
      fatigue: fatigueMult,
      oop_penalty: oopPenalty,
      subtotal: effChips,
    });
  }

  // 4. Apply carryover (e.g. Double Pivot → first attacker)
  var carryoverChips = 0;
  if (carryover) {
    var targetRole = carryover.target_role || 'attacker';
    var bonusChips = carryover.chips || carryover.add_chips || 0;
    if (targetRole === 'attacker') {
      for (var ai = 0; ai < field.length; ai++) {
        var aPos = field[ai][1];
        if (ATTACKER_POSITIONS.has(aPos)) {
          carryoverChips += bonusChips;
          firedDetails.push({ name: (carryover.source_synergy || 'Carryover') + ' (carryover)', effect_type:'carryover', value:bonusChips, contributors:[] });
          break;
        }
      }
    }
  }

  // 5. Apply shop buffs
  var shopChips = shopBuffs.extra_chips || 0;
  var shopAddMult = shopBuffs.extra_add_mult || 0;

  // 6. Formation multiplier
  var formationMult = formation ? formation.globalMult : 1.0;

  // 7. Total chips
  var totalChips = playerChips + synChips + carryoverChips + shopChips;

  // 8. Total add_mult (base 1 + synergy add_mult + shop add_mult)
  var totalAddMult = 1 + addMult + shopAddMult;

  // 9. Total x_mult (synergy x_mult × formation × momentum)
  var totalXMult = xMult * formationMult * momentum;

  // 10. Final score
  var total = Math.round(totalChips * totalAddMult * totalXMult);

  // Build fired_synergies flat list for backward compat
  var firedSynergies = [];
  var synergyContributors = {};
  var synergyDescriptions = {};
  for (var di2 = 0; di2 < firedDetails.length; di2++) {
    var fd = firedDetails[di2];
    firedSynergies.push(fd.name);
    synergyContributors[fd.name] = fd.contributors || [];
    synergyDescriptions[fd.name] = fd.effect_type === 'chips' ? '+' + fd.value + ' chips' :
      fd.effect_type === 'add_mult' ? '+' + fd.value + ' mult' :
      fd.effect_type === 'x_mult' ? '×' + fd.value : '';
  }

  return {
    total: total,
    breakdown: breakdown,
    player_chips: playerChips,
    synergy_chips: synChips,
    carryover_chips: carryoverChips,
    shop_chips: shopChips,
    total_chips: totalChips,
    add_mult: totalAddMult,
    x_mult: totalXMult,
    formation_mult: formationMult,
    momentum: momentum,
    phase_mult: 1.0,
    subtotal_before_formation: Math.round(totalChips * totalAddMult * xMult),
    fired_synergies: firedSynergies,
    fired_details: firedDetails,
    next_carryover: nextCarryover,
    synergy_contributors: synergyContributors,
    synergy_descriptions: synergyDescriptions,
  };
}

// ═══════════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════════

function shuffleArray(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pickRandomPhases() {
  return shuffleArray(ALL_PHASES);
}

function dealPhases() {
  return shuffleArray(ALL_PHASES);
}

function getAvailableSynergies(squad, allSynergies) {
  const available = [];
  for (const s of allSynergies) {
    if (s.persistent) continue;
    const tr = s.trigger;
    let canFire = false;
    let involved = [];

    if (s.triggerType === 'clean_sheet') {
      const gks = squad.filter(p => p.position === 'GK');
      const cbs = squad.filter(p => p.position === 'CB');
      for (const gk of gks) {
        for (const cb of cbs) {
          if (gk.def_ + cb.def_ >= tr.threshold) {
            canFire = true;
            involved = [gk.name + ' (DEF' + gk.def_ + ')', cb.name + ' (DEF' + cb.def_ + ')'];
            break;
          }
        } if (canFire) break;
      }
    } else if (s.triggerType === 'stretch_backline') {
      const fbs = squad.filter(p => p.position === 'FB');
      const lws = squad.filter(p => p.position === 'LW');
      for (const fb of fbs) {
        for (const lw of lws) {
          if (fb.pac + lw.pac >= tr.threshold) {
            canFire = true;
            involved = [fb.name + ' (PAC' + fb.pac + ')', lw.name + ' (PAC' + lw.pac + ')'];
            break;
          }
        } if (canFire) break;
      }
    } else if (s.triggerType === 'one_two') {
      const cms = squad.filter(p => p.position === 'CM');
      const sts = squad.filter(p => p.position === 'ST');
      for (const cm of cms) {
        for (const st of sts) {
          if (cm.pas + st.pac >= tr.threshold) {
            canFire = true;
            involved = [cm.name + ' (PAS' + cm.pas + ')', st.name + ' (PAC' + st.pac + ')'];
            break;
          }
        } if (canFire) break;
      }
    }
    // More synergies checked similarly but condensed for brevity
    else if (s.triggerType === 'route_one') {
      const cbs = squad.filter(p => p.position === 'CB');
      const sts = squad.filter(p => p.position === 'ST');
      for (const cb of cbs) { for (const st of sts) { if (cb.pas + st.pac >= tr.threshold) { canFire = true; involved = [cb.name + '(PAS' + cb.pas + ')', st.name + '(PAC' + st.pac + ')']; break; } } if (canFire) break; }
    } else if (s.triggerType === 'battering_ram') {
      const cbs = squad.filter(p => p.position === 'CB');
      const sts = squad.filter(p => p.position === 'ST');
      for (const cb of cbs) { for (const st of sts) { if (cb.def_ + st.atk >= tr.threshold) { canFire = true; involved = [cb.name + '(DEF' + cb.def_ + ')', st.name + '(ATK' + st.atk + ')']; break; } } if (canFire) break; }
    } else if (s.triggerType === 'target_man_release') {
      const sts = squad.filter(p => p.position === 'ST');
      const wingers = squad.filter(p => p.position === 'LW' || p.position === 'RW');
      for (const st of sts) { for (const w of wingers) { if (st.atk + w.pac >= tr.threshold) { canFire = true; involved = [st.name + '(ATK' + st.atk + ')', w.name + '(PAC' + w.pac + ')']; break; } } if (canFire) break; }
    } else if (s.triggerType === 'set_piece_threat') {
      const defHigh = squad.filter(p => p.def_ >= tr.threshold_a);
      const spcHigh = squad.filter(p => p.spc >= tr.threshold_b);
      for (const dp of defHigh) { for (const sp of spcHigh) { if (dp.id !== sp.id) { canFire = true; involved = [dp.name + '(DEF' + dp.def_ + ')', sp.name + '(SPC' + sp.spc + ')']; break; } } if (canFire) break; }
    } else if (s.triggerType === 'defensive_duo') {
      const sorted = [...squad].sort((a, b) => b.def_ - a.def_);
      if (sorted.length >= 2 && sorted[0].def_ + sorted[1].def_ >= tr.threshold) { canFire = true; involved = [sorted[0].name + '(DEF' + sorted[0].def_ + ')', sorted[1].name + '(DEF' + sorted[1].def_ + ')']; }
    } else if (s.triggerType === 'trio') {
      const cms = squad.filter(p => p.position === 'CM' && p.pas >= (tr.threshold||7));
      if (cms.length >= 3) { canFire = true; involved = cms.slice(0,3).map(p => p.name + '(PAS' + p.pas + ')'); }
    } else if (s.triggerType === 'double_pivot') {
      const cms = squad.filter(p => p.position === 'CM');
      for (let i = 0; i < cms.length; i++) { for (let j = i+1; j < cms.length; j++) { if (cms[i].pas + cms[j].pas >= tr.threshold) { canFire = true; involved = [cms[i].name + '(PAS' + cms[i].pas + ')', cms[j].name + '(PAS' + cms[j].pas + ')']; break; } } if (canFire) break; }
    }

    if (canFire) {
      available.push({ name: s.name, desc: s.description, players: involved });
    }
  }
  return available;
}

// Squad-builder role groups
const ROLE_GROUPS = {
  GK:        { positions: ["GK"], min: 1, label: "Goalkeeper" },
  Defenders: { positions: ["CB","FB"], min: 3, label: "Defenders (CB/FB)" },
  Midfielders: { positions: ["CM","CDM","CAM"], min: 3, label: "Midfielders (CM/CDM/CAM)" },
  Attackers: { positions: ["ST","LW","RW"], min: 2, label: "Attackers (ST/LW/RW)" },
};
const MIN_TOTAL = 11;
const BUDGET = 360;

function checkMinimums(squad) {
  const missing = [];
  const posCounts = {};
  for (const p of squad) {
    posCounts[p.position] = (posCounts[p.position] || 0) + 1;
  }
  for (const [groupName, cfg] of Object.entries(ROLE_GROUPS)) {
    const total = cfg.positions.reduce((s, pos) => s + (posCounts[pos] || 0), 0);
    if (total < cfg.min) missing.push(cfg.label + ' (have ' + total + ')');
  }
  if (squad.length < MIN_TOTAL) missing.push('11 players minimum (have ' + squad.length + ')');
  return missing;
}
</script>

  <script>
  // ═══════════════════════════════════════════════════════════════════
  // VISUAL ANIMATIONS
  // ═══════════════════════════════════════════════════════════════════

  /** Cascade the phase result score counting up from 0 */
  