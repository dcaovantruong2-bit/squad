/**
 * SQUAD — Game Engine
 * Complete port of the Python game logic to JavaScript.
 * CHIPS_FORMULA, eligibility, synergies, scoring, campaign data.
 */

// ═══════════════════════════════════════════════════════════════════════
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
    desc:"Keeper launches long — your best defenders win the header",
    slots:["GK", {as:"CB",min_def:7}, {as:"CB",min_def:6}] },
  { id:"build_up", name:"Build-Up", weight:"PAS", icon:"BLD", maxCards:3,
    desc:"Play out from the back — any good passer can step up",
    slots:[{as:"FB",min_pas:6}, {as:"FB",min_pas:6}, {as:"CM",min_pas:7}] },
  { id:"wing_attack", name:"Wing Attack", weight:"PAC", icon:"WNG", maxCards:2,
    desc:"Overlap and cross — pace wins, position doesn't matter",
    slots:[{as:"FB",min_pac:7}, {as:"LW",min_pac:7}] },
  { id:"long_ball", name:"Long Ball", weight:"ATK", icon:"LNB", maxCards:2,
    desc:"Bypass midfield — your best attackers chase it down",
    slots:[{as:"CB",min_def:6,min_pac:5}, {as:"ST",min_atk:6}] },
  { id:"defensive_block", name:"Defensive Block", weight:"DEF", icon:"BLK", maxCards:3,
    desc:"Park the bus — your toughest players, any position",
    slots:[{as:"CB",min_def:8}, {as:"CB",min_def:7}, {as:"CDM",min_def:6}] },
  { id:"tiki_taka", name:"Tiki-Taka", weight:"PAS", icon:"TIK", maxCards:3,
    desc:"Pass, pass, pass — best passers control the game",
    slots:[{as:"CM",min_pas:8}, {as:"CM",min_pas:7}, {as:"CM",min_pas:6}] },
  { id:"counter_attack", name:"Counter-Attack", weight:"PAC", icon:"CNT", maxCards:3,
    desc:"Explosive break — pacey wingers stretch the defence for a finisher",
    slots:[{as:"LW",min_pac:7}, {as:"ST",min_atk:7}, {as:"RW",min_pac:7}] },
  { id:"set_piece", name:"Set Piece", weight:"SPC", icon:"SET", maxCards:2,
    desc:"Corner or free kick — specialist delivery meets a physical target",
    slots:[{as:"CAM",min_spc:7}, {as:"ST",min_atk:7,trait:"physical"}] },
  { id:"high_press", name:"High Press", weight:"PAC", icon:"PRS", maxCards:3,
    desc:"Suffocate the opponent — all three need pace to press high",
    slots:[{as:"ST",min_pac:7}, {as:"RW",min_pac:7}, {as:"CM",min_pac:6}] },
  { id:"through_ball", name:"Through Ball", weight:"ATK", icon:"THR", maxCards:2,
    desc:"One pass unlocks the defence — passer meets pace",
    slots:[{as:"CM",min_pas:7}, {as:"ST",min_pac:7}] },
  { id:"wingback_push", name:"Wingback Push", weight:"PAC", icon:"WNG", maxCards:2,
    desc:"Fullback bombs forward to combine with the winger",
    slots:[{as:"FB",min_pac:7}, {as:"LW",min_pas:6}] },
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
  { name:"Group Stage", opponent:"Wolves FC", targets:[350,450,600], tier:"Match 1/5 — Easy" },
  { name:"Round of 16", opponent:"Inter Your-Nan", targets:[450,580,750], tier:"Match 2/5 — Moderate" },
  { name:"Quarter Final", opponent:"Borussia Mönchen-flapjack", targets:[550,700,880], tier:"Match 3/5 — Challenging" },
  { name:"Semi Final", opponent:"Man City Oilers", targets:[650,800,1050], tier:"Match 4/5 — Elite" },
  { name:"THE FINAL", opponent:"Galácticos FC", targets:[800,950,1200], tier:"Match 5/5 — Final Boss" },
];

// ═══════════════════════════════════════════════════════════════════════
// ELIGIBILITY CHECKING (from src/phases.py)
// ═══════════════════════════════════════════════════════════════════════

