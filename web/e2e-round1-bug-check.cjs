const { chromium } = require('playwright');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8765/game.html?e2e=buttons2';

async function wait(ms) { return new Promise(r => setTimeout(r, ms)); }
async function current(page) { return page.evaluate(() => (window.Game && Game._current) ? Game._current() : null); }

async function quickStart(page) {
  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => typeof window.quickStartGame === 'function');
  await page.evaluate(() => {
    localStorage.removeItem('squad_game_save');
    sessionStorage.clear();
    quickStartGame();
  });
  await page.waitForFunction(() => window.Game && Game._current && Game._current() === 'match', { timeout: 10000 });
}

async function triggerSubmitViaRealHandler(page) {
  return page.evaluate(() => {
    function placeForCurrentPhase(){
      const phase = getActivePhase();
      const used = new Set();
      const squad = getSquad();
      const placements = [];
      for (let i = 0; i < phase.slots.length; i++) {
        const slot = phase.slots[i];
        const pos = Array.isArray(slot) ? slot[0] : slot;
        const best = squad.filter(p => !used.has(p.id)).sort((a, b) => {
          const av = (a.position === pos ? 1000 : 0) + (a.atk + a.pac + a.pas + a.def_ + a.spc);
          const bv = (b.position === pos ? 1000 : 0) + (b.atk + b.pac + b.pas + b.def_ + b.spc);
          return bv - av;
        })[0];
        used.add(best.id);
        placements.push({ playerId: best.id, slotId: pos });
      }
      return placements;
    }
    // drive the live routed match screen the same way the UI does
    window.slots = placeForCurrentPhase().map(p => ({ playerId: p.playerId }));
    submitPhaseHandler();
    return { engineScreen: G.currentScreen, phaseIdx: G.phaseIdx, roundScore: G.roundScore };
  });
}

async function clickPhaseContinue(page) {
  await page.waitForFunction(() => window.Game && Game._current && Game._current() === 'phase-result', { timeout: 10000 });
  await page.click('#pr-continue-btn');
  await wait(250);
  return current(page);
}

async function clickRoundContinue(page) {
  await page.waitForFunction(() => window.Game && Game._current && Game._current() === 'round-result', { timeout: 10000 });
  await page.click('#rr-continue-btn');
  await wait(250);
  return current(page);
}

async function clickShopContinue(page) {
  await page.waitForFunction(() => window.Game && Game._current && Game._current() === 'shop', { timeout: 10000 });
  const ok = await page.evaluate(() => {
    const btn = document.getElementById('btnContinue') || document.getElementById('btn-continue') || document.querySelector('.btn-continue');
    if (!btn) return false;
    btn.click();
    return true;
  });
  if (!ok) throw new Error('shop continue button not found');
  await wait(300);
  return current(page);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => pageErrors.push(String(err)));

  await quickStart(page);

  const flow = [];
  flow.push({ stage: 'afterQuickStart', screen: await current(page), state: await page.evaluate(() => ({ engine: G.currentScreen, roundIdx: G.roundIdx, phaseIdx: G.phaseIdx, picked: G.pickedPhases.length, dealt: G.dealtPhases.length, morale: G.morale })) });

  // round 1 through real phase-result and round-result/shop buttons
  for (let i = 0; i < 3; i++) {
    const submit = await triggerSubmitViaRealHandler(page);
    flow.push({ stage: `r1_phase_${i+1}_submit`, screen: await current(page), submit });
    const next = await clickPhaseContinue(page);
    flow.push({ stage: `r1_phase_${i+1}_continue`, screen: next, state: await page.evaluate(() => ({ engine: G.currentScreen, roundIdx: G.roundIdx, phaseIdx: G.phaseIdx, roundScore: G.roundScore, morale: G.morale })) });
  }

  const afterRoundResult = await clickRoundContinue(page);
  flow.push({ stage: 'r1_round_result_continue', screen: afterRoundResult, state: await page.evaluate(() => ({ engine: G.currentScreen, roundIdx: G.roundIdx, phaseIdx: G.phaseIdx, roundResults: G.roundResults.length, morale: G.morale })) });

  const afterShop = await clickShopContinue(page);
  flow.push({ stage: 'shop_continue_to_round2', screen: afterShop, state: await page.evaluate(() => ({ engine: G.currentScreen, roundIdx: G.roundIdx, phaseIdx: G.phaseIdx, dealt: G.dealtPhases.length, picked: G.pickedPhases.length, roundScore: G.roundScore, morale: G.morale })) });

  console.log(JSON.stringify({ base: BASE, flow, consoleErrors, pageErrors }, null, 2));
  await browser.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
