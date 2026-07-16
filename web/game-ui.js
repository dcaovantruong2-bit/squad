/**
 * SQUAD — Game UI (rendering + state + events)
 * Extracted from game.html inline scripts
 * Depends on game-engine.js being loaded first
 */

// ═══════════════════════════════════════════════════════════════════
// VISUAL ANIMATIONS
// ═══════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════
  // VISUAL ANIMATIONS
  // ═══════════════════════════════════════════════════════════════════

  /** Cascade the phase result score counting up from 0 */
  function animateScoreCascade(finalScore, durationMs) {
    const el = document.getElementById('pr-score');
    const start = performance.now();
    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(elapsed / durationMs, 1);
      // Ease-out cubic for satisfying deceleration
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = Math.round(eased * finalScore);
      el.textContent = current;
      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        el.textContent = finalScore;
        el.classList.remove('score-cascading');
        // Trigger pulse glow at end
        el.classList.add('score-cascading');
        setTimeout(function() { el.classList.remove('score-cascading'); }, 800);
      }
    }
    el.classList.add('score-cascading');
    requestAnimationFrame(tick);
  }

// ═══════════════════════════════════════════════════════════════════
// GAME STATE + RENDERING + EVENTS
// ═══════════════════════════════════════════════════════════════════

// ═══════════════════════════════════════════════════════════════════
  // GAME STATE — all in memory, no localStorage needed
  // ═══════════════════════════════════════════════════════════════════

  const G = {
    // Squad
    selectedIds: new Set(),
    squad: [],          // built from selectedIds when confirmed

    // Formation
    formation: null,

    // Campaign
    matchIdx: 0,
    matchResults: [],   // [{won, opponent}]
    roundWins: [false, false, false],
    roundsWon: 0,
    roundsLost: 0,

    // Current round
    round: 0,
    roundScore: 0,
    roundPhases: [],
    phaseIdx: 0,

    // Current phase
    phasePlacement: {}, // slotIdx -> playerId
    activeSlot: null,

    // Fatigue
    fatigue: {},
    carryover: null,
    journeymanUsed: false,

    // Shop
    morale: 0,
    shopBuffs: {},

    // Phase fatigue + opponent adjustments
    phaseFatigue: {},
    opponentAdjustments: {},
    momentum: 1.0,

    // Persistent synergies
    persistentBuffs: null,
  };

  // ═══════════════════════════════════════════════════════════════════
  // SCREEN MANAGEMENT
  // ═══════════════════════════════════════════════════════════════════

  function showScreen(id) {
    document.querySelectorAll('.game-screen').forEach(s => s.classList.remove('active'));
    const screen = document.getElementById('screen-' + id);
    if (screen) screen.classList.add('active');
    window.scrollTo(0, 0);

    // Render the screen
    switch(id) {
      case 'title': break;
      case 'squad': renderSquadBuilder(); break;
      case 'formation': renderFormationSelect(); break;
      case 'match': renderMatch(); break;
      case 'phase-result': renderPhaseResult(); break;
      case 'round-result': renderRoundResult(); break;
      case 'shop': renderShop(); break;
      case 'campaign': renderCampaignComplete(); break;
      case 'phase-select': renderPhaseCards(); break;
    }
  }

  function showToast(msg) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = msg;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2500);
  }

  // ═══════════════════════════════════════════════════════════════════
  // TITLE SCREEN
  // ═══════════════════════════════════════════════════════════════════

  document.getElementById('start-btn').addEventListener('click', () => showScreen('squad'));

  // ─── Tutorial Modal ───────────────────────────────────────────────
  function showTutorial() {
    const overlay = document.getElementById('tut-overlay');
    overlay.style.display = 'flex';
    document.body.style.overflow = 'hidden';
  }
  function closeTutorial(event) {
    if (event && event.target !== event.currentTarget) return; // only close when clicking backdrop or close button
    const overlay = document.getElementById('tut-overlay');
    overlay.style.display = 'none';
    document.body.style.overflow = '';
  }

  // ─── Quick Start — auto-draft random valid squad ───────────────────
  document.getElementById('quick-start-btn').addEventListener('click', quickStartGame);

  function quickStartGame() {
    // Clear previous state
    G.selectedIds = new Set();
    G.squad = [];

    // Shuffle PLAYERS copy
    const shuffled = shuffleArray(PLAYERS);

    // Determine required positions
    const need = { GK:1, DEF:3, MID:3, ATT:2 };
    const posGroups = { GK:['GK'], DEF:['CB','FB'], MID:['CDM','CM','CAM'], ATT:['ST','LW','RW'] };
    const picks = [];
    let totalCost = 0;

    // Helper: pick best available player for a position group, respecting budget
    function pickForGroup(group, count) {
      const allowed = posGroups[group];
      let remaining = [];
      for (let pi = 0; pi < shuffled.length; pi++) {
        if (picks.includes(shuffled[pi].id)) continue;
        if (allowed.includes(shuffled[pi].position)) {
          remaining.push(shuffled[pi]);
        }
      }
      // Sort by cost descending to get best players first, but respect budget
      remaining.sort((a, b) => calcCost(b) - calcCost(a));
      const taken = [];
      for (let ri = 0; ri < remaining.length && taken.length < count; ri++) {
        const p = remaining[ri];
        const c = calcCost(p);
        const wouldBe = totalCost + c;
        if (wouldBe <= BUDGET) {
          taken.push(p.id);
          totalCost += c;
        }
      }
      return taken;
    }

    // Step 1: pick required minimums
    picks.push(...pickForGroup('GK', 1));
    picks.push(...pickForGroup('DEF', 3));
    picks.push(...pickForGroup('MID', 3));
    picks.push(...pickForGroup('ATT', 2));

    // Step 2: fill remaining slots up to 12 with best affordable players
    const remainingSlots = Math.min(4, 12 - picks.length);
    if (remainingSlots > 0) {
      // Collect all unpicked players
      const unpicked = [];
      for (let pi = 0; pi < shuffled.length; pi++) {
        if (!picks.includes(shuffled[pi].id)) {
          unpicked.push(shuffled[pi]);
        }
      }
      unpicked.sort((a, b) => calcCost(b) - calcCost(a));
      for (let ri = 0; ri < unpicked.length && picks.length < 12; ri++) {
        const p = unpicked[ri];
        const c = calcCost(p);
        if (totalCost + c <= BUDGET && !picks.includes(p.id)) {
          picks.push(p.id);
          totalCost += c;
        }
      }
    }

    // Fallback: if we still have < 11, just force-pick the cheapest remaining (probably won't happen with 40+ players)
    if (picks.length < MIN_TOTAL) {
      for (let pi = 0; pi < shuffled.length && picks.length < MIN_TOTAL; pi++) {
        if (!picks.includes(shuffled[pi].id)) {
          picks.push(shuffled[pi].id);
          totalCost += calcCost(shuffled[pi]);
        }
      }
    }

    // Set selectedIds
    picks.forEach(id => G.selectedIds.add(id));

    // Build squad
    G.squad = PLAYERS.filter(p => G.selectedIds.has(p.id));

    // Reset match state (same as confirm-squad-btn handler)
    G.fatigue = {};
    G.carryover = null;
    G.journeymanUsed = false;
    G.matchIdx = 0;
    G.matchResults = [];
    G.roundWins = [false, false, false];
    G.roundsWon = 0;
    G.roundsLost = 0;
    G.round = 0;

    // Compute persistent synergies
    G.persistentBuffs = detectSquadSynergies(G.squad, SYNERGIES);

    // Pick best formation (highest fill percentage)
    const fits = FORMATIONS.map(f => ({
      id: f.id,
      ...getFormationFit(f, G.squad)
    }));
    const maxPct = Math.max(...fits.map(f => f.pct));
    const bestFormation = FORMATIONS.find(f => fits.find(fi => fi.id === f.id && fi.pct === maxPct));
    G.formation = bestFormation || FORMATIONS[0];

    // Now navigate to match (same flow as confirm-formation-btn click handler)
    G.round = 0;
    G.roundsWon = 0;
    G.roundsLost = 0;
    G.roundWins = [false, false, false];
    G.fatigue = {};
    G.carryover = null;
    G.journeymanUsed = false;
    G.roundScore = 0;
    G.phaseIdx = 0;
    G.phasePlacement = {};
    G.activeSlot = null;
    G.morale = 0;
    G.shopBuffs = {};
    G.phaseFatigue = {};
    for (var pfi = 0; pfi < ALL_PHASES.length; pfi++) {
      G.phaseFatigue[ALL_PHASES[pfi].id] = 1.0;
    }
    G.phaseHand = dealPhases();
    G.selectedPhases = [];

    showToast('⚡ Random squad built!');
    startPhaseSelection();
  }

  // ═══════════════════════════════════════════════════════════════════
  // SQUAD BUILDER — Compact List + Pill Grid
  // ═══════════════════════════════════════════════════════════════════

  let squadFilter = 'ALL';
  let subFilter = null; // null = show all in group, or specific position like 'CB'

  const GROUP_POS = { ALL:null, GK:['GK'], DEF:['CB','FB'], MID:['CDM','CM','CAM'], ATT:['ST','LW','RW'] };
  const SUB_TABS = { ALL:[], GK:[], DEF:['CB','FB'], MID:['CDM','CM','CAM'], ATT:['ST','LW','RW'] };

  function renderSquadBuilder() {
    // Position tabs
    const positions = ['ALL', 'GK', 'DEF', 'MID', 'ATT'];
    document.getElementById('pos-tabs').innerHTML = positions.map(p =>
      `<div class="pos-tab ${p === squadFilter ? 'active' : ''}" onclick="filterSquad('${p}')">${p}</div>`
    ).join('');

    // Sub-tabs (only for DEF/MID/ATT)
    const subs = SUB_TABS[squadFilter] || [];
    const subTabsEl = document.getElementById('sub-tabs');
    if (subs.length > 0) {
      subTabsEl.innerHTML = `<div class="sub-tab ${!subFilter ? 'active' : ''}" onclick="filterSub(null)">ALL ${squadFilter}</div>` +
        subs.map(s => `<div class="sub-tab ${subFilter === s ? 'active' : ''}" onclick="filterSub('${s}')">${s}</div>`).join('');
      subTabsEl.style.display = 'flex';
    } else {
      subTabsEl.innerHTML = '';
      subTabsEl.style.display = 'none';
    }

    // Filter players by position group + sub-filter
    const allowed = GROUP_POS[squadFilter];
    let filtered = allowed ? PLAYERS.filter(p => allowed.includes(p.position)) : PLAYERS;
    if (subFilter) {
      filtered = filtered.filter(p => p.position === subFilter);
    }

    // Player card grid with stat bars
    const statKeys = ['atk','pac','pas','def_','spc'];
    const statNames = ['ATK','PAC','PAS','DEF','SPC'];
    const statColors = ['atk','pac','pas','def','spc'];

    document.getElementById('player-grid').innerHTML = filtered.map(p => {
      const sel = G.selectedIds.has(p.id);
      const cost = calcCost(p);
      const statsHtml = statKeys.map((k, i) =>
        `<div class="pc-stat">
          <span class="pc-stat-label">${statNames[i]}</span>
          <div class="pc-stat-bar"><div class="pc-stat-fill ${statColors[i]}" style="width:${p[k]*10}%"></div></div>
          <span class="pc-stat-val ${statColors[i]}">${p[k]}</span>
        </div>`
      ).join('');
      return `<div class="player-card${sel ? ' selected' : ''}" onclick="toggleSquadPlayer('${p.id}')" data-od-id="card-${p.id}">
        <div class="pc-header">
          <span class="pc-pos ${p.position}">${p.position}</span>
          <span class="pc-name">${p.name}</span>
          <span class="pc-cost">${cost}</span>
        </div>
        <div class="pc-stats">${statsHtml}</div>
        <div class="pc-traits">${p.traits.join(' · ')}</div>
        <div class="pc-chips" title="${p.position}: ${FORMULA_TEXT[p.position] || ''}">
          <span style="font-size:10px;color:var(--gold)">♣ ${calculateChips(p, p.position)}</span>
          <span style="font-size:8px;color:var(--muted)">${p.position} · ${FORMULA_TEXT[p.position] || ''}</span>
        </div>
      </div>`;
    }).join('');

    updateSquadSummary();
  }

  function filterSquad(pos) {
    squadFilter = pos;
    subFilter = null; // reset sub-filter when switching groups
    renderSquadBuilder();
  }

  function filterSub(pos) {
    subFilter = pos;
    renderSquadBuilder();
  }

  function toggleSquadPlayer(id) {
    if (G.selectedIds.has(id)) {
      G.selectedIds.delete(id);
    } else {
      if (G.selectedIds.size >= 12) { showToast('Max 12 players! Remove one first.'); return; }
      G.selectedIds.add(id);
    }
    renderSquadBuilder();
  }

  function getPillGroup(player) {
    if (player.position === 'GK') return 'GK';
    if (['CB','FB'].includes(player.position)) return 'DEF';
    if (['CM','CDM','CAM'].includes(player.position)) return 'MID';
    return 'ATT';
  }

  function getOpenSlots(group) {
    const selected = PLAYERS.filter(p => G.selectedIds.has(p.id));
    const counts = {};
    for (const p of selected) {
      const g = getPillGroup(p);
      counts[g] = (counts[g] || 0) + 1;
    }
    const perGroup = { GK:1, DEF:4, MID:4, ATT:4 };
    return Math.max(0, (perGroup[group] || 0) - (counts[group] || 0));
  }

  function getGroupReqs(selected) {
    const posCounts = {};
    for (const p of selected) posCounts[p.position] = (posCounts[p.position] || 0) + 1;
    const defCount = (posCounts['CB']||0) + (posCounts['FB']||0);
    const midCount = (posCounts['CM']||0) + (posCounts['CDM']||0) + (posCounts['CAM']||0);
    const attCount = (posCounts['ST']||0) + (posCounts['LW']||0) + (posCounts['RW']||0);
    const gkCount = posCounts['GK']||0;
    return {
      GK: { have: gkCount, need: 1, label: 'GK ≥ 1' },
      DEF: { have: defCount, need: 3, label: 'DEF ≥ 3' },
      MID: { have: midCount, need: 3, label: 'MID ≥ 3' },
      ATT: { have: attCount, need: 2, label: 'ATT ≥ 2' },
    };
  }

  function updateSquadSummary() {
    const selected = PLAYERS.filter(p => G.selectedIds.has(p.id));
    const totalCost = selected.reduce((s, p) => s + calcCost(p), 0);
    const overBudget = totalCost > BUDGET;
    const budgetPct = Math.min(100, (totalCost / BUDGET) * 100);

    // Budget
    document.getElementById('budget-used').textContent = totalCost;
    const fill = document.getElementById('budget-fill');
    fill.style.width = budgetPct + '%';
    fill.className = 'budget-fill' + (overBudget ? ' over' : '');
    document.getElementById('budget-used').className = 'num' + (overBudget ? ' over' : '');
    document.getElementById('squad-count').textContent = selected.length + '/12';
    document.getElementById('squad-cost-display').textContent = 'Cost: ' + totalCost;

    // Group pills
    const orderedGroups = ['GK','DEF','MID','ATT'];
    const groupLabels = { GK:'GK', DEF:'DEF', MID:'MID', ATT:'ATT' };
    const groupColors = { GK:'GK', DEF:'DEF', MID:'MID', ATT:'ATT' };

    let pillsHtml = '';
    const grouped = { GK:[], DEF:[], MID:[], ATT:[] };
    for (const p of selected) {
      const g = getPillGroup(p);
      grouped[g].push(p);
    }

    for (const g of orderedGroups) {
      const openCount = getOpenSlots(g);
      const count = grouped[g].length;
      // Group label + status
      const maxNeeded = { GK:1, DEF:4, MID:4, ATT:4 };
      const full = count >= maxNeeded[g];

      pillsHtml += '<div class="pill-line">' +
        '<span class="pill-label pill-label-' + groupColors[g] + '">' + groupLabels[g] + '</span>';

      // Filled pills
      for (const p of grouped[g]) {
        const cost = calcCost(p);
        pillsHtml += '<span class="pill pill-' + groupColors[g] + '" onclick="toggleSquadPlayer(\'' + p.id + '\')" title="Click to remove">' +
          p.name.split(' ').pop() + '<span class="pill-cost">' + cost + '</span>' +
          '<span class="pill-rm">×</span>' +
        '</span>';
      }

      // Open slots
      for (let i = 0; i < openCount; i++) {
        pillsHtml += '<span class="pill-open">+ OPEN</span>';
      }

      // Status badge
      const reqs = getGroupReqs(selected);
      const r = reqs[g === 'DEF' ? 'DEF' : (g === 'MID' ? 'MID' : (g === 'ATT' ? 'ATT' : 'GK'))];
      const met = r && r.have >= r.need;
      if (count > 0) {
        pillsHtml += '<span class="pill-line-status ' + (met ? 'met' : 'unmet') + '">' +
          (met ? '✓×' + Math.min(count, maxNeeded[g]) : '✗ need ' + r.need) +
        '</span>';
      }

      pillsHtml += '</div>';
    }

    document.getElementById('squad-pills').innerHTML = pillsHtml;

    // Requirements strip
    const missing = checkMinimums(selected);
    const reqs = getGroupReqs(selected);
    const allReqs = [
      { label: 'GK ≥ 1', met: reqs.GK.have >= 1 },
      { label: 'DEF ≥ 3', met: reqs.DEF.have >= 3 },
      { label: 'MID ≥ 3', met: reqs.MID.have >= 3 },
      { label: 'ATT ≥ 2', met: reqs.ATT.have >= 2 },
      { label: 'Total ≥ 10', met: selected.length >= 10 },
      { label: 'Budget ≤ ' + BUDGET, met: !overBudget },
    ];
    document.getElementById('req-strip').innerHTML = allReqs.map(r =>
      '<div class="req-badge ' + (r.met ? 'met' : 'unmet') + '">' + (r.met ? '✓' : '✗') + ' ' + r.label + '</div>'
    ).join('');

    // Formation fit preview
    renderFormationFit();

    // Error box hidden
    document.getElementById('squad-error').classList.remove('visible');
  }

  function renderFormationFit() {
    // Calculate fit for all formations based on current draft
    const selected = PLAYERS.filter(p => G.selectedIds.has(p.id));
    if (selected.length === 0) {
      document.getElementById('form-fit-preview').innerHTML = '';
      return;
    }
    const fits = FORMATIONS.map(f => ({ id: f.id, name: f.name, pct: getFormationFit(f, selected).pct }));
    const maxPct = Math.max(...fits.map(f => f.pct));
    const bestIds = fits.filter(f => f.pct === maxPct).map(f => f.id);
    const html = '<span class="form-fit-label">Best Fit</span>' +
      fits.map(f => {
        const isBest = bestIds.includes(f.id);
        return '<span class="form-fit-badge' + (isBest ? ' best' : '') + '" onclick="showScreen(\'formation\')" title="' + f.name + ' fit: ' + f.pct + '%">' +
          f.name + ' <span class="pct">' + f.pct + '%</span>' +
        '</span>';
      }).join('');
    document.getElementById('form-fit-preview').innerHTML = html;
  }

  // Confirm squad button — validates on click
  document.getElementById('confirm-squad-btn').addEventListener('click', () => {
    const selected = PLAYERS.filter(p => G.selectedIds.has(p.id));
    const missing = checkMinimums(selected);
    const totalCost = selected.reduce((s, p) => s + calcCost(p), 0);
    const errors = [...missing];
    if (totalCost > BUDGET) errors.push('Over budget: ' + totalCost + '/' + BUDGET);

    if (errors.length > 0) {
      const errEl = document.getElementById('squad-error');
      errEl.textContent = '⚠ ' + errors.join(' · ');
      errEl.classList.add('visible');
      errEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    document.getElementById('squad-error').classList.remove('visible');
    G.squad = selected;
    G.fatigue = {};
    G.carryover = null;
    G.journeymanUsed = false;
    G.matchIdx = 0;
    G.matchResults = [];
    G.roundWins = [false, false, false];
    G.roundsWon = 0;
    G.roundsLost = 0;
    G.round = 0;

    // Compute persistent synergies
    G.persistentBuffs = detectSquadSynergies(G.squad, SYNERGIES);

    showScreen('formation');
  });

  // ═══════════════════════════════════════════════════════════════════
  // FORMATION SELECT
  // ═══════════════════════════════════════════════════════════════════

  let selectedFormationId = null;
  let _carouselIdx = 0;

  function getFormationFit(formation, squad) {
    // Count positions in squad
    const counts = {};
    squad.forEach(p => { counts[p.position] = (counts[p.position] || 0) + 1; });
    // Count slots needed per position
    const slotCounts = {};
    formation.slots.forEach(s => { slotCounts[s] = (slotCounts[s] || 0) + 1; });
    // Calculate fit: how many slots can be filled with available players
    let filled = 0;
    let total = formation.slots.length;
    Object.entries(slotCounts).forEach(([pos, needed]) => {
      const have = counts[pos] || 0;
      filled += Math.min(have, needed);
    });
    return { filled, total, pct: Math.round((filled / total) * 100) };
  }

  function renderCarousel(idx) {
    const f = FORMATIONS[idx];
    const squad = G.squad || [];
    const fit = getFormationFit(f, squad);
    const fits = FORMATIONS.map(f2 => ({ id: f2.id, ...getFormationFit(f2, squad) }));
    const maxPct = Math.max(...fits.map(f2 => f2.pct));
    const bestIds = fits.filter(f2 => f2.pct === maxPct).map(f2 => f2.id);
    const isRec = bestIds.includes(f.id);

    // Pitch slots
    const pitchSlots = f.pitchPositions.map(p =>
      `<div class="form-slot" style="left:${p.x}%;top:${p.y}%">${p.pos}</div>`
    ).join('');

    // Bonuses
    const bonusEntries = Object.entries(f.positionBonus);
    const bonusHtml = bonusEntries.length
      ? bonusEntries.map(([pos, val]) => {
          const cls = val > 0 ? 'bonus-pos' : 'bonus-neg';
          const sign = val > 0 ? '+' : '';
          return `<span class="bonus-tag ${cls}">${pos} ${sign}${val}</span>`;
        }).join('')
      : '';

    // Card
    document.getElementById('carousel-card').innerHTML = `
      ${isRec ? `<div class="form-rec">RECOMMENDED</div>` : ''}
      <div class="formation-name">${f.name}</div>
      <div class="formation-index">Formation ${idx + 1} of ${FORMATIONS.length}</div>
      <div class="form-pitch">${pitchSlots}</div>
    `;

    // Detail panel — Position Fit Breakdown
    // Count squad players per position
    const posCounts = {};
    squad.forEach(p => { posCounts[p.position] = (posCounts[p.position] || 0) + 1; });
    // Count slots needed per position for this formation
    const slotNeeded = {};
    f.slots.forEach(s => { slotNeeded[s] = (slotNeeded[s] || 0) + 1; });
    // All unique positions across squad + formation slots
    const allPositions = [...new Set([...Object.keys(slotNeeded), ...Object.keys(posCounts)])];
    const posOrder = ['GK','CB','FB','CDM','CM','CAM','ST','LW','RW'];
    const sortedPositions = allPositions.sort((a,b) => posOrder.indexOf(a) - posOrder.indexOf(b));

    const posRows = sortedPositions.map(pos => {
      const needed = slotNeeded[pos] || 0;
      const have = posCounts[pos] || 0;
      if (needed === 0 && have > 0) return ''; // Player with no slot needed — skip
      const eligible = squad.filter(p => p.position === pos);
      const availNames = eligible.map(p => p.name.split(' ')[0]).join(', ');
      let status, statusClass;
      if (needed === 0) return '';
      if (have >= needed) { status = '✓ FULL'; statusClass = 'green'; }
      else if (have === 0) { status = `✗ EMPTY (need ${needed})`; statusClass = 'poor'; }
      else { status = `✗ NEED ${needed - have} more`; statusClass = 'gold'; }
      return `<div class="fit-row">
        <span class="fit-row-pos fit-row-pos-${pos}">${pos}</span>
        <span class="fit-row-players">${availNames || '—'}</span>
        <span class="fit-row-count">${have}/${needed}</span>
        <span class="fit-row-status ${statusClass}">${status}</span>
      </div>`;
    }).filter(Boolean).join('');

    const totalHave = squad.length;
    const totalNeeded = f.slots.length;
    const allFull = sortedPositions.every(pos => {
      const needed = slotNeeded[pos] || 0;
      return needed === 0 || (posCounts[pos] || 0) >= needed;
    });

    document.getElementById('form-detail').innerHTML = `
      <div class="form-desc">${f.description}</div>
      <div class="form-detail-meta">
        <div class="form-detail-stat">
          Global Mult
          <span class="val ${f.globalMult >= 1.0 ? 'green' : 'gold'}">×${f.globalMult}</span>
        </div>
        <div class="form-detail-stat">
          Slots Filled
          <span class="val ${fit.pct >= 80 ? 'green' : fit.pct >= 50 ? 'gold' : 'poor'}">${fit.filled}/${fit.total}</span>
        </div>
        <div class="form-detail-stat">
          Overall
          <span class="val ${allFull ? 'green' : 'gold'}">${allFull ? '✓ READY' : Math.round((fit.filled/fit.total)*100) + '%'}</span>
        </div>
      </div>
      <div class="fit-rows">${posRows}</div>
      ${bonusHtml ? `<div class="bonuses">${bonusHtml}</div>` : ''}
      <div style="font-family:var(--font-body);font-size:14px;color:var(--muted);margin-top:var(--space-2);text-align:center;">
        Squad: ${totalHave} players · ${totalNeeded} slots needed
      </div>
    `;

    // Dot indicators
    const dotsHtml = FORMATIONS.map((_, i) =>
      `<div class="carousel-dot${i === idx ? ' active' : ''}" onclick="carouselGo(${i})"></div>`
    ).join('');
    document.getElementById('carousel-dots').innerHTML = dotsHtml;

    // Arrow states
    document.getElementById('carousel-prev').disabled = idx === 0;
    document.getElementById('carousel-next').disabled = idx === FORMATIONS.length - 1;

    // Selection state
    selectedFormationId = f.id;
    document.getElementById('confirm-formation-btn').disabled = false;
  }

  function carouselPrev() { if (_carouselIdx > 0) { _carouselIdx--; renderCarousel(_carouselIdx); } }
  function carouselNext() { if (_carouselIdx < FORMATIONS.length - 1) { _carouselIdx++; renderCarousel(_carouselIdx); } }
  function carouselGo(i) { _carouselIdx = i; renderCarousel(_carouselIdx); }

  function renderFormationSelect() {
    _carouselIdx = 0;
    renderCarousel(0);
    document.getElementById('confirm-formation-btn').disabled = false;
  }

  document.getElementById('confirm-formation-btn').addEventListener('click', () => {
    try {
      if (!selectedFormationId) return;
      G.formation = FORMATIONS.find(f => f.id === selectedFormationId);
      if (!G.formation) { console.error('Formation not found:', selectedFormationId); return; }

      // Mid-match formation tweak — don't reset state, just go back to shop
      if (window._pendingFormationTweak) {
        window._pendingFormationTweak = false;
        showScreen('shop');
        return;
      }

      G.round = 0;
      G.roundsWon = 0;
      G.roundsLost = 0;
      G.roundWins = [false, false, false];
      G.fatigue = {};
      G.carryover = null;
      G.journeymanUsed = false;
      G.roundScore = 0;
      G.phaseIdx = 0;
      G.phasePlacement = {};
      G.activeSlot = null;
      G.morale = 0;
      G.shopBuffs = {};
      G.phaseFatigue = {};
      for (var pfi = 0; pfi < ALL_PHASES.length; pfi++) {
        G.phaseFatigue[ALL_PHASES[pfi].id] = 1.0;
      }
      G.phaseHand = dealPhases();
      G.selectedPhases = [];
      startPhaseSelection();
    } catch(err) {
      console.error('Formation confirm error:', err);
      
    }
  });

  // ═══════════════════════════════════════════════════════════════════
  // PHASE SELECTION — pick 3 of 6 dealt cards
  // ═══════════════════════════════════════════════════════════════════

  const WEIGHT_LABELS = { DEF:'DEF', PAS:'PAS', PAC:'PAC', ATK:'ATK', SPC:'SPC' };
  let _psPicked = [];
  let _psHand = [];

  function startPhaseSelection() {
    try {
      _psHand = G.phaseHand || dealPhases();
      // Scout report: show more phase cards if purchased
      var maxPhases = G.shopBuffs.scout_active ? 8 : 6;
      if (_psHand.length > maxPhases) _psHand = _psHand.slice(0, maxPhases);
      _psPicked = [];
      G.selectedPhases = [];
      G.momentum = 1.0;

      // Generate opponent adjustments for this round
      G.opponentAdjustments = {};
      var shuffledAdj = shuffleArray(ALL_PHASES);
      if (shuffledAdj.length > 0) G.opponentAdjustments[shuffledAdj[0].id] = 1.3;
      if (shuffledAdj.length > 1) G.opponentAdjustments[shuffledAdj[1].id] = 0.7;
      if (shuffledAdj.length > 2 && Math.random() < 0.5) {
        G.opponentAdjustments[shuffledAdj[2].id] = Math.random() < 0.5 ? 1.15 : 0.85;
      }

      const roundInfo = document.getElementById('ps-round-info');
      roundInfo.textContent = 'Round ' + (G.round + 1) + '/3 - Target: ' + (CAMPAIGN_MATCHES[G.matchIdx] ? CAMPAIGN_MATCHES[G.matchIdx].targets[G.round] : 400);

      // Show scouting report for the first round of each match
      var scoutingEl = document.getElementById('ps-scouting');
      if (G.round === 0 && CAMPAIGN_MATCHES[G.matchIdx] && CAMPAIGN_MATCHES[G.matchIdx].intro) {
        scoutingEl.textContent = '🔍 ' + CAMPAIGN_MATCHES[G.matchIdx].intro;
        scoutingEl.style.display = 'block';
      } else if (scoutingEl) {
        scoutingEl.style.display = 'none';
      }

      // Show available synergies
      const synDiv = document.getElementById('ps-available-syns');
      const av = getAvailableSynergies(G.squad, SYNERGIES);
      if (av.length > 0) {
        const lines = av.slice(0, 5).map(s =>
          '<span style="color:var(--accent);margin-right:var(--space-2)">' + s.name + '</span>'
        );
        synDiv.innerHTML = 'Synergies available: ' + lines.join('');
        if (av.length > 5) synDiv.innerHTML += ' <span style="color:var(--muted)">(+' + (av.length - 5) + ' more)</span>';
      }

      renderPhaseCards();
      showScreen('phase-select');
    } catch(err) {
      console.error('startPhaseSelection error:', err);
      
    }
  }

  function renderPhaseCards() {
    const container = document.getElementById('ps-cards');
    const html = _psHand.map((phase, i) => {
      const isPicked = _psPicked.includes(i);
      const pickClass = isPicked ? 'picked' : (_psPicked.length > 0 && _psPicked[_psPicked.length-1] === i ? 'just-picked' : '');
      const pickOrder = _psPicked.indexOf(i) + 1;
      const icon = WEIGHT_LABELS[phase.weight] || '?';
      const slotsStr = phase.slots.map(s => typeof s === 'string' ? s : (Array.isArray(s) ? s.join('/') : (s.as || '?'))).join(' → ');

      // Calculate best fit players
      const bestFit = [];
      for (const slot of phase.slots) {
        const pos = typeof slot === 'string' ? slot : (Array.isArray(slot) ? slot[0] : (slot.as || '?'));
        var elig = G.squad.filter(p => isPlayerEligible(p, slot));
        if (elig.length) {
          const best = elig.reduce((a, b) => calculateChips(a, pos) > calculateChips(b, pos) ? a : b);
          bestFit.push(best.name + '(' + pos + ')');
        }
      }

      // Phase adjustment tags
      const phaseId = phase.id;
      const fatigueVal = G.phaseFatigue[phaseId] !== undefined ? G.phaseFatigue[phaseId] : 1.0;
      const oppVal = G.opponentAdjustments[phaseId] || 1.0;
      var tagsHtml = '';
      if (fatigueVal < 1.0) tagsHtml += '<span style="color:var(--gold);font-size:10px;margin-left:var(--space-1)">fatigue ×' + fatigueVal.toFixed(2) + '</span>';
      if (oppVal !== 1.0) {
        var opColor = oppVal > 1.0 ? 'var(--accent)' : 'var(--danger)';
        var opLabel = oppVal > 1.0 ? 'opp. weakness' : 'opp. strong';
        tagsHtml += '<span style="color:' + opColor + ';font-size:10px;margin-left:var(--space-1)">' + opLabel + ' ×' + oppVal.toFixed(2) + '</span>';
      }

      const synPotential = getAvailableSynergies(G.squad, SYNERGIES);
      const synNames = synPotential.slice(0, 2).map(s => s.name).join(', ');

      return '<div class="ps-card ' + pickClass + '" onclick="selectPhaseCard(' + i + ')" data-idx="' + i + '">' +
        (pickOrder ? '<div class="pc-order">#' + pickOrder + '</div>' : '') +
        '<div class="pc-icon">' + icon + '</div>' +
        '<div class="pc-name">' + phase.name + '</div>' +
        '<div class="pc-desc">' + (phase.desc || phase.description || '') + '</div>' +
        '<div class="pc-slots">' + slotsStr + '</div>' +
        (bestFit.length ? '<div style="font-size:11px;color:var(--fg-dim);margin-top:var(--space-1)">Best: ' + bestFit.join(', ') + '</div>' : '') +
        (tagsHtml ? '<div style="margin-top:var(--space-1)">' + tagsHtml + '</div>' : '') +
        (synNames ? '<div class="pc-syn">◈ ' + synNames + '</div>' : '') +
        '</div>';
    }).join('');
    container.innerHTML = html;

    // Update picks display
    const picksDiv = document.getElementById('ps-picks');
    if (_psPicked.length === 0) {
      picksDiv.textContent = 'Click a phase card to select it. Pick 3 in order.';
    } else {
      const pickedNames = _psPicked.map(i => _psHand[i].name).join(' → ');
      picksDiv.textContent = 'Selected order: ' + pickedNames;
    }

    document.getElementById('confirm-phases-btn').disabled = (_psPicked.length < 3);
  }

  function selectPhaseCard(index) {
    if (_psPicked.includes(index)) return;
    // Visual feedback
    var card = document.querySelector('.ps-card[data-idx="' + index + '"]');
    if (card) { card.classList.add('selected'); setTimeout(function() { card.classList.remove('selected'); }, 400); } // already picked
    if (_psPicked.length >= 3) return; // already picked 3
    _psPicked.push(index);
    renderPhaseCards();
  }

  document.getElementById('confirm-phases-btn').addEventListener('click', () => {
    if (_psPicked.length !== 3) return;
    G.selectedPhases = _psPicked.map(i => _psHand[i]);
    G.roundPhases = G.selectedPhases;
    G.phaseIdx = 0;
    G.phasePlacement = {};
    showScreen('match');
    setTimeout(renderMatchPhase, 100);
  });

  // ═══════════════════════════════════════════════════════════════════
  // MATCH SCREEN
  // ═══════════════════════════════════════════════════════════════════

  // ═══════════════════════════════════════════════════════════════════
  // TACTICAL SIDE-VIEW PITCH + PLAYER PICKER MODAL
  // ═══════════════════════════════════════════════════════════════════

  const TACTICAL_ZONES = {
    goal_kick:       { left:'0%',  width:'35%', label:'Defensive Third' },
    defensive_block: { left:'0%',  width:'40%', label:'Defensive Zone' },
    regroup:         { left:'5%',  width:'30%', label:'Deep Defence' },
    hold_shape:      { left:'15%', width:'35%', label:'Midfield Screen' },
    build_up:        { left:'15%', width:'35%', label:'Build-Up Zone' },
    tiki_taka:       { left:'25%', width:'40%', label:'Midfield Control' },
    controlled_tempo:{ left:'30%', width:'30%', label:'Pivot Zone' },
    direct_play:     { left:'10%', width:'80%', label:'Full Pitch' },
    counter_attack:  { left:'55%', width:'40%', label:'Attacking Third' },
    wide_overload:   { left:'50%', width:'45%', label:'Wide Channels' },
    target_man:      { left:'65%', width:'30%', label:'Box Area' },
    late_run:        { left:'60%', width:'35%', label:'Final Third' },
    set_piece:       { left:'65%', width:'30%', label:'Box Area' },
  };

  const FORMULA_TEXT = {
    ST:'ATK×4 + PAC×1.5',
    LW:'PAC×3 + ATK×2',
    RW:'PAC×3 + ATK×2',
    CM:'PAS×4 + DEF×1',
    CAM:'PAS×3.5 + ATK×2 + SPC×1',
    CDM:'DEF×4 + PAS×1',
    CB:'DEF×5',
    FB:'DEF×3 + PAC×1.5',
    GK:'DEF×3 + SPC×2'
  };

  const FORMULA_PARTS = {
    ST:[['ATK',4],['PAC',1.5]],
    LW:[['PAC',3],['ATK',2]],
    RW:[['PAC',3],['ATK',2]],
    CM:[['PAS',4],['DEF',1]],
    CAM:[['PAS',3.5],['ATK',2],['SPC',1]],
    CDM:[['DEF',4],['PAS',1]],
    CB:[['DEF',5]],
    FB:[['DEF',3],['PAC',1.5]],
    GK:[['DEF',3],['SPC',2]]
  };

  const STAT_COLORS = { ATK:'#ff3344', PAC:'var(--gold)', PAS:'var(--info)', DEF:'var(--accent)', SPC:'#c084fc' };
  const STAT_KEY = { ATK:'atk', PAC:'pac', PAS:'pas', DEF:'def_', SPC:'spc' };

  function getPosClass(fp) {
    if (fp === 'GK') return 'GK';
    if (['CB','FB'].includes(fp)) return 'DEF';
    if (['CDM','CM','CAM'].includes(fp)) return 'MID';
    return 'ATT';
  }
  function getShirtNum(fp) {
    const map = { GK:1, CB:4, CB1:5, CB2:5, FB:2, FB1:2, FB2:3, CDM:6, CM:8, CM1:8, CM2:11, CAM:10, LW:7, RW:11, ST:9, ST1:9, ST2:12 };
    return map[fp] || 0;
  }

  function renderMatch() {
    const matchData = CAMPAIGN_MATCHES[G.matchIdx] || CAMPAIGN_MATCHES[0];
    document.getElementById('opponent-name').textContent = matchData.opponent;
    document.getElementById('match-label').textContent = matchData.tier;
    document.getElementById('rounds-won').textContent = G.roundsWon;
    document.getElementById('rounds-lost').textContent = G.roundsLost;
    renderMatchPhase();
  }

  function renderMatchPhase() {
    const phase = G.roundPhases[G.phaseIdx];
    if (!phase) { console.error('No phase'); return; }

    document.getElementById('phase-icon').textContent = phase.icon;
    document.getElementById('phase-name').textContent = phase.name;
    document.getElementById('phase-desc').textContent = phase.desc || '';
    document.getElementById('phase-weight').textContent = phase.weight;

    const tz = TACTICAL_ZONES[phase.id] || { label:'Pitch' };
    document.getElementById('phase-zone-label').textContent = tz.label;

    // Opponent name
    if (CAMPAIGN_MATCHES[G.matchIdx]) {
      document.getElementById('opponent-name').textContent = CAMPAIGN_MATCHES[G.matchIdx].opponent;
    }

    // Progress dots
    document.getElementById('round-num').textContent = G.round + 1;
    document.getElementById('phase-num').textContent = G.phaseIdx + 1;
    const roundDots = document.getElementById('round-dots');
    roundDots.innerHTML = '';
    for (let i = 0; i <= G.round; i++) {
      const dot = document.createElement('span');
      dot.className = 'progress-dot';
      if (i < G.round) dot.classList.add(G.roundWins[i] ? 'done' : 'lose');
      else if (i === G.round) dot.classList.add('active');
      roundDots.appendChild(dot);
    }
    const phaseDots = document.getElementById('phase-dots');
    phaseDots.innerHTML = '';
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement('span');
      dot.className = 'progress-dot';
      if (i < G.phaseIdx) dot.classList.add('done');
      else if (i === G.phaseIdx) dot.classList.add('active');
      phaseDots.appendChild(dot);
    }

    // Target
    const target = CAMPAIGN_MATCHES[G.matchIdx] ? CAMPAIGN_MATCHES[G.matchIdx].targets[G.round] : 500;
    document.getElementById('target-num').textContent = target;
    document.getElementById('live-score').textContent = G.roundScore;

    renderSlotCards();
    renderEligiblePlayers(null);
    renderSynergyPreview();
  }

  // ═══════════════════════════════════════════════════════════════════
  // LIVE PHASE SCORE + SYNERGY INDICATORS
  // ═══════════════════════════════════════════════════════════════════

  function updateLivePhaseDisplay() {
    const phase = G.roundPhases[G.phaseIdx];
    if (!phase) return;

    // Build field from current placements
    const field = [];
    for (const [idx, pid] of Object.entries(G.phasePlacement)) {
      const player = G.squad.find(p => p.id === pid);
      const slot = phase.slots[parseInt(idx)];
      if (player && slot) field.push([player, slotFieldPosition(slot)]);
    }

    // Detect synergies live (new API: returns {chips, add_mult, x_mult, fired_details})
    const synResult = field.length >= 2 ? detectSynergies(field, SYNERGIES) : { chips:0, add_mult:0, x_mult:1.0, fired_details:[] };

    // Collect fired synergy names
    const firedSet = new Set();
    for (const fd of (synResult.fired_details || [])) {
      firedSet.add(fd.name.split(' (')[0]);
    }
    // Add persistent synergies
    for (const name of (G.persistentBuffs && G.persistentBuffs.fired_synergies || [])) {
      firedSet.add(name + ' (P)');
    }

    // Calculate total chips from placed players
    let totalChips = 0;
    const placementList = [];
    for (const [idx, pid] of Object.entries(G.phasePlacement)) {
      const player = G.squad.find(p => p.id === pid);
      const slot = phase.slots[parseInt(idx)];
      if (player && slot) {
        const fp = slotFieldPosition(slot);
        const baseChips = calculateChips(player, fp);
        const fBonus = (G.formation && G.formation.positionBonus && G.formation.positionBonus[fp]) || 0;
        const totalWithBonus = baseChips + fBonus;

        // Get synergy add for this player
        const ps = synResult[player.id] || { add_chips: 0, multiply: 1.0 };
        const fatigueMult = G.fatigue[player.id] !== undefined ? G.fatigue[player.id] : 1.0;
        const afterSyn = Math.round((totalWithBonus + (ps.add_chips || 0)) * (ps.multiply || 1.0) * fatigueMult);
        placementList.push({ player, fp, chips: afterSyn });
        totalChips += afterSyn;
      }
    }

    // Update DOM
    document.getElementById('live-phase-score').textContent = totalChips;
    const detailEl = document.getElementById('live-score-detail');
    if (field.length === 0) {
      detailEl.textContent = '— assign players';
    } else if (field.length < phase.slots.length) {
      detailEl.textContent = field.length + '/' + phase.slots.length + ' slots · ' + firedSet.size + ' syn';
    } else {
      detailEl.textContent = 'all slots · ' + firedSet.size + ' syn · READY';
    }

    // Update synergy badges
    const badgesEl = document.getElementById('live-synergy-badges');
    if (firedSet.size === 0 && field.length === 0) {
      badgesEl.innerHTML = '<span class="live-syn-empty">Place players to trigger synergies</span>';
    } else if (firedSet.size === 0) {
      badgesEl.innerHTML = '<span class="live-syn-empty">No synergies with current placements</span>';
    } else {
      let badgesHtml = '';
      for (const name of firedSet) {
        const isP = name.endsWith(' (P)');
        badgesHtml += '<span class="live-syn-badge fired">' + name + '</span>';
      }
      badgesEl.innerHTML = badgesHtml;
    }

    // Also update submit hint
    updateSubmitHint();
  }

  function renderSlotCards() {
    const phase = G.roundPhases[G.phaseIdx];
    const container = document.getElementById('slot-cards');
    // Detect synergies live to show badge on slot cards
    const field = [];
    for (const [fj, pid] of Object.entries(G.phasePlacement)) {
      const p = G.squad.find(s => s.id === pid);
      const sl = phase.slots[parseInt(fj)];
      if (p && sl) field.push([p, slotFieldPosition(sl)]);
    }
    const synResult = field.length >= 2 ? detectSynergies(field, SYNERGIES) : { chips:0, add_mult:0, x_mult:1.0, fired_details:[] };
    const synPlayerSet = new Set();
    for (const fd of (synResult.fired_details || [])) {
      for (const c of (fd.contributors || [])) synPlayerSet.add(c);
    }

    let html = '';
    phase.slots.forEach(function(slot, i) {
      const fp = slotFieldPosition(slot);
      const pid = G.phasePlacement[i];
      const player = pid ? G.squad.find(function(p) { return p.id === pid; }) : null;
      const filled = !!player;
      const label = formatSlotLabel(slot);
      const hasEligible = !filled && G.squad.some(function(p) {
        return p && isPlayerEligible(p, slot) && !Object.values(G.phasePlacement).includes(p.id);
      });

      const chips = filled ? calculateChips(player, fp) : 0;
      const posClass = getPosClass(fp);
      const synActive = filled && synPlayerSet.has(player.id);
      const playerSynCount = synActive ? (synResult.fired_details || []).length : 0;

      html += '<div class="' + (filled ? 'slot-card filled' : 'slot-card') + (synActive ? ' syn-fired' : '') + '" onclick="selectSlot(' + i + ')" data-od-id="slot-' + i + '">' +
        '<div><span style="font-family:var(--font-display);font-size:9px;color:' +
          (filled ? 'var(--accent)' : 'var(--fg-dim)') + '">' + fp + '</span>' +
        (synActive ? '<span class="slot-syn-badge" style="font-family:var(--font-display);font-size:7px;color:var(--accent);background:rgba(57,255,20,0.1);border:1px solid var(--accent);border-radius:2px;padding:1px 6px;margin-left:var(--space-2)">*' + playerSynCount + '</span>' : '') +
        (label ? '<span style="font-family:var(--font-body);font-size:var(--text-sm);color:var(--muted);margin-left:var(--space-2)">' + label + '</span>' : '') +
        '</div>' +
        '<span style="font-family:var(--font-body);font-size:var(--text-lg);color:' +
          (filled ? 'var(--fg)' : 'var(--muted)') + '">' +
          (filled ? player.name : (hasEligible ? '▸ Tap to fill' : 'No eligible')) +
        '</span>' +
        (filled ? '<span style="font-family:var(--font-display);font-size:8px;color:var(--gold)">' + chips + ' ♣</span>' : '') +
      '</div>';
    });
    container.innerHTML = html;

    // Summary
    const filled = Object.keys(G.phasePlacement).length;
    const total = phase.slots.length;
    document.getElementById('slot-summary').textContent = filled + '/' + total + ' slots filled' +
      (filled > 0 ? ' · preview below' : '');

    updateLivePhaseDisplay();
  }
  let _selectedSlot = null;

  function renderEligiblePlayers(slotIdx) {
    _selectedSlot = slotIdx;
    const phase = G.roundPhases[G.phaseIdx];
    const titleEl = document.getElementById('eligible-title');
    const listEl = document.getElementById('eligible-list');

    if (slotIdx === null || slotIdx === undefined) {
      titleEl.textContent = 'Tap a slot to see eligible players';
      listEl.innerHTML = '<div style="text-align:center;padding:var(--space-4);color:var(--muted);font-family:var(--font-body);font-size:var(--text-lg)">No slot selected</div>';
      return;
    }

    const slot = phase.slots[slotIdx];
    const fp = slotFieldPosition(slot);
    const pid = G.phasePlacement[slotIdx];
    if (pid) {
      const player = G.squad.find(p => p.id === pid);
      titleEl.textContent = fp + ' — ' + player.name + ' assigned';
      listEl.innerHTML = '<div style="text-align:center;padding:var(--space-4)">' +
        '<div style="font-family:var(--font-body);font-size:var(--text-lg);color:var(--accent);margin-bottom:var(--space-2)">✅ Slot filled</div>' +
        '<span style="font-family:var(--font-display);font-size:7px;color:var(--muted);cursor:pointer" onclick="removeSlot(' + slotIdx + ')">[tap to remove]</span>' +
        '</div>';
      return;
    }

    const usedIds = new Set(Object.values(G.phasePlacement));
    const eligible = G.squad.filter(function(p) {
      return !usedIds.has(p.id) && isPlayerEligible(p, slot);
    }).sort(function(a, b) { return calculateChips(b, fp) - calculateChips(a, fp); });

    if (eligible.length === 0) {
      titleEl.textContent = 'No eligible players for ' + fp;
      listEl.innerHTML = '<div style="text-align:center;padding:var(--space-4);color:var(--warn);font-family:var(--font-body);font-size:var(--text-lg)">' +
        'No one meets the requirements</div>';
      return;
    }

    titleEl.textContent = 'Pick ' + fp + ' (' + eligible.length + ' eligible)';
    let html = '';
    eligible.forEach(function(p) {
      const chips = calculateChips(p, fp);
      const fatigue = G.fatigue[p.id] !== undefined ? G.fatigue[p.id] : 1.0;
      const fatigueStr = fatigue < 1.0 ? ' ×' + fatigue.toFixed(1) : '';
      html += '<div class="picker-row" onclick="openPickerFromEligible(' + slotIdx + ',\'' + p.id + '\')" style="grid-template-columns:1fr 54px 28px">' +
        '<span class="pr-name">' + p.name + '</span>' +
        '<span class="pr-chips">' + chips + ' ♣</span>' +
        '<span style="font-family:var(--font-body);font-size:var(--text-sm);color:' + (fatigue < 1.0 ? 'var(--warn)' : 'var(--accent)') + '">' + (fatigue < 1.0 ? fatigueStr : '✓') + '</span>' +
      '</div>';
    });
    listEl.innerHTML = html + '<div style="margin-top:var(--space-2);text-align:center"><span style="font-family:var(--font-body);font-size:var(--text-sm);color:var(--muted);cursor:pointer" onclick="openPicker(' + slotIdx + ')">[view full stats →]</span></div>';
  }

  function removeSlot(index) {
    delete G.phasePlacement[index];
    renderSlotCards();
    renderEligiblePlayers(_selectedSlot);
    renderSynergyPreview();
    updateLivePhaseDisplay();
  }

  function selectSlot(index) {
    const placed = G.phasePlacement[index] !== undefined;
    if (placed) {
      // Offer to remove
      _selectedSlot = index;
      renderSlotCards();
      renderEligiblePlayers(index);
      return;
    }
    _selectedSlot = index;
    renderSlotCards();
    renderEligiblePlayers(index);
  }

  function openPickerFromEligible(slotIdx, playerId) {
    // Use the existing picker to assign and show stats
    G.phasePlacement[slotIdx] = playerId;
    G._pickerSlot = null;
    renderSlotCards();
    renderEligiblePlayers(null);
    renderSynergyPreview();
    updateLivePhaseDisplay();
  }function formatSlotLabel(slot) {
    if (typeof slot === 'string') return slot;
    if (Array.isArray(slot)) return slot.join('/');
    return '?';
  }

  function updateSubmitHint() {
    const phase = G.roundPhases[G.phaseIdx];
    const filled = phase.slots.filter(function(_, i) { return G.phasePlacement[i] !== undefined; }).length;
    const total = phase.slots.length;
    const hint = document.getElementById('submit-hint') || document.createElement('div');
    if (!hint.id) {
      hint.id = 'submit-hint';
      hint.style.cssText = 'font-family:var(--font-body);font-size:var(--text-sm);color:var(--muted);text-align:center;margin-top:var(--space-2)';
      document.getElementById('submit-phase-btn').parentElement.appendChild(hint);
    }
    if (filled === 0) {
      hint.textContent = 'No players assigned — submit with 0 ♣ from this phase';
    } else if (filled < total) {
      hint.textContent = 'Assigned ' + filled + '/' + total + ' slots. Empty slots contribute 0 ♣';
    } else {
      hint.textContent = 'All slots filled — ready to submit!';
    }
  }

  function renderSynergyPreview() {
    const container = document.getElementById('synergy-list');
    const placed = [];
    for (const [idx, pid] of Object.entries(G.phasePlacement)) {
      const player = G.squad.find(p => p.id === pid);
      const slot = G.roundPhases[G.phaseIdx].slots[parseInt(idx)];
      if (player && slot) placed.push([player, slotFieldPosition(slot)]);
    }

    const lines = [];
    for (const name of (G.persistentBuffs.fired_synergies || [])) {
      lines.push('<div class="synergy-row"><div class="synergy-dot"></div>' + name + ' <span style="color:var(--muted)">(persistent)</span></div>');
    }

    if (placed.length >= 2) {
      const result = detectSynergies(placed, SYNERGIES);
      const fired = new Set();
      for (const fd of (result.fired_details || [])) {
        fired.add(fd.name.split(' (')[0]);
      }
      for (const s of fired) {
        if (!lines.some(l => l.includes(s))) lines.push('<div class="synergy-row"><div class="synergy-dot"></div>' + s + '</div>');
      }
    }

    if (lines.length === 0) {
      container.innerHTML = '<div style="font-family:var(--font-body);font-size:var(--text-lg);color:var(--muted)">Place players to activate synergies</div>';
    } else {
      container.innerHTML = lines.join('');
    }
  }

  // ═══════════════════════════════════════════════════════════════════
  // MATCH ACTIONS
  // ═══════════════════════════════════════════════════════════════════

  function placeMatchPlayer(playerId) {
    if (G._pickerSlot === null || G._pickerSlot === undefined) return;

    const phase = G.roundPhases[G.phaseIdx];
    const usedIds = new Set(Object.values(G.phasePlacement));
    if (usedIds.has(playerId)) return;

    const player = G.squad.find(p => p.id === playerId);
    const slot = phase.slots[G._pickerSlot];
    if (!isPlayerEligible(player, slot)) {
      showToast(player.name + ' doesn\'t meet requirements');
      return;
    }

    G.phasePlacement[G._pickerSlot] = playerId;
    G._pickerSlot = null;

    renderSlotCards();
    renderEligiblePlayers(null);
    renderSynergyPreview();
    updateLivePhaseDisplay();
  }

  // ═══════════════════════════════════════════════════════════════════
  // PLAYER PICKER MODAL
  // ═══════════════════════════════════════════════════════════════════

  let _expandedRow = null;

  function openPicker(slotIndex) {
    const phase = G.roundPhases[G.phaseIdx];
    const slot = phase.slots[slotIndex];
    const fp = slotFieldPosition(slot);
    G._pickerSlot = slotIndex;

    // Header
    document.getElementById('picker-pos').textContent = fp;
    document.getElementById('picker-req').textContent = formatSlotLabel(slot);
    document.getElementById('picker-formula').textContent = 'Formula: ' + (FORMULA_TEXT[fp] || '\u2014');

    // Build rows
    const usedIds = new Set(Object.values(G.phasePlacement));
    const body = document.getElementById('picker-body');
    _expandedRow = null;

    const entries = G.squad.map(p => {
      const used = usedIds.has(p.id);
      const eligible = !used && isPlayerEligible(p, slot);
      const fatigueMult = G.fatigue[p.id] !== undefined ? G.fatigue[p.id] : 1.0;
      const baseChips = eligible ? calculateChips(p, fp) : 0;
      const finalChips = eligible ? Math.round(baseChips * fatigueMult) : 0;
      // Count potential synergies
      const testField = [[p, fp]];
      for (const [idx2, pid] of Object.entries(G.phasePlacement)) {
        if (pid !== p.id) {
          const pp = G.squad.find(s => s.id === pid);
          const sl = phase.slots[parseInt(idx2)];
          if (pp) testField.push([pp, slotFieldPosition(sl)]);
        }
      }
      const synResult = testField.length >= 2 ? detectSynergies(testField, SYNERGIES) : { chips:0, add_mult:0, x_mult:1.0, fired_details:[] };
      let synCount = (synResult.fired_details || []).length;

      return { player: p, used, eligible, fatigueMult, baseChips, finalChips, synCount, fp };
    });

    entries.sort((a, b) => {
      if (a.used !== b.used) return a.used ? 1 : -1;
      if (a.eligible !== b.eligible) return a.eligible ? -1 : 1;
      return b.finalChips - a.finalChips;
    });

    let html = '';
    for (const e of entries) {
      const cls = e.used ? 'used' : (e.eligible ? '' : 'inel');
      html += '<div class="picker-row ' + cls + '" data-pid="' + e.player.id + '" data-eligible="' + e.eligible + '">' +
        '<span class="pr-name">' + (e.used ? '\u2713 ' : '') + e.player.name + '</span>' +
        '<span class="pr-st atk">' + e.player.atk + '</span>' +
        '<span class="pr-st pac">' + e.player.pac + '</span>' +
        '<span class="pr-st pas">' + e.player.pas + '</span>' +
        '<span class="pr-st def">' + e.player.def_ + '</span>' +
        '<span class="pr-st spc">' + e.player.spc + '</span>' +
        '<span class="pr-chips">' + (e.eligible ? e.finalChips + ' \u2663' : '\u2014') + '</span>' +
        '<span class="pr-syn">' + (e.synCount > 0 ? 'S' + e.synCount : '') + '</span>' +
      '</div>';

      if (e.eligible && !e.used) {
        html += buildExpandedBreakdown(e, fp, slot, phase);
      }
    }

    body.innerHTML = html;
    document.getElementById('picker-overlay').style.display = 'flex';

    // Attach click handlers
    body.querySelectorAll('.picker-row[data-eligible="true"]').forEach(row => {
      row.addEventListener('click', function() { toggleExpandedRow(this); });
    });
    body.querySelectorAll('.pe-pick').forEach(btn => {
      btn.addEventListener('click', function(ev) {
        ev.stopPropagation();
        placeMatchPlayer(this.dataset.pid);
        closePicker();
      });
    });
  }

  function buildExpandedBreakdown(e, fp, slot, phase) {
    const p = e.player;
    const fm = e.fatigueMult;
    const parts = FORMULA_PARTS[fp] || [];
    const statVals = { ATK: p.atk, PAC: p.pac, PAS: p.pas, DEF: p.def_, SPC: p.spc };
    const fBonus = (G.formation && G.formation.positionBonus && G.formation.positionBonus[fp]) || 0;

    // Synergy preview
    const testField = [[p, fp]];
    for (const [idx, pid] of Object.entries(G.phasePlacement)) {
      if (pid !== p.id) {
        const pp = G.squad.find(s => s.id === pid);
        const sl = phase.slots[parseInt(idx)];
        if (pp) testField.push([pp, slotFieldPosition(sl)]);
      }
    }
    const synResult = testField.length >= 2 ? detectSynergies(testField, SYNERGIES) : { chips:0, add_mult:0, x_mult:1.0, fired_details:[] };
    let synHtml = '';
    const firedNames = (synResult.fired_details || []).map(fd => fd.name);
    for (const syn of SYNERGIES) {
      if (syn.persistent) continue;
      let fired = firedNames.some(n => n.startsWith(syn.name));
      const tr = syn.trigger;
      const relevant = (tr.pos_a === fp || tr.pos_b === fp || (tr.positions && tr.positions.includes(fp)));
      if (relevant || fired) {
        synHtml += '<div class="pe-syn-row ' + (fired ? 'fired' : 'inact') + '">' +
          '<span class="pe-syn-chk">' + (fired ? '\u2713' : '\u2717') + '</span>' +
          '<span>' + syn.name + '</span>' +
          '<span class="pe-syn-desc">' + syn.description + '</span>' +
        '</div>';
      }
    }

    let html = '<div class="picker-expand" data-expand-for="' + p.id + '">';
    // Traits
    html += '<div class="pe-traits">' + p.traits.map(function(t) { return '<span>' + t + '</span>'; }).join('') + '</div>';
    // Stat rows
    for (let si = 0; si < parts.length; si++) {
      const stat = parts[si][0];
      const mult = parts[si][1];
      const val = statVals[stat];
      const result = val * mult;
      const color = STAT_COLORS[stat];
      const fillPct = (val / 10) * 100;
      html += '<div class="pe-stat-row">' +
        '<span class="pe-stat-lbl" style="color:' + color + '">' + stat + '</span>' +
        '<div class="pe-stat-bar"><div class="pe-stat-fill" style="width:' + fillPct + '%;background:' + color + ';box-shadow:0 0 4px ' + color + '"></div></div>' +
        '<span class="pe-stat-val" style="color:' + color + '">' + val + '</span>' +
        '<span class="pe-stat-mult">\u00d7' + mult + '</span>' +
        '<span class="pe-stat-res">' + result + '</span>' +
      '</div>';
    }
    html += '<hr class="pe-divider">';
    html += '<div class="pe-info">Base: ' + e.baseChips + ' chips</div>';
    if (fBonus !== 0) html += '<div class="pe-info">Formation bonus: ' + (fBonus > 0 ? '+' : '') + fBonus + '</div>';
    if (fm < 1) html += '<div class="pe-info">Fatigue: \u00d7' + fm.toFixed(1) + '</div>';
    html += '<div class="pe-total">TOTAL: ' + e.finalChips + ' \u2663</div>';
    if (synHtml) {
      html += '<div class="pe-syn-title">Synergies if placed:</div>';
      html += synHtml;
    }
    html += '<button class="pe-pick" data-pid="' + p.id + '">PICK PLAYER</button>';
    html += '</div>';
    return html;
  }

  function toggleExpandedRow(row) {
    const expanded = row.nextElementSibling;
    if (!expanded || !expanded.classList.contains('picker-expand')) return;

    if (_expandedRow && _expandedRow !== expanded) {
      _expandedRow.classList.remove('open');
    }

    if (expanded.classList.contains('open')) {
      expanded.classList.remove('open');
      _expandedRow = null;
    } else {
      expanded.classList.add('open');
      _expandedRow = expanded;
    }
  }

  function closePicker() {
    document.getElementById('picker-overlay').style.display = 'none';
    document.getElementById('picker-cols').style.display = '';
    _expandedRow = null;
    G._pickerSlot = null;
    window._shopPickerActive = false;
  }

  document.getElementById('picker-close').addEventListener('click', closePicker);
  document.getElementById('picker-overlay').addEventListener('click', function(e) {
    if (e.target === e.currentTarget) closePicker();
  });

  function toggleSynergies() {
    const list = document.getElementById('synergy-list');
    const toggle = document.getElementById('syn-toggle');
    if (list.style.maxHeight === '0px' || !list.style.maxHeight || list.style.maxHeight === '0') {
      list.style.maxHeight = list.scrollHeight + 'px';
      toggle.textContent = '▲ collapse';
    } else {
      list.style.maxHeight = '0px';
      toggle.textContent = '▼ expand';
    }
  }

  document.getElementById('submit-phase-btn').addEventListener('click', () => {
    const phase = G.roundPhases[G.phaseIdx];

    // Build field: [(player, fieldPosition)]
    const field = [];
    for (const [idx, pid] of Object.entries(G.phasePlacement)) {
      const player = G.squad.find(p => p.id === pid);
      const slot = phase.slots[parseInt(idx)];
      if (player) {
        field.push([player, slotFieldPosition(slot)]);
        // Apply fatigue
        const penalty = (G.persistentBuffs && G.persistentBuffs.fatigue_penalty) || 0.7;
        G.fatigue[player.id] = (G.fatigue[player.id] !== undefined ? G.fatigue[player.id] : 1.0) * penalty;
      }
    }

    // Calculate momentum for this phase
    var momentumMult = {0: 1.0, 1: 1.2, 2: 1.5}[G.phaseIdx] || 1.5;
    G.momentum = momentumMult;

    // Calculate phase multiplier: fatigue × opponent adjustment
    var phaseId = phase.id;
    var fatiguePhase = G.phaseFatigue[phaseId] !== undefined ? G.phaseFatigue[phaseId] : 1.0;
    var oppAdj = G.opponentAdjustments[phaseId] || 1.0;
    var effectivePhaseMult = fatiguePhase * oppAdj;

    // Calculate real score with all parameters
    const result = calculateRoundScore(field, SYNERGIES, G.formation, G.fatigue, G.carryover, G.persistentBuffs, G.shopBuffs, momentumMult);
    result.phase_mult = effectivePhaseMult;
    result.total = Math.round(result.total * effectivePhaseMult);
    result.subtotal_before_formation = Math.round((result.subtotal_before_formation || result.total) * effectivePhaseMult);
    
    G.carryover = result.next_carryover || null;
    G.roundScore += result.total;

    // Apply phase fatigue decay
    if (G.phaseFatigue[phaseId] !== undefined) {
      G.phaseFatigue[phaseId] = G.phaseFatigue[phaseId] * 0.85;
    }

    // Store result for phase-result screen
    G._lastPhaseResult = {
      phase: { name: phase.name, weight: phase.weight, icon: phase.icon, id: phase.id },
      result: result,
      round: G.round,
      phaseIdx: G.phaseIdx,
      roundScore: G.roundScore,
      target: CAMPAIGN_MATCHES[G.matchIdx].targets[G.round],
    };

    showScreen('phase-result');
  });

  // ═══════════════════════════════════════════════════════════════════
  // PHASE RESULT
  // ═══════════════════════════════════════════════════════════════════

  function renderPhaseResult() {
    const pr = G._lastPhaseResult;
    if (!pr) { showScreen('match'); return; }

    const result = pr.result;
    const target = pr.target;
    const running = pr.roundScore;

    // Hero score cascade
    document.getElementById('pr-score').textContent = '0';
    setTimeout(function() { animateScoreCascade(result.total, 800); }, 100);
    document.getElementById('pr-target').textContent = 'Target: ' + target + ' · Running: ' + running;

    // Balatro formula display
    var balatroHtml = '<div style="margin-bottom:var(--space-4);padding:var(--space-3);background:rgba(0,0,0,0.3);border-radius:var(--radius-md);border:1px solid var(--border)">';
    balatroHtml += '<div style="color:var(--accent);font-weight:bold;font-size:var(--text-lg)">🃏 CHIPS: ' + (result.player_chips || 0) + (result.synergy_chips > 0 ? ' +' + result.synergy_chips + 'syn' : '') + (result.carryover_chips > 0 ? ' +' + result.carryover_chips + 'carry' : '') + (result.shop_chips > 0 ? ' +' + result.shop_chips + 'shop' : '') + ' = ' + (result.total_chips || result.total) + '</div>';
    var addMultDisp = (result.add_mult || 1);
    balatroHtml += '<div style="color:var(--gold);font-weight:bold">➕ ADD MULT: ' + addMultDisp + '</div>';
    var xMultDisp = (result.x_mult || 1);
    balatroHtml += '<div style="color:var(--info);font-weight:bold">✖ × MULT: ' + xMultDisp.toFixed(2) + '</div>';
    balatroHtml += '<div style="border-top:1px solid var(--border);padding-top:var(--space-2);margin-top:var(--space-2);">FORMULA: <span style="color:var(--accent)">' + (result.total_chips || 0) + '</span> × <span style="color:var(--gold)">' + addMultDisp + '</span> × <span style="color:var(--info)">' + xMultDisp.toFixed(2) + '</span>';
    if (result.formation_mult && result.formation_mult !== 1.0) balatroHtml += ' × <span style="color:var(--muted)">' + result.formation_mult.toFixed(2) + '</span>';
    if (result.momentum && result.momentum !== 1.0) balatroHtml += ' × <span style="color:var(--gold)">Momentum ×' + result.momentum + '</span>';
    if (result.phase_mult && result.phase_mult !== 1.0) balatroHtml += ' × <span style="color:var(--magenta)">Phase ×' + result.phase_mult.toFixed(2) + '</span>';
    balatroHtml += ' = <span style="color:var(--gold);font-size:var(--text-xl);font-weight:bold">' + result.total + '</span></div>';
    balatroHtml += '</div>';

    // Player Contributions Table
    const formation = G.formation || {};
    const posBonusMap = formation.positionBonus || {};
    const headerRow = '<div class="pr-tr" style="color:var(--muted);font-size:var(--text-sm);border-bottom:2px solid var(--border-soft);padding-bottom:var(--space-1)"><span class="pr-td-pos">POS</span><span class="pr-td-name">Player</span><span class="pr-td-base">Base</span><span class="pr-td-form">Form</span><span class="pr-td-fatigue">Fati</span><span class="pr-td-chips">Chips</span></div>';

    const rowsHtml = result.breakdown.map(b => {
      const posFormBonus = posBonusMap[b.position] || 0;
      const baseWithoutForm = b.base_chips - posFormBonus;
      const formDisplay = posFormBonus > 0 ? '+' + posFormBonus : '—';
      const fatigueClass = b.fatigue < 1.0 ? 'tired' : 'ok';
      const fatigueDisplay = b.fatigue < 1.0 ? '×' + b.fatigue : '✓';
      return '<div class="pr-tr">' +
        '<span class="pr-td-pos">' + b.position + '</span>' +
        '<span class="pr-td-name">' + b.player + '</span>' +
        '<span class="pr-td-base">' + baseWithoutForm + '</span>' +
        '<span class="pr-td-form">' + formDisplay + '</span>' +
        '<span class="pr-td-fatigue ' + fatigueClass + '">' + fatigueDisplay + '</span>' +
        '<span class="pr-td-chips">' + b.subtotal + '♣</span>' +
        '</div>';
    }).join('');

    document.getElementById('pr-breakdown-rows').innerHTML = balatroHtml + headerRow + rowsHtml;

    // Synergies Accordion
    const firedNames = result.fired_synergies || [];
    document.getElementById('pr-syn-count').textContent = firedNames.length;

    // Calculate total synergy chip adds
    let totalSynAdd = 0;
    for (const b of result.breakdown) {
      totalSynAdd += (b.add_chips || 0);
    }
    document.getElementById('pr-syn-total').textContent = '+' + Math.round(totalSynAdd);

    const synBody = document.getElementById('pr-syn-body');
    const contributors = result.synergy_contributors || {};
    const descriptions = result.synergy_descriptions || {};

    if (firedNames.length === 0) {
      synBody.innerHTML = '<div class="pr-syn-none">No synergies fired this phase</div>';
    } else {
      // Categorize by persistent
      var phaseSyns = [];
      var persistentSyns = [];
      for (var si = 0; si < firedNames.length; si++) {
        var name = firedNames[si];
        var synDef = null;
        for (var sj = 0; sj < SYNERGIES.length; sj++) {
          if (SYNERGIES[sj].name === name) { synDef = SYNERGIES[sj]; break; }
        }
        if (synDef && synDef.persistent) persistentSyns.push(name);
        else phaseSyns.push(name);
      }

      var synHtml = '';

      if (phaseSyns.length > 0) {
        synHtml += '<div class="pr-syn-group-title">Phase-Specific</div>';
        for (var si = 0; si < phaseSyns.length; si++) {
          var name = phaseSyns[si];
          var isActive = name.indexOf('INACTIVE') === -1;
          var synergyNames = phaseSyns; // needed inside
          var contribText = '';
          var cList = contributors[name];
          if (cList && cList.length > 0) {
            contribText = '<div class="pr-syn-contrib">' + cList.join(' · ') + '</div>';
          }
          var descText = descriptions[name] || '';
          // Extract value from synergy definition
          var valText = '';
          var synDef = null;
          for (var sj = 0; sj < SYNERGIES.length; sj++) {
            if (SYNERGIES[sj].name === name) { synDef = SYNERGIES[sj]; break; }
          }
          if (synDef) {
            if (synDef.effectType === 'add_chips' && synDef.effect && (synDef.effect.chips || synDef.effect.add_chips)) {
              valText = '+' + (synDef.effect.chips || synDef.effect.add_chips);
            } else if (synDef.effectType === 'multiply' && synDef.effect && (synDef.effect.x_mult || synDef.effect.multiply)) {
              valText = '×' + (synDef.effect.x_mult || synDef.effect.multiply);
            }
          }
          synHtml += '<div class="pr-syn-item triggered">' +
            '<div class="pr-syn-dot active"></div>' +
            '<div class="pr-syn-info"><div class="pr-syn-name">' + name + '</div>' +
            (descText ? '<div class="pr-syn-desc">' + descText + '</div>' : '') +
            contribText + '</div>' +
            (valText ? '<div class="pr-syn-value">' + valText + '</div>' : '') +
            '</div>';
        }
      }

      if (persistentSyns.length > 0) {
        synHtml += '<div class="pr-syn-group-title">Persistent</div>';
        for (var si = 0; si < persistentSyns.length; si++) {
          var name = persistentSyns[si];
          var contribText = '';
          var cList = contributors[name];
          if (cList && cList.length > 0) {
            contribText = '<div class="pr-syn-contrib">' + cList.join(' · ') + '</div>';
          }
          var descText = descriptions[name] || '';
          var valText = '';
          var synDef = null;
          for (var sj = 0; sj < SYNERGIES.length; sj++) {
            if (SYNERGIES[sj].name === name) { synDef = SYNERGIES[sj]; break; }
          }
          if (synDef) {
            if (synDef.effectType === 'persistent_add' && synDef.effect && (synDef.effect.chips || synDef.effect.add_chips)) {
              valText = '+' + (synDef.effect.chips || synDef.effect.add_chips);
            } else if (synDef.effectType === 'persistent_multiply' && synDef.effect && (synDef.effect.multiply || synDef.effect.x_mult)) {
              valText = '×' + (synDef.effect.multiply || synDef.effect.x_mult);
            }
          }
          synHtml += '<div class="pr-syn-item triggered">' +
            '<div class="pr-syn-dot active"></div>' +
            '<div class="pr-syn-info"><div class="pr-syn-name">' + name + '</div>' +
            (descText ? '<div class="pr-syn-desc">' + descText + '</div>' : '') +
            contribText + '</div>' +
            (valText ? '<div class="pr-syn-value">' + valText + '</div>' : '') +
            '</div>';
        }
      }

      synBody.innerHTML = synHtml;
    }

    // Accordion stays collapsed by default
    document.getElementById('pr-syn-body').classList.remove('open');
    document.getElementById('pr-syn-arrow').classList.remove('open');
  }

  // Accordion toggle
  document.getElementById('pr-syn-toggle').addEventListener('click', function() {
    var body = document.getElementById('pr-syn-body');
    var arrow = document.getElementById('pr-syn-arrow');
    body.classList.toggle('open');
    arrow.classList.toggle('open');
  });

  document.getElementById('pr-continue-btn').addEventListener('click', () => {
    G.phaseIdx++;

    // AUTO-WIN: if we beat the target, immediately end the round
    var target = CAMPAIGN_MATCHES[G.matchIdx].targets[G.round];
    if (G.roundScore >= target) {
      G.roundWins[G.round] = true;
      G.roundsWon++;
      // Calculate morale
      var moraleEarned = 1 + (G.roundScore >= target ? 3 : 0) + (G.roundScore >= target * 1.5 ? 2 : 0);
      G.morale += moraleEarned;
      // Check match end
      if (G.roundsWon >= 2 || G.roundsLost >= 2 || G.round >= 2) {
        const matchWon = G.roundsWon > G.roundsLost;
        G.matchResults.push({ won: matchWon, opponent: CAMPAIGN_MATCHES[G.matchIdx].opponent, name: CAMPAIGN_MATCHES[G.matchIdx].name, roundsWon: G.roundsWon, roundsLost: G.roundsLost });
        showScreen('round-result');
      } else {
        renderShop();
        showScreen('shop');
      }
      return;
    }

    if (G.phaseIdx >= 3) {
      // Round complete — all phases used, target not met
      G.roundWins[G.round] = false;
      G.roundsLost++;
      // Check match end (best of 3)
      if (G.roundsWon >= 2 || G.roundsLost >= 2 || G.round >= 2) {
        const matchWon = G.roundsWon > G.roundsLost;
        G.matchResults.push({
          won: matchWon,
          opponent: CAMPAIGN_MATCHES[G.matchIdx].opponent,
          name: CAMPAIGN_MATCHES[G.matchIdx].name,
          roundsWon: G.roundsWon,
          roundsLost: G.roundsLost,
        });
        showScreen('round-result');
        return;
      }
      showScreen('round-result');
      return;
    }

    // Next phase
    G.phasePlacement = {};
    G.activeSlot = null;
    showScreen('match');
  });

  // ═══════════════════════════════════════════════════════════════════
  // ROUND RESULT
  // ═══════════════════════════════════════════════════════════════════

  function renderRoundResult() {
    const target = CAMPAIGN_MATCHES[G.matchIdx].targets[G.round];
    const won = G.roundScore >= target;
    const matchComplete = G.roundsWon >= 2 || G.roundsLost >= 2 || G.round >= 2;

    if (matchComplete) {
      const matchWon = G.roundsWon > G.roundsLost;
      document.getElementById('rr-verdict').textContent = matchWon ? 'Match Won!' : 'Match Lost';
      document.getElementById('rr-verdict').className = 'round-verdict ' + (matchWon ? 'win' : 'lose');
      document.getElementById('rr-message').textContent = matchWon
        ? `You beat ${CAMPAIGN_MATCHES[G.matchIdx].opponent} ${G.roundsWon}-${G.roundsLost}`
        : `${CAMPAIGN_MATCHES[G.matchIdx].opponent} wins ${G.roundsLost}-${G.roundsWon}`;
    } else {
      document.getElementById('rr-verdict').textContent = won ? 'Round Won' : 'Round Lost';
      document.getElementById('rr-verdict').className = 'round-verdict ' + (won ? 'win' : 'lose');
      document.getElementById('rr-message').textContent = won
        ? 'You cleared the target! Keep going.'
        : 'You fell short. Must win the remaining rounds.';
    }

    document.getElementById('rr-your-score').textContent = G.roundScore;
    document.getElementById('rr-target').textContent = target;

    // Round indicators
    const roundsEl = document.getElementById('rr-rounds');
    roundsEl.innerHTML = '';
    for (let i = 0; i <= G.round; i++) {
      const ind = document.createElement('div');
      ind.className = 'round-indicator';
      if (i < G.round) ind.classList.add(G.roundWins[i] ? 'won' : 'lost');
      else ind.classList.add('current');
      ind.textContent = `R${i+1}`;
      roundsEl.appendChild(ind);
    }
  }

  document.getElementById('rr-continue-btn').addEventListener('click', () => {
    const matchComplete = G.roundsWon >= 2 || G.roundsLost >= 2 || G.round >= 2;

    if (matchComplete) {
      // Next match or campaign end
      G.matchIdx++;
      if (G.matchIdx >= CAMPAIGN_MATCHES.length) {
        showScreen('campaign');
      } else {
        // Start next match
        G.round = 0;
        G.roundsWon = 0;
        G.roundsLost = 0;
        G.roundWins = [false, false, false];
        G.roundScore = 0;
        G.phaseIdx = 0;
        G.phasePlacement = {};
        G.activeSlot = null;
        G.fatigue = {};
        G.carryover = null;
        G.journeymanUsed = false;
        G.phaseHand = dealPhases();
        G.selectedPhases = [];
        startPhaseSelection();
      }
    } else {
      // Round won — earn morale, show shop
      var targetVal = CAMPAIGN_MATCHES[G.matchIdx].targets[G.round];
      var moraleEarned = 1 + (G.roundScore >= targetVal ? 3 : 0) + (G.roundScore >= targetVal * 1.5 ? 2 : 0);
      G.morale += moraleEarned;
      renderShop();
      showScreen('shop');
    }
  });

  // ═══════════════════════════════════════════════════════════════════
  // CAMPAIGN COMPLETE
  // ═══════════════════════════════════════════════════════════════════

  function renderCampaignComplete() {
    const wins = G.matchResults.filter(r => r.won).length;
    const title = document.getElementById('cc-title');
    title.textContent = wins >= 3 ? 'Campaign Won!' : 'Campaign Complete';
    title.className = 'campaign-title ' + (wins >= 3 ? 'victory' : 'defeat');

    const container = document.getElementById('cc-results');
    container.innerHTML = G.matchResults.map((r, i) =>
      `<div class="match-result-card ${r.won ? 'won' : 'lost'}" data-od-id="match-result-${i}">
        <div style="font-family:var(--font-display);font-size:8px;color:var(--muted);min-width:24px">M${i+1}</div>
        <div style="flex:1">
          <div class="mrc-name">${r.name}</div>
          <div class="mrc-opponent">vs ${r.opponent}</div>
        </div>
        <div class="mrc-result ${r.won ? 'won' : 'lost'}">${r.won ? 'WIN' : 'LOSS'} ${r.roundsWon}-${r.roundsLost}</div>
      </div>`
    ).join('');
  }

  function resetGame() {
    G.selectedIds = new Set();
    G.squad = [];
    G.formation = null;
    G.matchIdx = 0;
    G.matchResults = [];
    G.roundWins = [false, false, false];
    G.roundsWon = 0;
    G.roundsLost = 0;
    G.round = 0;
    G.roundScore = 0;
    G.roundPhases = [];
    G.phaseIdx = 0;
    G.phasePlacement = {};
    G.activeSlot = null;
    G.fatigue = {};
    G.carryover = null;
    G.journeymanUsed = false;
    G.persistentBuffs = null;
    showScreen('title');
  }

  // ═══════════════════════════════════════════════════════════════════
  // SHOP — Between rounds
  // ═══════════════════════════════════════════════════════════════════

  const SHOP_ITEMS = [
    { id:'scout_report', name:'Scout Report', cost:2, desc:'See all 8 phase cards next round', rarity:'common' },
    { id:'inspired_sub', name:'Inspired Sub', cost:2, desc:'Restore one player fatigue', rarity:'common' },
    { id:'formation_tweak', name:'Formation Tweak', cost:3, desc:'Swap formation', rarity:'common' },
    { id:'set_piece_drill', name:'Set Piece Drill', cost:4, desc:'Next round: +40 chips', rarity:'uncommon', effect:{extra_chips:40} },
    { id:'tactical_shift', name:'Tactical Shift', cost:5, desc:'Next round: +5 add_mult', rarity:'uncommon', effect:{extra_add_mult:5} },
    { id:'vet_wisdom', name:"Veteran's Wisdom", cost:6, desc:'Random trait', rarity:'rare' },
  ];

  function renderShop() {
    document.getElementById('shop-morale').textContent = '💰 ' + G.morale + ' Morale';
    var shuffled = shuffleArray(SHOP_ITEMS).slice(0, 4);
    var itemsEl = document.getElementById('shop-items');
    itemsEl.innerHTML = shuffled.map(function(item, idx) {
      var canAfford = G.morale >= item.cost;
      var rarityColors = {common:'var(--fg-dim)', uncommon:'var(--info)', rare:'var(--gold)'};
      var col = rarityColors[item.rarity] || 'var(--fg-dim)';
      return '<div style="border-left:4px solid ' + col + ';padding:var(--space-3);margin:var(--space-2) 0;opacity:' + (canAfford ? 1 : 0.4) + ';cursor:' + (canAfford ? 'pointer' : 'default') + '" onclick="buyShopItem(' + idx + ')">' +
        '<div style="font-weight:bold;color:var(--fg)">[' + (idx+1) + '] ' + item.name + ' <span style="color:' + col + ';font-size:var(--text-sm)">(' + item.rarity + ')</span></div>' +
        '<div style="font-size:var(--text-sm);color:var(--fg-dim)">' + item.desc + '</div>' +
        '<div style="color:' + (canAfford ? 'var(--accent)' : 'var(--danger)') + '">' + (canAfford ? '✔' : '✘') + ' ' + item.cost + ' Morale</div>' +
        '</div>';
    }).join('');
    window._shopItems = shuffled;
  }

  function buyShopItem(idx) {
    var items = window._shopItems || [];
    var item = items[idx];
    if (!item || G.morale < item.cost) return;
    G.morale -= item.cost;
    if (item.effect) { for (var k in item.effect) G.shopBuffs[k] = item.effect[k]; }

    // Handle special item effects
    switch (item.id) {
      case 'inspired_sub':
        renderShop();
        renderShopPlayerPicker('inspired_sub', 'Select a player to restore fatigue');
        return;
      case 'formation_tweak':
        G.shopBuffs.formation_tweaked = true;
        window._pendingFormationTweak = true;
        renderShop();
        showToast('✅ Bought ' + item.name + '! Pick a new formation.');
        showScreen('formation');
        return;
      case 'scout_report':
        G.shopBuffs.scout_active = true;
        break;
      case 'vet_wisdom':
        renderShop();
        renderShopPlayerPicker('vet_wisdom', 'Select a player to grant a random trait');
        return;
    }

    renderShop();
    showToast('✅ Bought ' + item.name + '!');
  }

  function renderShopPlayerPicker(type, title) {
    var players = G.squad.filter(function(p) {
      if (type === 'inspired_sub') {
        var fat = G.fatigue[p.id] !== undefined ? G.fatigue[p.id] : 1.0;
        return fat < 1.0;
      }
      return true;
    });

    if (players.length === 0) {
      renderShop();
      showToast('⚠ No eligible players for ' + (type === 'inspired_sub' ? 'fatigue restore' : 'trait grant') + '!');
      return;
    }

    var body = document.getElementById('picker-body');
    body.innerHTML = '<div style="padding:var(--space-4);text-align:center">' +
      '<h3 style="color:var(--gold);margin-bottom:var(--space-4)">' + title + '</h3>' +
      players.map(function(p) {
        var fat = G.fatigue[p.id] !== undefined ? G.fatigue[p.id] : 1.0;
        var extra = '';
        if (type === 'inspired_sub') {
          extra = ' <span style="color:var(--info);font-size:var(--text-sm)">(fatigue: ×' + fat.toFixed(2) + ')</span>';
        } else if (type === 'vet_wisdom') {
          extra = '<br><span style="color:var(--info);font-size:var(--text-sm)">Traits: ' + p.traits.join(', ') + '</span>';
        }
        return '<div style="padding:var(--space-3);margin:var(--space-2);background:var(--surface);border:1px solid var(--border);border-radius:var(--radius-md);cursor:pointer" onclick="applyShopPlayerPick(\'' + type + '\',\'' + p.id + '\')">' +
          '<span style="color:var(--fg);font-weight:bold">' + p.name + '</span> ' +
          '<span style="color:var(--fg-dim)">(' + p.position + ')</span>' + extra +
          '</div>';
      }).join('') +
      '<div style="margin-top:var(--space-3)"><button class="btn btn-secondary" onclick="closePicker();renderShop();">Cancel</button></div>' +
      '</div>';

    document.getElementById('picker-pos').textContent = 'SHOP';
    document.getElementById('picker-req').textContent = '';
    document.getElementById('picker-formula').textContent = '';
    document.getElementById('picker-cols').style.display = 'none';
    document.getElementById('picker-overlay').style.display = 'flex';
    window._shopPickerActive = true;
  }

  function applyShopPlayerPick(type, playerId) {
    var player = G.squad.find(function(p) { return p.id === playerId; });
    if (!player) return;

    if (type === 'inspired_sub') {
      G.fatigue[player.id] = 1.0;
      closePicker();
      renderShop();
      showToast('✅ Fatigue restored for ' + player.name + '!');
    } else if (type === 'vet_wisdom') {
      var TRAIT_POOL = ['pacey','clinical','technical','playmaker','physical','destroyer','aerial','poacher','leader'];
      var available = TRAIT_POOL.filter(function(t) { return player.traits.indexOf(t) === -1; });
      if (available.length === 0) {
        closePicker();
        renderShop();
        showToast('⚠ ' + player.name + ' already has all traits!');
        return;
      }
      var trait = available[Math.floor(Math.random() * available.length)];
      player.traits.push(trait);
      closePicker();
      renderShop();
      showToast('✅ ' + player.name + ' learned ' + trait + '!');
    }
  }

  function skipShop() {
    G.round++;
    G.roundScore = 0;
    G.phaseIdx = 0;
    G.phaseHand = null;
    G.momentum = 1.0;
    G.opponentAdjustments = {};
    G.phasePlacement = {};
    G.activeSlot = null;
    G.carryover = null;
    startPhaseSelection();
  }

  // ═══════════════════════════════════════════════════════════════════
  // AUTO-FILL
  // ═══════════════════════════════════════════════════════════════════

  function autoFillPhase() {
    var phase = G.roundPhases[G.phaseIdx];
    var usedIds = new Set(Object.values(G.phasePlacement));
    for (var si = 0; si < phase.slots.length; si++) {
      if (G.phasePlacement[si] !== undefined) continue;
      var slot = phase.slots[si];
      var fp = typeof slot === 'string' ? slot : (Array.isArray(slot) ? slot[0] : (slot.as || 'ST'));
      var best = null, bestChips = -1;
      for (var pi = 0; pi < G.squad.length; pi++) {
        var p = G.squad[pi];
        if (usedIds.has(p.id) || !isPlayerEligible(p, slot)) continue;
        var fat = G.fatigue[p.id] !== undefined ? G.fatigue[p.id] : 1.0;
        var oop = getPositionPenalty(p, fp);
        var chips = Math.round(calculateChips(p, fp) * fat * oop);
        if (chips > bestChips) { bestChips = chips; best = p; }
      }
      if (best) { G.phasePlacement[si] = best.id; usedIds.add(best.id); }
    }
    G._pickerSlot = null;
    renderSlotCards();
    renderEligiblePlayers(null);
    renderSynergyPreview();
    closePicker();
    showToast('🤖 Auto-filled!');
  }

  // ═══════════════════════════════════════════════════════════════════
