/** SQUAD — Game Engine (clean rebuild) */
// PLAYER DATA
const PLAYERS = [
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
function calcCost(p) { return p.atk + p.pac + p.pas + p.def_ + p.spc; }
var BUDGET = 360, MIN_TOTAL = 11;

// CHIPS FORMULA
var CHIPS_FORMULA = {
  GK: function(p) { return Math.round(p.def_ * 3 + p.spc * 2); },
  CB: function(p) { return Math.round(p.def_ * 5); },
  FB: function(p) { return Math.round(p.def_ * 3 + p.pac * 1.5); },
  CDM: function(p) { return Math.round(p.def_ * 4 + p.pas * 1); },
  CM: function(p) { return Math.round(p.pas * 4 + p.def_ * 1); },
  CAM: function(p) { return Math.round(p.pas * 3.5 + p.atk * 2 + p.spc * 1); },
  LW: function(p) { return Math.round(p.pac * 3 + p.atk * 2); },
  RW: function(p) { return Math.round(p.pac * 3 + p.atk * 2); },
  ST: function(p) { return Math.round(p.atk * 4 + p.pac * 1.5); },
};
function calculateChips(player, fieldPosition) {
  var fn = CHIPS_FORMULA[fieldPosition];
  return fn ? fn(player) : (player.atk + player.pac + player.pas + player.def_ + player.spc) * 4;
}

// 8 TACTICAL FOCUSES
var ALL_PHASES = [
  { id:"goal_kick", name:"Goal Kick", weight:"DEF", icon:"GK", maxCards:3, desc:"Keeper launches long — defenders win the header", slots:["GK","CB","CB"] },
  { id:"build_up", name:"Build-Up", weight:"PAS", icon:"BLD", maxCards:3, desc:"Play out from the back — fullbacks push up", slots:["FB","FB","CM"] },
  { id:"wide_attack", name:"Wide Attack", weight:"PAC", icon:"WNG", maxCards:3, desc:"Overload the flanks — pacey wingers stretch defence", slots:["FB","LW","RW"] },
  { id:"direct_play", name:"Direct Play", weight:"ATK", icon:"DIR", maxCards:3, desc:"Quick transition — bypass midfield", slots:[["LW","RW"],"ST","CM"] },
  { id:"defensive_block", name:"Defensive Block", weight:"DEF", icon:"BLK", maxCards:3, desc:"Compact defensive shape", slots:["CB","CB","CDM"] },
  { id:"tiki_taka", name:"Tiki-Taka", weight:"PAS", icon:"TIK", maxCards:3, desc:"Pass, move, repeat — creative midfielders", slots:["CM","CM","CAM"] },
  { id:"counter", name:"Counter", weight:"PAC", icon:"CNT", maxCards:3, desc:"Explosive break — pacey attackers in behind", slots:["LW","ST","RW"] },
  { id:"set_piece", name:"Set Piece", weight:"SPC", icon:"SET", maxCards:3, desc:"Dead ball specialist meets aerial threat", slots:["CAM","CB","ST"] },
];

// FORMATIONS (with pitchPositions for carousel)
var FORMATIONS = [
  { id:"4-4-2", name:"4-4-2", handSize:11, globalMult:1.0,
    slots:["CB","CB","FB","FB","CM","CM","ST","ST"],
    positionBonus:{}, description:"Balanced. No frills. Classic.",
    pitchPositions:[{pos:"GK",x:50,y:92},{pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},{pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},{pos:"CM",x:30,y:40},{pos:"CM",x:70,y:40},{pos:"ST",x:30,y:17},{pos:"ST",x:70,y:17}] },
  { id:"4-3-3", name:"4-3-3", handSize:12, globalMult:1.05,
    slots:["CB","CB","FB","FB","CDM","CM","CM","LW","RW","ST"],
    positionBonus:{"LW":20,"RW":20,"ST":-15,"CDM":-10},
    description:"Attacking. Wingers thrive (+20). ST and CDM stretched (-15/-10). +5% global.",
    pitchPositions:[{pos:"GK",x:50,y:92},{pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},{pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},{pos:"CDM",x:50,y:50},{pos:"CM",x:30,y:34},{pos:"CM",x:70,y:34},{pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}] },
  { id:"5-3-2", name:"5-3-2", handSize:11, globalMult:0.95,
    slots:["CB","CB","CB","FB","FB","CM","CM","CDM","ST","ST"],
    positionBonus:{"CB":25,"FB":12,"LW":-20,"RW":-20},
    description:"Defence wins. CBs+25, FBs+12. Wingers don't exist (-20). -5% global.",
    pitchPositions:[{pos:"GK",x:50,y:92},{pos:"CB",x:18,y:76},{pos:"CB",x:50,y:76},{pos:"CB",x:82,y:76},{pos:"FB",x:5,y:55},{pos:"FB",x:95,y:55},{pos:"CDM",x:50,y:50},{pos:"CM",x:30,y:36},{pos:"CM",x:70,y:36},{pos:"ST",x:30,y:17},{pos:"ST",x:70,y:17}] },
  { id:"3-4-3", name:"3-4-3", handSize:12, globalMult:1.08,
    slots:["CB","CB","CB","FB","FB","CM","CM","LW","ST","RW"],
    positionBonus:{"ST":20,"LW":15,"RW":15,"CB":-25},
    description:"All-out attack. Front 3 +15-20. CBs exposed (-25). +8% global.",
    pitchPositions:[{pos:"GK",x:50,y:92},{pos:"CB",x:20,y:76},{pos:"CB",x:50,y:76},{pos:"CB",x:80,y:76},{pos:"FB",x:8,y:50},{pos:"FB",x:92,y:50},{pos:"CM",x:35,y:38},{pos:"CM",x:65,y:38},{pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}] },
  { id:"4-2-3-1", name:"4-2-3-1", handSize:12, globalMult:1.02,
    slots:["CB","CB","FB","FB","CM","CM","CAM","LW","RW","ST"],
    positionBonus:{"CM":10,"CAM":25,"ST":-15},
    description:"Possession. CAM+25, CM+10. Lone ST isolated (-15). +2% global.",
    pitchPositions:[{pos:"GK",x:50,y:92},{pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},{pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},{pos:"CM",x:30,y:40},{pos:"CM",x:70,y:40},{pos:"CAM",x:50,y:30},{pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}] },
  { id:"4-5-1", name:"4-5-1", handSize:12, globalMult:0.98,
    slots:["CB","CB","FB","FB","CDM","CM","CM","LW","RW","ST"],
    positionBonus:{"CDM":15,"LW":20,"RW":20,"ST":-20,"CB":-5},
    description:"Counter. CDM+15, wingers+20. Lone ST isolated (-20). -2% global.",
    pitchPositions:[{pos:"GK",x:50,y:92},{pos:"CB",x:28,y:75},{pos:"CB",x:72,y:75},{pos:"FB",x:5,y:58},{pos:"FB",x:95,y:58},{pos:"CDM",x:50,y:50},{pos:"CM",x:30,y:34},{pos:"CM",x:70,y:34},{pos:"LW",x:12,y:17},{pos:"ST",x:50,y:12},{pos:"RW",x:88,y:17}] },
];

// CAMPAIGN
var CAMPAIGN_MATCHES = [
  { name:"Group Stage", opponent:"Wolves FC", targets:[200000,350000,500000], tier:"Match 1/5", intro:"Relegation battlers. Forwards can't finish — exploit set pieces." },
  { name:"Round of 16", opponent:"Inter Your-Nan", targets:[350000,500000,700000], tier:"Match 2/5", intro:"Mid-table side. Solid defence but slow at the back." },
  { name:"Quarter Final", opponent:"Borussia Mönchen-flapjack", targets:[500000,700000,900000], tier:"Match 3/5", intro:"European contenders. Press hard." },
  { name:"Semi Final", opponent:"Man City Oilers", targets:[700000,900000,1100000], tier:"Match 4/5", intro:"Title favourites. No obvious weakness." },
  { name:"THE FINAL", opponent:"Galácticos FC", targets:[900000,1100000,1500000], tier:"Match 5/5", intro:"The best in the world. Leave nothing on the pitch." },
];

// ELIGIBILITY + OOP
function isPlayerEligible(player, slotSpec) {
  if (player.position === 'GK' && slotSpec !== 'GK') return false;
  if (slotSpec === 'GK') return player.position === 'GK';
  return true;
}
function slotFieldPosition(slot) {
  if (typeof slot === 'string') return slot;
  if (Array.isArray(slot)) return slot[0];
  return (slot && slot.as) ? slot.as : 'ST';
}

var POSITION_GROUPS = { 'GK':['GK'],'CB':['CB','FB','CDM'],'FB':['FB','CB','CDM'],'CDM':['CDM','CB','CM'],'CM':['CM','CAM','CDM'],'CAM':['CAM','CM','ST'],'LW':['LW','RW','ST'],'RW':['RW','LW','ST'],'ST':['ST','LW','RW'] };
function getPositionPenalty(playerPos, fieldPos) {
  if (playerPos === fieldPos) return 1.0;
  if (playerPos === 'GK' || fieldPos === 'GK') return 0.0;
  var group = POSITION_GROUPS[playerPos] || [];
  if (group.indexOf(fieldPos) >= 0) return 0.9;
  return 0.7;
}
var ATTACKER_POSITIONS = new Set(["LW","RW","ST"]);

// SYNERGY HELPERS
function _playersAt(field, pos) { return field.filter(function(f){return f[1]===pos}).map(function(f){return f[0]}); }
function _bestAt(field, pos, stat) { var c = _playersAt(field, pos); return c.length ? c.reduce(function(a,b){return a[stat]>b[stat]?a:b}) : null; }

// DETECT SYNERGIES (phase-level accumulators)
function detectSynergies(field, synergyCards) {
  var result = { chips:0, add_mult:0, x_mult:1.0, nextCarryover:null, fired_details:[] };
  for (var si = 0; si < synergyCards.length; si++) {
    var syn = synergyCards[si];
    if (syn.persistent) continue;
    var tr = syn.trigger, eff = syn.effect, name = syn.name, contribs = [];
    function addC(p) { if (contribs.indexOf(p.name)<0) contribs.push(p.name); }
    var all = field.map(function(f){return f[0]});
    switch (syn.triggerType) {
      case 'clean_sheet': { var gk=_bestAt(field,tr.pos_a,tr.stat),cb=_bestAt(field,tr.pos_b,tr.stat); if(gk&&cb&&gk[tr.stat]+cb[tr.stat]>=tr.threshold){addC(gk);addC(cb);var v=eff.chips||eff.add_chips||0;result.chips+=v;result.fired_details.push({name:name,effect_type:'chips',value:v,contributors:contribs.slice()});} break; }
      case 'organised_defence': { var cbs=_playersAt(field,tr.positions[0]); if(cbs.length>=2){cbs.sort(function(a,b){return b[tr.stat]-a[tr.stat]});if(cbs[0][tr.stat]+cbs[1][tr.stat]>=tr.threshold){addC(cbs[0]);addC(cbs[1]);var v=eff.chips||eff.add_chips||0;result.chips+=v;result.fired_details.push({name:name,effect_type:'chips',value:v,contributors:contribs.slice()});}} break; }
      case 'defensive_duo': case 'midfield_engine': case 'covering_defender': case 'wingback_overlap': { var v=eff.add_mult||eff.chips||0; if(v>0){all.forEach(function(p){addC(p)});result.add_mult+=v;result.fired_details.push({name:name,effect_type:'add_mult',value:v,contributors:contribs.slice()});} break; }
      case 'overload': { var pc={}; for(var fi=0;fi<field.length;fi++){var p=field[fi][1];if(!pc[p])pc[p]=[];pc[p].push(field[fi][0]);} for(var pk in pc){if(pc[pk].length>=(tr.min_duplicates||2)){pc[pk].forEach(function(p){addC(p)});var v=eff.add_mult||eff.chips||0;result.add_mult+=v;result.fired_details.push({name:name+' ('+pk+')',effect_type:'add_mult',value:v,contributors:contribs.slice()});}} break; }
      case 'stretch_backline': case 'back_three': case 'target_man_release': case 'near_post_flick': case 'one_two': case 'overlap': { var v=eff.x_mult||eff.multiply||1.0; if(v>1.0){all.forEach(function(p){addC(p)});result.x_mult*=v;result.fired_details.push({name:name,effect_type:'x_mult',value:v,contributors:contribs.slice()});} break; }
      case 'route_one': case 'battering_ram': { var v=eff.chips||eff.add_chips||0; if(v>0){all.forEach(function(p){addC(p)});result.chips+=v;result.fired_details.push({name:name,effect_type:'chips',value:v,contributors:contribs.slice()});} break; }
      case 'double_pivot': { var cms=_playersAt(field,tr.positions[0]); if(cms.length>=2){var srt=cms.slice().sort(function(a,b){return b[tr.stat]-a[tr.stat]});if(srt[0][tr.stat]+srt[1][tr.stat]>=tr.threshold){srt.forEach(function(p){addC(p)});result.nextCarryover={type:'double_pivot',source_synergy:syn.name,chips:eff.chips||eff.add_chips||40,target_role:eff.target_role||'attacker'};result.fired_details.push({name:name+' (carryover)',effect_type:'carryover',value:eff.chips||eff.add_chips||40,contributors:contribs.slice()});}} break; }
      case 'set_piece_threat': { var v=eff.chips||eff.add_chips||0;result.chips+=v;result.fired_details.push({name:name,effect_type:'chips',value:v,contributors:contribs.slice()}); break; }
    }
  }
  return result;
}

// CALCULATE ROUND SCORE (Balatro formula)
function calculateRoundScore(field, synergyCards, formation, fatigue, carryover, persistentBuffs, shopBuffs, momentum) {
  if(!fatigue)fatigue={};if(!persistentBuffs)persistentBuffs={player_mult:{},player_add:{},position_mult:{},position_add:{},global_mult:1.0,global_add:0,fired_synergies:[]};if(!shopBuffs)shopBuffs={};if(!momentum)momentum=1.0;
  var syn=detectSynergies(field,synergyCards),synChips=syn.chips||0,addMult=syn.add_mult||0,xMult=syn.x_mult||1.0,nextCarry=syn.nextCarryover||null,fired=syn.fired_details||[];
  if(persistentBuffs.fired_synergies){for(var pi=0;pi<persistentBuffs.fired_synergies.length;pi++)fired.push({name:persistentBuffs.fired_synergies[pi]+' (persistent)',effect_type:'persistent',value:0,contributors:[]});}
  var pChips=0,breakdown=[];
  for(var fi=0;fi<field.length;fi++){var player=field[fi][0],pos=field[fi][1],base=calculateChips(player,pos),fat=fatigue[player.id]!==undefined?fatigue[player.id]:1.0,oop=getPositionPenalty(player.position,pos);
  var ppM=(persistentBuffs.player_mult&&persistentBuffs.player_mult[player.id])||1.0,ppA=(persistentBuffs.player_add&&persistentBuffs.player_add[player.id])||0;
  var posM=(persistentBuffs.position_mult&&persistentBuffs.position_mult[pos])||1.0,posA=(persistentBuffs.position_add&&persistentBuffs.position_add[pos])||0;
  var fB=(formation&&formation.positionBonus&&formation.positionBonus[pos])||0;
  var eff=Math.round((base+fB+posA+ppA)*fat*oop*ppM*posM);pChips+=eff;
  breakdown.push({player:player.name,position:pos,base_chips:base,add_chips:0,multiply:1.0,fatigue:fat,oop_penalty:oop,subtotal:eff});}
  var carryC=0;if(carryover){var bc=carryover.chips||carryover.add_chips||0;for(var ai=0;ai<field.length;ai++){if(ATTACKER_POSITIONS.has(field[ai][1])){carryC+=bc;fired.push({name:(carryover.source_synergy||'Carryover')+' (carryover)',effect_type:'carryover',value:bc,contributors:[]});break;}}}
  var shopC=shopBuffs.extra_chips||0,shopAM=shopBuffs.extra_add_mult||0,fM=formation?(formation.globalMult||1.0):1.0;
  var tC=pChips+synChips+carryC+shopC,tAM=1+addMult+shopAM,tXM=xMult*fM*momentum,total=Math.round(tC*tAM*tXM);
  var fS=[],sC={},sD={};for(var di=0;di<fired.length;di++){var fd=fired[di];fS.push(fd.name);sC[fd.name]=fd.contributors||[];sD[fd.name]=fd.effect_type==='chips'?'+'+fd.value+' chips':fd.effect_type==='add_mult'?'+'+fd.value+' mult':fd.effect_type==='x_mult'?'×'+fd.value:'';}
  return{total:total,breakdown:breakdown,player_chips:pChips,synergy_chips:synChips,carryover_chips:carryC,shop_chips:shopC,total_chips:tC,add_mult:tAM,x_mult:tXM,formation_mult:fM,momentum:momentum,phase_mult:1.0,subtotal_before_formation:Math.round(tC*tAM*xMult),fired_synergies:fS,fired_details:fired,next_carryover:nextCarry,synergy_contributors:sC,synergy_descriptions:sD};
}

function shuffleArray(arr){var a=arr.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var tmp=a[i];a[i]=a[j];a[j]=tmp;}return a;}
function dealPhases(){return shuffleArray(ALL_PHASES);}