function isPlayerEligible(player, slotSpec) {
  // String spec: player must be that exact position
  if (typeof slotSpec === 'string') {
    return player.position === slotSpec;
  }
  // Array spec: player must be one of those positions
  if (Array.isArray(slotSpec)) {
    return slotSpec.includes(player.position);
  }
  // Dict spec: stat/trait based eligibility
  if (slotSpec.min_atk && player.atk < slotSpec.min_atk) return false;
  if (slotSpec.min_pac && player.pac < slotSpec.min_pac) return false;
  if (slotSpec.min_pas && player.pas < slotSpec.min_pas) return false;
  if (slotSpec.min_def && player.def_ < slotSpec.min_def) return false;
  if (slotSpec.min_spc && player.spc < slotSpec.min_spc) return false;
  if (slotSpec.trait && !player.traits.includes(slotSpec.trait)) return false;
  return true;
}

function slotLabel(slot) {
  if (typeof slot === 'string') return slot;
  if (Array.isArray(slot)) return slot.join('/');
  if (typeof slot === 'object' && slot.as) {
    const parts = [];
    if (slot.min_atk) parts.push('ATK≥' + slot.min_atk);
    if (slot.min_pac) parts.push('PAC≥' + slot.min_pac);
    if (slot.min_pas) parts.push('PAS≥' + slot.min_pas);
    if (slot.min_def) parts.push('DEF≥' + slot.min_def);
    if (slot.min_spc) parts.push('SPC≥' + slot.min_spc);
    if (slot.trait) parts.push(slot.trait);
    return '→' + slot.as + (parts.length ? ' [' + parts.join(', ') + ']' : '');
  }
  return '?';
}

function slotFieldPosition(slot) {
  // The position the player will play at (for CHIPS_FORMULA)
  if (typeof slot === 'string') return slot;
  if (typeof slot === 'object' && slot.as) return slot.as;
  return '?';
}

