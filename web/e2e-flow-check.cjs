const { chromium } = require('playwright');

const BASE = process.env.BASE_URL || 'http://127.0.0.1:8765/game.html?e2e=1';

async function wait(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function getScreen(page) {
  return await page.evaluate(() => (window.Game && Game._current) ? Game._current() : null);
}

async function assertNoJsErrors(page, stage) {
  const errs = await page.evaluate(() => ({
    hasG: typeof window.G !== 'undefined',
    current: (window.Game && Game._current) ? Game._current() : null,
    title: document.title,
  }));
  if (!errs.hasG) throw new Error(`[${stage}] window.G missing`);
  return errs;
}

async function ensureMatchReady(page) {
  await page.waitForFunction(() => typeof window.G !== 'undefined' && typeof window.getActivePhase === 'function');
}

async function driveRoundViaEngine(page, roundLabel) {
  await ensureMatchReady(page);
  const result = await page.evaluate((label) => {
    function placeForCurrentPhase(){
      const phase = getActivePhase();
      const used = new Set();
      const squad = getSquad();
      const placements = [];
      for (let i = 0; i < phase.slots.length; i++) {
        const slot = phase.slots[i];
        const pos = Array.isArray(slot) ? slot[0] : slot;
        const best = squad
          .filter(p => !used.has(p.id))
          .sort((a, b) => {
            const av = (a.position === pos ? 1000 : 0) + (a.atk + a.pac + a.pas + a.def_ + a.spc);
            const bv = (b.position === pos ? 1000 : 0) + (b.atk + b.pac + b.pas + b.def_ + b.spc);
            return bv - av;
          })[0];
        used.add(best.id);
        placements.push({ playerId: best.id, slotId: pos });
      }
      return placements;
    }

    commitPhases(G.dealtPhases.slice(0, 3));
    const phaseScores = [];
    for (let i = 0; i < 3; i++) {
      const res = submitPhase(placeForCurrentPhase());
      phaseScores.push(res.score);
    }
    const roundRes = finishRound();
    return {
      label,
      phaseScores,
      finishRoundResult: roundRes,
      roundIdx: G.roundIdx,
      phaseIdx: G.phaseIdx,
      roundScore: G.roundScore,
      roundResult: G.roundResults[G.roundResults.length - 1],
      currentScreen: G.currentScreen,
    };
  }, roundLabel);
  return result;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const consoleErrors = [];
  const pageErrors = [];

  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', err => pageErrors.push(String(err)));

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => typeof window.G !== 'undefined' && typeof window.quickStartGame === 'function');
  await assertNoJsErrors(page, 'initial');

  // start from title and use real button handler path
  await page.evaluate(() => {
    localStorage.removeItem('squad_game_save');
    sessionStorage.clear();
    quickStartGame();
  });
  await wait(300);

  const afterQuick = await page.evaluate(() => ({
    current: (window.Game && Game._current) ? Game._current() : null,
    engineScreen: G.currentScreen,
    roundIdx: G.roundIdx,
    phaseIdx: G.phaseIdx,
    picked: G.pickedPhases.length,
    dealt: G.dealtPhases.length,
    morale: G.morale,
  }));

  // Round 1
  const r1 = await driveRoundViaEngine(page, 'round1');
  await page.evaluate(() => { if (window.Game) Game.navigate('round-result'); });
  await wait(200);
  const screenAfterR1 = await getScreen(page);
  await page.evaluate(() => {
    G.roundIdx += 1; // emulate round-result continue
    if (window.Game) Game.navigate('shop');
  });
  await wait(200);
  const screenAtShop = await getScreen(page);
  await page.evaluate(() => {
    if (typeof startRound === 'function') startRound();
    if (window.Game) Game.navigate('phases');
  });
  await wait(200);
  const afterShop = await page.evaluate(() => ({
    current: (window.Game && Game._current) ? Game._current() : null,
    roundIdx: G.roundIdx,
    phaseIdx: G.phaseIdx,
    roundScore: G.roundScore,
    dealt: G.dealtPhases.length,
    picked: G.pickedPhases.length,
    morale: G.morale,
  }));

  // Round 2
  const r2 = await driveRoundViaEngine(page, 'round2');
  await page.evaluate(() => { G.roundIdx += 1; if (window.Game) Game.navigate('shop'); });
  await wait(200);
  await page.evaluate(() => { if (typeof startRound === 'function') startRound(); if (window.Game) Game.navigate('phases'); });
  await wait(200);

  // Round 3 + match complete
  const r3 = await driveRoundViaEngine(page, 'round3');
  const matchOutcome = await page.evaluate(() => finishMatch());
  const postMatch = await page.evaluate(() => ({
    current: (window.Game && Game._current) ? Game._current() : null,
    matchIdx: G.matchIdx,
    roundIdx: G.roundIdx,
    campaignWon: G.campaignWon,
    matchResults: G.matchResults.length,
    morale: G.morale,
  }));

  const result = {
    base: BASE,
    afterQuick,
    screenAfterR1,
    screenAtShop,
    afterShop,
    r1,
    r2,
    r3,
    matchOutcome,
    postMatch,
    consoleErrors,
    pageErrors,
  };

  console.log(JSON.stringify(result, null, 2));

  await browser.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