// SYNERGIES
var SYNERGIES=[
  {id:"clean_sheet",name:"Clean Sheet",rarity:"common",persistent:false,triggerType:"clean_sheet",trigger:{pos_a:"GK",pos_b:"CB",stat:"def_",threshold:18},effectType:"add_chips",effect:{chips:20},description:"GK DEF + CB DEF ≥ 18: +20 chips"},
  {id:"organised_defence",name:"Organised Defence",rarity:"common",persistent:false,triggerType:"organised_defence",trigger:{positions:["CB","CB"],stat:"def_",threshold:18},effectType:"add_chips",effect:{chips:20},description:"2 CBs DEF ≥ 18: +20 chips"},
  {id:"wingback_overlap",name:"Wingback Overlap",rarity:"common",persistent:false,triggerType:"wingback_overlap",trigger:{pos_a:"FB",stat_a:"pac",pos_b:"CM",stat_b:"pas",threshold:15},effectType:"add_chips",effect:{chips:25},description:"FB PAC + CM PAS ≥ 15: +25 chips"},
  {id:"overload",name:"Overload",rarity:"common",persistent:false,triggerType:"overload",trigger:{min_duplicates:2},effectType:"add_chips",effect:{chips:15},description:"2+ same position: +15 chips each"},
  {id:"stretch_backline",name:"Stretch the Backline",rarity:"common",persistent:false,triggerType:"stretch_backline",trigger:{pos_a:"FB",stat_a:"pac",pos_b:"LW",stat_b:"pac",threshold:17},effectType:"multiply",effect:{x_mult:1.5},description:"FB PAC + LW PAC ≥ 17: ×1.5 mult"},
  {id:"route_one",name:"Route One",rarity:"uncommon",persistent:false,triggerType:"route_one",trigger:{pos_a:"CB",stat_a:"pas",pos_b:"ST",stat_b:"pac",threshold:14},effectType:"add_chips",effect:{chips:30},description:"CB PAS + ST PAC ≥ 14: +30 chips"},
  {id:"battering_ram",name:"Battering Ram",rarity:"common",persistent:false,triggerType:"battering_ram",trigger:{pos_a:"CB",stat_a:"def_",pos_b:"ST",stat_b:"atk",threshold:17},effectType:"add_chips",effect:{chips:20},description:"CB DEF + ST ATK ≥ 17: +20 chips"},
  {id:"defensive_duo",name:"Defensive Duo",rarity:"uncommon",persistent:false,triggerType:"defensive_duo",trigger:{stat:"def_",threshold:18},effectType:"add_chips",effect:{chips:25},description:"2 highest DEF ≥ 18: +25 chips"},
  {id:"back_three",name:"Back Three",rarity:"rare",persistent:false,triggerType:"back_three",trigger:{stat:"def_",threshold:7},effectType:"multiply",effect:{x_mult:1.3},description:"All 3 DEF ≥ 7: ×1.3 mult"},
  {id:"midfield_engine",name:"Midfield Engine",rarity:"common",persistent:false,triggerType:"midfield_engine",trigger:{positions:["CM","CM"],stat_a:"pas",stat_b:"def_",threshold:15},effectType:"add_chips",effect:{chips:25},description:"CM PAS + CM DEF ≥ 15: +25 chips"},
  {id:"double_pivot",name:"Double Pivot",rarity:"uncommon",persistent:false,triggerType:"double_pivot",trigger:{positions:["CM","CM"],stat:"pas",threshold:17},effectType:"carryover",effect:{chips:40,target_role:"attacker"},description:"2 CMs PAS ≥ 17: carryover +40 chips next phase"},
  {id:"trio",name:"Trio",rarity:"rare",persistent:false,triggerType:"trio",trigger:{position:"CM",stat:"pas",threshold:7},effectType:"chain_multiply",effect:{multipliers:[1.3,1.5,1.3]},description:"All 3 CMs PAS ≥ 7: ×1.3/×1.5/×1.3 chain"},
  {id:"covering_defender",name:"Covering Defender",rarity:"uncommon",persistent:false,triggerType:"covering_defender",trigger:{position:"CB",stat_a:"pac",threshold_a:7,stat_b:"def_",threshold_b:9},effectType:"add_chips",effect:{chips:25},description:"CB PAC≥7 + CB DEF≥9: +25 chips"},
  {id:"target_man_release",name:"Target Man Release",rarity:"uncommon",persistent:false,triggerType:"target_man_release",trigger:{pos_a:"ST",stat_a:"atk",winger_positions:["LW","RW"],stat_b:"pac",threshold:17},effectType:"multiply",effect:{x_mult:1.5},description:"ST ATK + winger PAC ≥ 17: ×1.5 mult"},
  {id:"near_post_flick",name:"Near Post Flick",rarity:"common",persistent:false,triggerType:"near_post_flick",trigger:{pos_a:"CAM",stat_a:"spc",pos_b:"ST",stat_b:"atk",threshold:16},effectType:"multiply",effect:{x_mult:1.5},description:"CAM SPC + ST ATK ≥ 16: ×1.5 mult"},
  {id:"one_two",name:"One-Two",rarity:"common",persistent:false,triggerType:"one_two",trigger:{pos_a:"CM",stat_a:"pas",pos_b:"ST",stat_b:"pac",threshold:15},effectType:"multiply",effect:{x_mult:1.5},description:"CM PAS + ST PAC ≥ 15: ×1.5 mult"},
  {id:"overlap",name:"Overlap",rarity:"common",persistent:false,triggerType:"overlap",trigger:{pos_a:"FB",stat_a:"pac",pos_b:"LW",stat_b:"pas",threshold:15},effectType:"multiply",effect:{x_mult:1.5},description:"FB PAC + LW PAS ≥ 15: ×1.5 mult"},
  {id:"set_piece_threat",name:"Set Piece Threat",rarity:"uncommon",persistent:false,triggerType:"set_piece_threat",trigger:{stat_a:"def_",threshold_a:8,stat_b:"spc",threshold_b:7},effectType:"add_chips",effect:{chips:35},description:"DEF≥8 + SPC≥7: +35 chips"},
  // Persistent synergies
  {id:"pace_in_behind",name:"Pace in Behind",rarity:"uncommon",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"pacey",min_count:5},effectType:"persistent_multiply",effect:{multiply:1.15,target_trait:"pacey"},description:"5+ pacey: all pacey ×1.15 each phase"},
  {id:"iron_wall",name:"Iron Wall",rarity:"uncommon",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"physical",min_count:3},effectType:"persistent_multiply",effect:{multiply:1.2,target_trait:"physical",fatigue_penalty:0.6},description:"3+ physical: ×1.2 + fatigue ×0.6"},
  {id:"leadership_council",name:"Leadership Council",rarity:"common",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"leader",min_count:3},effectType:"persistent_add",effect:{chips:15,target:"all"},description:"3+ leaders: all get +15 chips per phase"},
  {id:"tiki_taka_persistent",name:"Tiki-Taka",rarity:"uncommon",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"technical",min_count:3},effectType:"persistent_multiply",effect:{multiply:1.15,target_position:["CM","CDM","CAM"]},description:"3+ technical: midfielders ×1.15"},
  {id:"clinical_edge",name:"Clinical Edge",rarity:"common",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"clinical",min_count:2},effectType:"persistent_add",effect:{chips:15,target_position:["LW","RW","ST"]},description:"2+ clinical: attackers +15 chips"},
  {id:"double_destroyer",name:"Double Destroyer",rarity:"common",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"destroyer",min_count:2},effectType:"persistent_multiply",effect:{multiply:1.2,target_position:["CB","FB","CDM"]},description:"2+ destroyers: defenders ×1.2"},
  {id:"two_up_top",name:"Two Up Top",rarity:"rare",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"poacher",min_count:2},effectType:"persistent_multiply",effect:{multiply:1.3,target_position:["ST"]},description:"2+ poachers: STs ×1.3"},
  {id:"journeyman",name:"Journeyman",rarity:"rare",persistent:true,triggerType:"squad_trait_present",trigger:{trait:"journeyman"},effectType:"persistent_special",effect:{special:"fatigue_reset"},description:"Journeyman: once per match fatigue reset"},
  {id:"pace_and_power",name:"Pace & Power",rarity:"rare",persistent:true,triggerType:"squad_trait_combo",trigger:{traits:["pacey","physical"],min_count:2},effectType:"persistent_multiply",effect:{multiply:1.3,target_trait_combo:["pacey","physical"]},description:"2+ pacey+physical: ×1.3"},
  {id:"silent_killers",name:"Silent Killers",rarity:"uncommon",persistent:true,triggerType:"squad_trait_combo",trigger:{traits:["clinical","pacey"],min_count:2},effectType:"persistent_multiply",effect:{multiply:1.25,target_trait_combo:["clinical","pacey"]},description:"2+ clinical+pacey: ×1.25"},
  {id:"aerial_fortress",name:"Aerial Fortress",rarity:"uncommon",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"aerial",min_count:3},effectType:"persistent_multiply",effect:{multiply:1.2,target_position:["ST","CB","GK"]},description:"3+ aerial: ST/CB/GK ×1.2"},
  {id:"playmaker_network",name:"Playmaker Network",rarity:"common",persistent:true,triggerType:"squad_trait_count",trigger:{trait:"playmaker",min_count:3},effectType:"persistent_multiply",effect:{multiply:1.15,target_position:["CM","CAM","CDM"]},description:"3+ playmakers: midfield ×1.15"},
];

