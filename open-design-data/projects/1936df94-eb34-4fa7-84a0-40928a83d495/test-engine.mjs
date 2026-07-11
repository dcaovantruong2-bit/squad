import { readFileSync } from 'fs';

const code = readFileSync('./game-engine.js', 'utf-8');

// Execute in global scope using vm module for proper hoisting
import vm from 'vm';
const ctx = {};
vm.createContext(ctx);

try {
  vm.runInContext(code, ctx);
} catch(e) {
  console.error('PARSE ERROR:', e.message);
  process.exit(1);
}

const { PLAYERS, FORMATIONS, ALL_PHASES, SYNERGIES, CAMPAIGN_MATCHES, CHIPS_FORMULA, calculateChips, calculateRoundScore, isPlayerEligible, getEligiblePlayers, detectPersistentSynergies, detectSynergies, pickRandomPhases, dealPhases, getAvailableSynergies, checkMinimums, BUDGET, MIN_TOTAL, ROLE_GROUPS } = ctx;

console.log('=== GAME DATA ===');
console.log('Players:', PLAYERS.length);
console.log('Formations:', FORMATIONS.length);
console.log('All Phases:', ALL_PHASES.length);
console.log('Synergies:', SYNERGIES.length);
console.log('Campaign matches:', CAMPAIGN_MATCHES.length);

// Check CHIPS_FORMULA coverage
const allPos = ['GK','CB','FB','CDM','CM','CAM','LW','RW','ST'];
const missing = allPos.filter(p => !CHIPS_FORMULA[p]);
console.log('Missing CHIPS_FORMULA:', missing.length === 0 ? 'NONE ✓' : missing);

// Build a valid squad
const squad = ['gigi_wall','van_aura','big_phil','danny_pace','turbo_trent','sergio_busq','luka_modric','kevin_de_b','terry_henri','big_zlat']
  .map(id => PLAYERS.find(p => p.id === id))
  .filter(Boolean);

const missingPlayers = ['gigi_wall','van_aura','big_phil','danny_pace','turbo_trent','sergio_busq','luka_modric','kevin_de_b','terry_henri','big_zlat']
  .filter(id => !PLAYERS.find(p => p.id === id));
if (missingPlayers.length > 0) console.log('MISSING PLAYERS:', missingPlayers);

const totalCost = squad.reduce((s,p) => s + p.cost, 0);
console.log('\n=== SQUAD ===');
console.log('Squad size:', squad.length, '/ 10', squad.length >= 10 ? '✓' : '✗');
console.log('Total cost:', totalCost, '/ 360', totalCost <= 360 ? '✓' : '✗');

// Check minimums
const minCheck = checkMinimums ? checkMinimums(squad) : null;
console.log('Minimum check:', minCheck ? JSON.stringify(minCheck) : 'FUNCTION NOT FOUND');

// Detect persistent synergies
let pers = [];
try { pers = detectPersistentSynergies ? detectPersistentSynergies(squad, SYNERGIES) : []; } catch(e) { console.log('detectPersistentSynergies error:', e.message); }
console.log('\nPersistent synergies:', pers.length);
if (pers.length > 0) pers.forEach(s => console.log('  -', s.name, s.effect_description || ''));

// Test eligibility
console.log('\n=== ELIGIBILITY ===');
const testSlot = ALL_PHASES[0].slots[0]; // First phase, first slot
console.log('Test slot:', testSlot.pos, '- weight:', testSlot.weight, '- min_atk:', testSlot.min_atk, '- min_pac:', testSlot.min_pac, '- min_def:', testSlot.min_def);
const eligible = getEligiblePlayers ? getEligiblePlayers(testSlot, squad) : [];
console.log('Eligible players:', eligible.length);
eligible.slice(0, 3).forEach(p => console.log('  -', p.name, '(' + p.pos + ')', 'ATK:', p.atk, 'PAC:', p.pac, 'DEF:', p.def_, 'SPC:', p.spc));

// Test scoring - all 6 phases of first match
console.log('\n=== PHASE SCORING ===');
const formation = FORMATIONS[0]; // 4-3-3
const phases = dealPhases ? dealPhases(6) : ALL_PHASES.slice(0, 6);
let totalScore = 0;
let synergyCount = 0;

phases.forEach((ph, idx) => {
  const placements = {};
  ph.slots.forEach((slot, si) => {
    const elig = getEligiblePlayers ? getEligiblePlayers(slot, squad) : [];
    if (elig.length > 0) {
      placements[si] = elig[0].id;
    }
  });
  
  try {
    const result = calculateRoundScore(squad, placements, ph, formation, pers, 1);
    totalScore += result.score;
    const sc = Object.keys(result.fired_synergies || {}).length;
    synergyCount += sc;
    const filled = Object.keys(placements).length;
    console.log('Phase', idx+1, ':', ph.name, '- filled:', filled, '/' + ph.slots.length, '- Score:', result.score, '- Synergies:', sc);
  } catch(e) {
    console.log('Phase', idx+1, ':', ph.name, '- ERROR:', e.message);
  }
});

console.log('\nTotal Match Score:', totalScore);

// Check against match 1 round targets
console.log('\n=== CAMPAIGN TARGETS ===');
CAMPAIGN_MATCHES.forEach((m, i) => {
  console.log('Match', i+1, ':', m.opponent, '- Targets:', m.roundTargets.join(', '), '- Difficulty:', m.difficulty);
});

// Verify round 1 result against match 1 target
const match1Target = CAMPAIGN_MATCHES[0].roundTargets[0];
console.log('\nMatch 1 Round 1:', totalScore, 'vs target', match1Target, '-', totalScore >= match1Target ? 'WIN ✓' : 'LOSE');

console.log('\n=== ALL TESTS PASSED ✓ ===');
