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
    // fatiguePenalty deprecated — energy system uses fixed tiered multipliers
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
      // Energy system uses fixed tiers; iron_wall no longer modifies fatigue penalty
    }
  }

  return buffs;
}

/**
 * ATTACKER_POSITIONS set for carryover targeting
 */

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
    var fatigue = getEnergyMultiplier(player.id);
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

  var momentum = 1.0;
  // Momentum: earned by hitting ≥15% of round target in previous phase
  if (G.phaseIdx > 0 && G.phaseResults && G.phaseResults.length > 0) {
    var prevResult = G.phaseResults[G.phaseResults.length - 1];
    var target = (CAMPAIGN_MATCHES[G.matchIdx] && CAMPAIGN_MATCHES[G.matchIdx].targets)
      ? CAMPAIGN_MATCHES[G.matchIdx].targets[G.roundIdx] : 9999;
    if (target && prevResult.score >= target * 0.15) {
      momentum = Math.min(G.momentum + 0.15, 1.3);
    }
  }
  G.momentum = momentum;
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
          synResult.details.push({
            name: 'Combo: ' + chain.desc,
            type: chain.value >= 1.0 ? 'combo_xmult' : 'combo_penalty',
            value: chain.value,
            contributors: []
          });
        } else if (chain.effect === 'addChips') {
          synChips += chain.value;
          synResult.details.push({
            name: 'Combo: ' + chain.desc,
            type: chain.value >= 0 ? 'combo_chips' : 'combo_penalty',
            value: chain.value,
            contributors: []
          });
        } else if (chain.effect === 'fatigueRecovery') {
          // Fatigue recovery handled separately
          synResult.details.push({
            name: 'Combo: ' + chain.desc,
            type: 'combo_recovery',
            value: chain.value,
            contributors: []
          });
        }
      } else {
        // No matching chain — apply mild penalty for bad sequencing
        phaseMult = COMBO_NO_MATCH_PENALTY || 0.95;
        synResult.details.push({
          name: 'Combo: No tactical link — ×' + (COMBO_NO_MATCH_PENALTY || 0.95).toFixed(2),
          type: 'combo_penalty',
          value: COMBO_NO_MATCH_PENALTY || 0.95,
          contributors: []
        });
      }
    }
  }

  // Apply opponent tactical modifier
  var oppTacticalMult = 1.0;
  if (currPhase) {
    oppTacticalMult = getOpponentTacticalMultiplier(currPhase.tag, G.phaseIdx);
  } else if (phaseId) {
    // Find the phase to get its tag
    for (var pi = 0; pi < ALL_PHASES.length; pi++) {
      if (ALL_PHASES[pi].id === phaseId) {
        oppTacticalMult = getOpponentTacticalMultiplier(ALL_PHASES[pi].tag, G.phaseIdx);
        break;
      }
    }
  }
  phaseMult *= oppTacticalMult;

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
  // Deal 5 of 8 — player picks 3, creating tension
  return shuffled.slice(0, 5).map(function(p) { return p.id; });
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
 * useEnergy(playerId)
 * Consumes 1 energy for a player. Returns the new multiplier.
 * Energy tiers: 3=FRESH(1.0), 2=TIRED(0.85), 1=EXHAUSTED(0.65), 0=INJURED(0.0)
 * 25% injury risk when used at EXHAUSTED.
 */
function useEnergy(playerId) {
  if (!G.energy[playerId]) G.energy[playerId] = {current: 3, injured: false};
  var e = G.energy[playerId];
  if (e.injured) return 0.0;
  if (e.current <= 1) {
    // Risk injury when using at exhausted
    if (Math.random() < 0.25) {
      e.injured = true;
      e.current = 0;
      return 0.0;
    }
  }
  e.current = Math.max(0, e.current - 1);
  G.roundUsedPlayers[playerId] = true;
  return getEnergyMultiplier(playerId);
}

/**
 * getEnergyMultiplier(playerId)
 * Returns current energy multiplier for a player.
 */
function getEnergyMultiplier(playerId) {
  if (!G.energy[playerId]) return 1.0;
  var e = G.energy[playerId];
  if (e.injured) return 0.0;
  return {3: 1.0, 2: 0.85, 1: 0.65, 0: 0.0}[e.current] || 1.0;
}

/** @deprecated — use useEnergy() instead */
function applyFatigue(playerId) {
  return useEnergy(playerId);
}

/**
 * recoverEnergy()
 * Bench recovery between rounds: unused players recover 1 energy.
 * Used players (in roundUsedPlayers) do NOT recover.
 */
function recoverEnergy() {
  for (var pid in G.energy) {
    if (G.energy.hasOwnProperty(pid)) {
      if (!G.roundUsedPlayers[pid]) {
        var e = G.energy[pid];
        if (!e.injured) {
          e.current = Math.min(3, e.current + 1);
        }
      }
    }
  }
  G.roundUsedPlayers = {}; // Reset for next round
}

/** @deprecated — use recoverEnergy() instead */
function recoverFatigue(amount) {
  recoverEnergy();
}

/**
 * buyShopItem(itemId)
 * Deducts morale, adds buff to shopBuffs.
 * Item definitions are inline.
 * Returns true if purchased, false if insufficient morale.
 */
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
    G.energy = {};
  }
  if (eff.type === 'morale') {
    G.morale += eff.value;
  }

  return true;
}