// SQUAD SYNERGY DETECTION (persistent buffs)
function detectSquadSynergies(squad, synergyCards) {
  var buffs = {fatigue_penalty:0.7,player_mult:{},player_add:{},position_mult:{},position_add:{},global_mult:1.0,global_add:0,journeyman_available:false,fired_synergies:[]};
  var traitToPlayers = {};
  for (var pi=0;pi<squad.length;pi++) {var p=squad[pi];for(var ti=0;ti<p.traits.length;ti++){var t=p.traits[ti];if(!traitToPlayers[t])traitToPlayers[t]=[];traitToPlayers[t].push(p);}}
  for (var si=0;si<synergyCards.length;si++) {var syn=synergyCards[si];if(!syn.persistent)continue;var tr=syn.trigger,eff=syn.effect;
    if(syn.triggerType==='squad_trait_count'){var m=traitToPlayers[tr.trait]||[];if(m.length>=(tr.min_count||1))applyPersistentEffect(buffs,syn,eff,m,squad);}
    else if(syn.triggerType==='squad_trait_present'){var m=traitToPlayers[tr.trait]||[];if(m.length>0)applyPersistentEffect(buffs,syn,eff,m,squad);}
    else if(syn.triggerType==='squad_trait_combo'){var m=squad.filter(function(p){return tr.traits.every(function(t){return p.traits.indexOf(t)>=0})});if(m.length>=(tr.min_count||1))applyPersistentEffect(buffs,syn,eff,m,squad);}
  }
  return buffs;
}
function applyPersistentEffect(buffs,syn,eff,matching,squad) {
  buffs.fired_synergies.push(syn.name);
  if(syn.effectType==='persistent_multiply'){var mult=eff.multiply||1.0;
    if(eff.target_trait){for(var i=0;i<squad.length;i++){var p=squad[i];if(p.traits.indexOf(eff.target_trait)>=0)buffs.player_mult[p.id]=(buffs.player_mult[p.id]||1.0)*mult;}}
    if(eff.target_trait_combo){for(var i=0;i<squad.length;i++){var p=squad[i];if(eff.target_trait_combo.every(function(t){return p.traits.indexOf(t)>=0}))buffs.player_mult[p.id]=(buffs.player_mult[p.id]||1.0)*mult;}}
    if(eff.target_position){for(var i=0;i<eff.target_position.length;i++){var pos=eff.target_position[i];buffs.position_mult[pos]=(buffs.position_mult[pos]||1.0)*mult;}}
    if(eff.fatigue_penalty!==undefined)buffs.fatigue_penalty=eff.fatigue_penalty;
  }else if(syn.effectType==='persistent_add'){var chips=eff.chips||0;
    if(eff.target==='all')buffs.global_add+=chips;
    if(eff.target_position){for(var i=0;i<eff.target_position.length;i++){var pos=eff.target_position[i];buffs.position_add[pos]=(buffs.position_add[pos]||0)+chips;}}
  }else if(syn.effectType==='persistent_special'){if(eff.special==='fatigue_reset')buffs.journeyman_available=true;}
}