// ═══════════════════════════════════════════════════════════════════════
// SYNERGY DATA (from data/synergies.toml)
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
  const players = field.map(([p]) => p);
  const results = {};
  for (const p of players) {
    results[p.id] = { multiply: 1.0, add_chips: 0, fired_synergies: [] };
  }

  let globalMult = 1.0;
  let globalAdd = 0;
  let nextCarryover = null;

  for (const syn of synergyCards) {
    if (syn.persistent) continue; // Persistent synergies handled separately
    const tr = syn.trigger;
    const eff = syn.effect;

    switch (syn.triggerType) {
      case 'clean_sheet': {
        const gk = _bestAt(field, tr.pos_a, tr.stat);
        const cb = _bestAt(field, tr.pos_b, tr.stat);
        if (gk && cb && gk[tr.stat] + cb[tr.stat] >= tr.threshold) {
          for (const p of [gk, cb]) {
            results[p.id].add_chips += eff.add_chips || 0;
            results[p.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'organised_defence': {
        const cbs = _playersAt(field, tr.positions[0]);
        if (cbs.length >= 2) {
          cbs.sort((a, b) => b[tr.stat] - a[tr.stat]);
          if (cbs[0][tr.stat] + cbs[1][tr.stat] >= tr.threshold) {
            for (const p of [cbs[0], cbs[1]]) {
              results[p.id].add_chips += eff.add_chips || 0;
              results[p.id].fired_synergies.push(syn.name);
            }
          }
        }
        break;
      }
      case 'wingback_overlap': {
        const fb = _bestAt(field, tr.pos_a, tr.stat_a);
        const cm = _bestAt(field, tr.pos_b, tr.stat_b);
        if (fb && cm && fb[tr.stat_a] + cm[tr.stat_b] >= tr.threshold) {
          for (const p of [fb, cm]) {
            results[p.id].add_chips += eff.add_chips || 0;
            results[p.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'overload': {
        const posCounts = {};
        for (const [p, pos] of field) {
          if (!posCounts[pos]) posCounts[pos] = [];
          posCounts[pos].push(p);
        }
        for (const pos of Object.keys(posCounts)) {
          if (posCounts[pos].length >= (tr.min_duplicates || 2)) {
            for (const p of posCounts[pos]) {
              results[p.id].add_chips += eff.add_chips || 0;
              results[p.id].fired_synergies.push(syn.name);
            }
          }
        }
        break;
      }
      case 'stretch_backline': {
        const fb = _bestAt(field, tr.pos_a, tr.stat_a);
        const lw = _bestAt(field, tr.pos_b, tr.stat_b);
        if (fb && lw && fb[tr.stat_a] + lw[tr.stat_b] >= tr.threshold) {
          for (const p of [fb, lw]) {
            results[p.id].multiply *= eff.multiply || 1.0;
            results[p.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'route_one': {
        const cb = _bestAt(field, tr.pos_a, tr.stat_a);
        const st = _bestAt(field, tr.pos_b, tr.stat_b);
        if (cb && st && cb[tr.stat_a] + st[tr.stat_b] >= tr.threshold) {
          const target = eff.target || 'ST';
          if (target === 'ST') {
            results[st.id].add_chips += eff.add_chips || 0;
            results[st.id].fired_synergies.push(syn.name);
          }
          results[cb.id].fired_synergies.push(syn.name);
        }
        break;
      }
      case 'battering_ram': {
        const cb = _bestAt(field, tr.pos_a, tr.stat_a);
        const st = _bestAt(field, tr.pos_b, tr.stat_b);
        if (cb && st && cb[tr.stat_a] + st[tr.stat_b] >= tr.threshold) {
          for (const p of [cb, st]) {
            results[p.id].add_chips += eff.add_chips || 0;
            results[p.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'defensive_duo': {
        if (players.length >= 2) {
          const sorted = [...players].sort((a, b) => b[tr.stat] - a[tr.stat]);
          if (sorted[0][tr.stat] + sorted[1][tr.stat] >= tr.threshold) {
            for (const p of players) {
              results[p.id].add_chips += eff.add_chips || 0;
              results[p.id].fired_synergies.push(syn.name);
            }
          }
        }
        break;
      }
      case 'back_three': {
        if (players.every(p => p[tr.stat] >= tr.threshold)) {
          for (const p of players) {
            results[p.id].multiply *= eff.multiply || 1.0;
            results[p.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'midfield_engine': {
        const cms = _playersAt(field, tr.positions[0]);
        if (cms.length >= 2) {
          const sortedByPas = [...cms].sort((a, b) => b[tr.stat_a] - a[tr.stat_a]);
          const bestPas = sortedByPas[0];
          const remaining = cms.filter(p => p.id !== bestPas.id);
          const bestDef = remaining.reduce((best, p) => (p[tr.stat_b] > best[tr.stat_b] ? p : best), remaining[0]);
          if (bestPas[tr.stat_a] + bestDef[tr.stat_b] >= tr.threshold) {
            for (const p of [bestPas, bestDef]) {
              results[p.id].add_chips += eff.add_chips || 0;
              results[p.id].fired_synergies.push(syn.name);
            }
          }
        }
        break;
      }
      case 'double_pivot': {
        const cms = _playersAt(field, tr.positions[0]);
        if (cms.length >= 2) {
          const sorted = [...cms].sort((a, b) => b[tr.stat] - a[tr.stat]);
          if (sorted[0][tr.stat] + sorted[1][tr.stat] >= tr.threshold) {
            nextCarryover = {
              type: 'double_pivot',
              source_synergy: syn.name,
              add_chips: eff.add_chips || 40,
              target_role: eff.target_role || 'attacker',
            };
            for (const p of [sorted[0], sorted[1]]) {
              results[p.id].fired_synergies.push(syn.name);
            }
          }
        }
        break;
      }
      case 'trio': {
        const cms = _playersAt(field, tr.position);
        if (cms.length >= 3 && cms.every(p => p[tr.stat] >= tr.threshold)) {
          const sorted = [...cms].sort((a, b) => b[tr.stat] - a[tr.stat]);
          const mults = eff.multipliers || [1.3, 1.5, 1.3];
          for (let i = 0; i < sorted.length; i++) {
            const m = mults[Math.min(i, mults.length - 1)];
            results[sorted[i].id].multiply *= m;
            results[sorted[i].id].fired_synergies.push(syn.name + ' (×' + m + ')');
          }
        }
        break;
      }
      case 'covering_defender': {
        const cbs = _playersAt(field, tr.position);
        if (cbs.length >= 2) {
          const pacCbs = cbs.filter(p => p[tr.stat_a] >= tr.threshold_a);
          const defCbs = cbs.filter(p => p[tr.stat_b] >= tr.threshold_b);
          let fired = false;
          for (const fp of pacCbs) {
            for (const sp of defCbs) {
              if (fp.id !== sp.id) {
                for (const p of [fp, sp]) {
                  results[p.id].add_chips += eff.add_chips || 0;
                  results[p.id].fired_synergies.push(syn.name);
                }
                fired = true;
                break;
              }
            }
            if (fired) break;
          }
        }
        break;
      }
      case 'target_man_release': {
        const st = _bestAt(field, tr.pos_a, tr.stat_a);
        const wingerPositions = tr.winger_positions || ['LW', 'RW'];
        const wingers = field.filter(([p, pos]) => wingerPositions.includes(pos)).map(([p]) => p);
        if (st && wingers.length > 0) {
          const bestWinger = wingers.reduce((best, p) => (p[tr.stat_b] > best[tr.stat_b] ? p : best), wingers[0]);
          if (st[tr.stat_a] + bestWinger[tr.stat_b] >= tr.threshold) {
            results[bestWinger.id].multiply *= eff.multiply || 1.0;
            results[bestWinger.id].fired_synergies.push(syn.name);
            results[st.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'near_post_flick': {
        const cam = _bestAt(field, tr.pos_a, tr.stat_a);
        const st = _bestAt(field, tr.pos_b, tr.stat_b);
        if (cam && st && cam[tr.stat_a] + st[tr.stat_b] >= tr.threshold) {
          results[st.id].multiply *= eff.multiply || 1.0;
          results[st.id].fired_synergies.push(syn.name);
          results[cam.id].fired_synergies.push(syn.name);
        }
        break;
      }
      case 'one_two': {
        const cm = _bestAt(field, tr.pos_a, tr.stat_a);
        const st = _bestAt(field, tr.pos_b, tr.stat_b);
        if (cm && st && cm[tr.stat_a] + st[tr.stat_b] >= tr.threshold) {
          for (const p of [cm, st]) {
            results[p.id].multiply *= eff.multiply || 1.0;
            results[p.id].fired_synergies.push(syn.name);
          }
        }
        break;
      }
      case 'overlap': {
        const fb = _bestAt(field, tr.pos_a, tr.stat_a);
        const lw = _bestAt(field, tr.pos_b, tr.stat_b);
        if (fb && lw && fb[tr.stat_a] + lw[tr.stat_b] >= tr.threshold) {
          results[fb.id].multiply *= eff.multiply || 1.0;
          results[fb.id].fired_synergies.push(syn.name);
          results[lw.id].fired_synergies.push(syn.name);
        }
        break;
      }
      case 'set_piece_threat': {
        const defPlayers = players.filter(p => p[tr.stat_a] >= tr.threshold_a);
        const spcPlayers = players.filter(p => p[tr.stat_b] >= tr.threshold_b);
        if (defPlayers.length > 0 && spcPlayers.length > 0) {
          if (tr.different_players) {
            for (const dp of defPlayers) {
              for (const sp of spcPlayers) {
                if (dp.id !== sp.id) {
                  globalAdd += eff.add_chips || 0;
                  for (const p of players) {
                    results[p.id].fired_synergies.push(syn.name);
                  }
                  break;
                }
              }
            }
          }
        }
        break;
      }
    }
  }

  results.__global__ = { global_mult: globalMult, global_add: globalAdd };
  if (nextCarryover) results.__carryover__ = nextCarryover;
  return results;
}

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

function calculateRoundScore(field, synergyCards, formation, fatigue, carryover, persistentBuffs) {
  if (!fatigue) fatigue = {};
  if (!persistentBuffs) persistentBuffs = {
    player_mult:{}, player_add:{}, position_mult:{}, position_add:{},
    global_mult:1.0, global_add:0,
  };

  const synergies = detectSynergies(field, synergyCards);
  const globalMeta = synergies.__global__ || { global_mult: 1.0, global_add: 0 };
  const nextCarryover = synergies.__carryover__ || null;
  delete synergies.__global__;
  delete synergies.__carryover__;

  // Apply carryover bonus
  if (carryover) {
    const targetRole = carryover.target_role || 'attacker';
    const bonusChips = carryover.add_chips || 0;
    if (targetRole === 'attacker') {
      for (const [player, pos] of field) {
        if (ATTACKER_POSITIONS.has(pos)) {
          if (!synergies[player.id]) synergies[player.id] = { multiply: 1.0, add_chips: 0, fired_synergies: [] };
          synergies[player.id].add_chips += bonusChips;
          synergies[player.id].fired_synergies.push(carryover.source_synergy + ' (carryover)');
          break;
        }
      }
    }
  }

  // Apply persistent buffs
  const pb = persistentBuffs;
  const combinedGlobalMult = globalMeta.global_mult * (pb.global_mult || 1.0);
  const combinedGlobalAdd = globalMeta.global_add + (pb.global_add || 0);

  for (const [player, pos] of field) {
    const pid = player.id;
    // Per-player mult from persistent buffs
    if (pb.player_mult && pb.player_mult[pid]) {
      if (!synergies[pid]) synergies[pid] = { multiply: 1.0, add_chips: 0, fired_synergies: [] };
      synergies[pid].multiply *= pb.player_mult[pid];
    }
    // Per-player add_chips from persistent buffs
    if (pb.player_add && pb.player_add[pid]) {
      if (!synergies[pid]) synergies[pid] = { multiply: 1.0, add_chips: 0, fired_synergies: [] };
      synergies[pid].add_chips += pb.player_add[pid];
    }
    // Position-based persistent buffs
    const posMult = (pb.position_mult && pb.position_mult[pos]) || 1.0;
    const posAdd = (pb.position_add && pb.position_add[pos]) || 0;
    if (posMult !== 1.0 || posAdd !== 0) {
      if (!synergies[pid]) synergies[pid] = { multiply: 1.0, add_chips: 0, fired_synergies: [] };
      synergies[pid].multiply *= posMult;
      synergies[pid].add_chips += posAdd;
    }
  }

  // Collect persistent synergy names
  for (const name of (pb.fired_synergies || [])) {
    for (const pid of Object.keys(synergies)) {
      synergies[pid].fired_synergies.push(name + ' (persistent)');
    }
  }

  // Build synergy contributors map
  const synergyContributors = {};
  for (const [player, pos] of field) {
    const pid = player.id;
    if (synergies[pid]) {
      for (const rawName of synergies[pid].fired_synergies) {
        const cleanName = rawName.split(' (')[0];
        const entry = player.name + ' [' + pos + ']';
        if (!synergyContributors[cleanName]) synergyContributors[cleanName] = [];
        if (!synergyContributors[cleanName].includes(entry)) synergyContributors[cleanName].push(entry);
      }
    }
  }
  if (pb.fired_synergies && pb.fired_synergies.length > 0) {
    synergyContributors.__persistent__ = [...pb.fired_synergies];
  }

  // Formation multiplier
  const formationMult = formation ? (formation.globalMult || 1.0) : 1.0;

  const breakdown = [];
  let total = 0;
  const allFired = new Set();

  for (const [player, pos] of field) {
    let baseChips = calculateChips(player, pos);
    // Formation position bonus
    const posBonus = formation && formation.positionBonus ? (formation.positionBonus[pos] || 0) : 0;
    baseChips += posBonus;

    const playerSyn = synergies[player.id] || { multiply: 1.0, add_chips: 0, fired_synergies: [] };
    const fatigueMult = fatigue[player.id] !== undefined ? fatigue[player.id] : 1.0;

    const chipsWithBonus = baseChips + playerSyn.add_chips;
    const afterMult = chipsWithBonus * playerSyn.multiply * fatigueMult;

    for (const name of playerSyn.fired_synergies) allFired.add(name.split(' (')[0]);

    breakdown.push({
      player: player.name,
      position: pos,
      base_chips: baseChips,
      add_chips: playerSyn.add_chips,
      multiply: Math.round(playerSyn.multiply * 100) / 100,
      fatigue: Math.round(fatigueMult * 100) / 100,
      subtotal: Math.round(afterMult),
    });
    total += afterMult;
  }

  const subtotalBeforeGlobals = Math.round(total);
  total = total * combinedGlobalMult + combinedGlobalAdd;
  total = Math.round(total * formationMult);

  // Build synergy descriptions
  const synergyDescriptions = {};
  for (const syn of synergyCards) {
    if (allFired.has(syn.name) || (pb.fired_synergies && pb.fired_synergies.includes(syn.name))) {
      synergyDescriptions[syn.name] = syn.description;
    }
  }

  return {
    total,
    breakdown,
    subtotal_before_globals: subtotalBeforeGlobals,
    formation_mult: formationMult,
    formation_name: formation ? formation.name : '',
    global_mult: Math.round(combinedGlobalMult * 1000) / 1000,
    global_add: combinedGlobalAdd,
    fired_synergies: [...allFired].sort(),
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

function pickRandomPhases(count) {
  const shuffled = shuffleArray(ALL_PHASES);
  return shuffled.slice(0, Math.min(count, shuffled.length));
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