/**
 * resetRound()
 * Resets phase-level state between rounds.
 * NOTE: This function is NOT currently called in the SPA flow.
 *   The startRound() function handles round transitions.
 *   If called, it MUST NOT reset roundIdx (that's the caller's responsibility).
 */
function resetRound() {
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
  recoverFatigue(0.3);
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
      energy: G.energy,
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
    G.energy = saveData.energy || {};
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
  G.energy = {};
  G.roundUsedPlayers = {};
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

  // Initialize all squad players' energy (3 uses per match, tiered penalties)
  G.energy = {};
  G.roundUsedPlayers = {};
  for (var i = 0; i < G.selectedIds.length; i++) {
    G.energy[G.selectedIds[i]] = {current: 3, injured: false};
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
  recoverFatigue(0.3);
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

/* ===================================================================
   SECTION 11 — DRAFTING SYSTEM
   Formation-first: GK → CB → FB → MID → ATK
   =================================================================== */

var DRAFT_ORDER = [
  { group: 'GK',  count: 1, label: 'Pick your Goalkeeper (1)' },
  { group: 'DEF', count: 4, label: 'Pick 4 Defenders \u2014 any mix of CBs & FBs' },
  { group: 'MID', count: 3, label: 'Pick 3 Midfielders' },
  { group: 'ATK', count: 2, label: 'Pick 2 Attackers' },
];

/** Group players by position for drafting */
function groupPlayersByDraftGroup(players) {
  var groups = { GK: [], DEF: [], MID: [], ATK: [] };
  var posMap = {
    GK: 'GK',
    CB: 'DEF', FB: 'DEF',
    CM: 'MID', CDM: 'MID', CAM: 'MID',
    ST: 'ATK', LW: 'ATK', RW: 'ATK'
  };
  for (var i = 0; i < players.length; i++) {
    var p = players[i];
    var g = posMap[p.position];
    if (g) groups[g].push(p);
  }
  return groups;
}

/** Shuffle array in place (Fisher-Yates) */
function shuffleArray(arr, seed) {
  // Simple deterministic shuffle if seed provided, else Math.random
  var rng = seed !== undefined ? seededRandom(seed) : Math.random;
  for (var i = arr.length - 1; i > 0; i--) {
    var j = Math.floor(rng() * (i + 1));
    var tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;
  }
  return arr;
}

var _seedState = 0;
function seededRandom(seed) {
  return function() {
    seed = (seed * 16807 + 0) % 2147483647;
    return (seed - 1) / 2147483646;
  };
}

/**
 * generateDraftPicks(players, seed)
 * Create a draft sequence from the player pool.
 */
function generateDraftPicks(players, seed) {
  var groups = groupPlayersByDraftGroup(players);
  for (var g in groups) {
    shuffleArray(groups[g], seed);
  }

  var picks = [];
  for (var ri = 0; ri < DRAFT_ORDER.length; ri++) {
    var rd = DRAFT_ORDER[ri];
    var pool = groups[rd.group];  // Show ALL players in this group
    if (pool.length === 0) continue;
    picks.push({
      group: rd.group,
      count: rd.count,
      pool: pool,
      label: rd.label,
    });
  }

  // Store in G
  G.draftPicks = picks;
  G.draftPickIdx = 0;
  G.draftedPlayers = [];
  return picks;
}

/**
 * getCurrentDraftPick()
 * Returns the current draft pick or null if done.
 */
function getCurrentDraftPick() {
  if (!G.draftPicks || G.draftPickIdx >= G.draftPicks.length) return null;
  return G.draftPicks[G.draftPickIdx];
}

/**
 * confirmDraftPick(chosenIds)
 * Confirm the current pick with chosen player IDs. Advances to next.
 */
function confirmDraftPick(chosenIds) {
  var pick = getCurrentDraftPick();
  if (!pick) return { done: true, error: 'No active pick' };
  if (chosenIds.length !== pick.count) return { done: false, error: 'Must pick exactly ' + pick.count };

  // Validate all chosen are in pool
  var poolIds = pick.pool.map(function(p) { return p.id; });
  for (var i = 0; i < chosenIds.length; i++) {
    if (poolIds.indexOf(chosenIds[i]) < 0) {
      return { done: false, error: 'Invalid selection' };
    }
  }

  // Add to drafted players
  for (var i = 0; i < chosenIds.length; i++) {
    var p = getPlayerById(chosenIds[i]);
    if (p) G.draftedPlayers.push(p);
  }

  G.draftPickIdx++;
  return { done: G.draftPickIdx >= G.draftPicks.length };
}

/**
 * isDraftComplete()
 */
function isDraftComplete() {
  return !G.draftPicks || G.draftPickIdx >= G.draftPicks.length;
}

/**
 * getDraftProgress()
 * Returns { current: N, total: N, pct: N }
 */
function getDraftProgress() {
  if (!G.draftPicks || G.draftPicks.length === 0) return { current: 0, total: 0, pct: 100 };
  return {
    current: G.draftPickIdx,
    total: G.draftPicks.length,
    pct: Math.round((G.draftPickIdx / G.draftPicks.length) * 100)
  };
}