// SQUAD BUILDER HELPERS
var ROLE_GROUPS = {GK:{positions:["GK"],min:1,label:"Goalkeeper"},Defenders:{positions:["CB","FB"],min:3,label:"Defenders (CB/FB)"},Midfielders:{positions:["CM","CDM","CAM"],min:3,label:"Midfielders (CM/CDM/CAM)"},Attackers:{positions:["ST","LW","RW"],min:2,label:"Attackers (ST/LW/RW)"}};
function checkMinimums(squad) {
  var missing=[],posCounts={};
  for(var i=0;i<squad.length;i++){var pos=squad[i].position;posCounts[pos]=(posCounts[pos]||0)+1;}
  for(var gn in ROLE_GROUPS){var cfg=ROLE_GROUPS[gn];var total=cfg.positions.reduce(function(s,p){return s+(posCounts[p]||0)},0);if(total<cfg.min)missing.push(cfg.label+' (have '+total+')');}
  if(squad.length<MIN_TOTAL)missing.push('11 players minimum (have '+squad.length+')');
  return missing;
}
function getAvailableSynergies(squad, allSynergies) {
  var available = [];
  for(var si=0;si<allSynergies.length;si++){var s=allSynergies[si];if(s.persistent)continue;var tr=s.trigger,canFire=false,involved=[];
    if(s.triggerType==='clean_sheet'){var gks=squad.filter(function(p){return p.position==='GK'}),cbs=squad.filter(function(p){return p.position==='CB'});for(var gi=0;gi<gks.length;gi++){for(var ci=0;ci<cbs.length;ci++){if(gks[gi].def_+cbs[ci].def_>=tr.threshold){canFire=true;involved=[gks[gi].name,cbs[ci].name];break;}}if(canFire)break;}}
    else if(s.triggerType==='stretch_backline'){var fbs=squad.filter(function(p){return p.position==='FB'}),lws=squad.filter(function(p){return p.position==='LW'});for(var fi=0;fi<fbs.length;fi++){for(var li=0;li<lws.length;li++){if(fbs[fi].pac+lws[li].pac>=tr.threshold){canFire=true;involved=[fbs[fi].name,lws[li].name];break;}}if(canFire)break;}}
    else if(s.triggerType==='route_one'){var cbs2=squad.filter(function(p){return p.position==='CB'}),sts=squad.filter(function(p){return p.position==='ST'});for(var ci=0;ci<cbs2.length;ci++){for(var mi=0;mi<sts.length;mi++){if(cbs2[ci].pas+sts[mi].pac>=tr.threshold){canFire=true;involved=[cbs2[ci].name,sts[mi].name];break;}}if(canFire)break;}}
    else if(s.triggerType==='battering_ram'){var cbs3=squad.filter(function(p){return p.position==='CB'}),sts2=squad.filter(function(p){return p.position==='ST'});for(var ci=0;ci<cbs3.length;ci++){for(var mi=0;mi<sts2.length;mi++){if(cbs3[ci].def_+sts2[mi].atk>=tr.threshold){canFire=true;involved=[cbs3[ci].name,sts2[mi].name];break;}}if(canFire)break;}}
    else if(s.triggerType==='target_man_release'){var sts3=squad.filter(function(p){return p.position==='ST'}),wingers=squad.filter(function(p){return p.position==='LW'||p.position==='RW'});for(var sti=0;sti<sts3.length;sti++){for(var wi=0;wi<wingers.length;wi++){if(sts3[sti].atk+wingers[wi].pac>=tr.threshold){canFire=true;involved=[sts3[sti].name,wingers[wi].name];break;}}if(canFire)break;}}
    else if(s.triggerType==='set_piece_threat'){var defH=squad.filter(function(p){return p.def_>=tr.threshold_a}),spcH=squad.filter(function(p){return p.spc>=tr.threshold_b});for(var di=0;di<defH.length;di++){for(var spi=0;spi<spcH.length;spi++){if(defH[di].id!==spcH[spi].id){canFire=true;involved=[defH[di].name,spcH[spi].name];break;}}if(canFire)break;}}
    else if(s.triggerType==='defensive_duo'){var sorted=squad.slice().sort(function(a,b){return b.def_-a.def_});if(sorted.length>=2&&sorted[0].def_+sorted[1].def_>=tr.threshold){canFire=true;involved=[sorted[0].name,sorted[1].name];}}
    if(canFire)available.push({name:s.name,desc:s.description,players:involved});}
  return available;
}
