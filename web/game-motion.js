/**
 * SQUAD — emilkowalski-motion Animation Trigger Functions
 * Transform & opacity animation helpers for all 9 game screens.
 *
 * USAGE:
 *   Load game-motion.css first, then call these from
 *   game-engine.js or game.html inline event handlers.
 *
 * PRINCIPLES:
 *   - Only animates `transform` and `opacity` (never top/left/width/height)
 *   - UI controls: 140–220ms
 *   - Page reveals: 300–500ms
 *   - Respects prefers-reduced-motion (all durations → 0.01ms)
 *   - No JS animation libraries — pure CSS + class toggling
 */

/* ═══════════════════════════════════════════════════════════════════════
   HELPERS
   ═══════════════════════════════════════════════════════════════════════ */

/**
 * Check if the user prefers reduced motion.
 * @returns {boolean}
 */
function gmPrefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Resolve a duration, clamping to 0.01ms when reduced motion is preferred.
 * @param {number} ms — desired duration in milliseconds.
 * @returns {number}
 */
function gmResolveDuration(ms) {
  return gmPrefersReducedMotion() ? 0.01 : ms;
}

/**
 * Apply a CSS animation class, optionally removing it after the animation ends.
 * @param {Element} el - Target DOM element.
 * @param {string} className - CSS class to add (e.g. 'gm-fade-up').
 * @param {number} [duration=200] - Animation duration in ms (for cleanup timeout).
 * @param {boolean} [keepClass=false] - If true, do NOT remove the class after animation.
 */
function gmApply(el, className, duration, keepClass) {
  if (!el) return;
  duration = gmResolveDuration(duration || 200);
  el.classList.add(className);
  if (!keepClass) {
    setTimeout(function () {
      el.classList.remove(className);
    }, duration + 50);
  }
}

/**
 * Animate a list of elements with stagger delay between each.
 * @param {NodeList|Array<Element>} elements - The elements to animate.
 * @param {string} className - CSS class to add.
 * @param {number} [staggerMs=50] - Delay between each element (ms).
 * @param {number} [duration=200] - Animation duration (ms).
 * @param {boolean} [keepClass=false] - Keep the class after animation.
 */
function gmStagger(elements, className, staggerMs, duration, keepClass) {
  if (!elements || !elements.length) return;
  staggerMs = gmResolveDuration(staggerMs || 50);
  duration = duration || 200;
  Array.prototype.forEach.call(elements, function (el, i) {
    setTimeout(function () {
      gmApply(el, className, duration, keepClass);
    }, i * staggerMs);
  });
}

/**
 * Map a direction string to the corresponding CSS fade class.
 * @param {string} dir - 'up', 'down', 'left', 'right', 'in', 'scale'
 * @returns {string} CSS class name.
 */
function gmFadeClass(dir) {
  var map = {
    up:     'gm-fade-up',
    down:   'gm-fade-down',
    left:   'gm-fade-left',
    right:  'gm-fade-right',
    in:     'gm-fade-in',
    scale:  'gm-scale-in',
    bounce: 'gm-bounce-in',
  };
  return map[dir] || 'gm-fade-in';
}

/* ═══════════════════════════════════════════════════════════════════════
   PUBLIC ANIMATION TRIGGER FUNCTIONS
   ═══════════════════════════════════════════════════════════════════════ */

/**
 * Animate elements staggered into view from a direction.
 * @param {Element|string} container - Container element or CSS selector.
 * @param {string} selector - CSS selector for child elements.
 * @param {number} [delay=50] - Stagger delay in ms.
 * @param {string} [direction='up'] - 'up', 'down', 'left', 'right', 'in', 'scale'.
 */
function animateStaggerIn(container, selector, delay, direction) {
  if (typeof container === 'string') {
    container = document.querySelector(container);
  }
  if (!container) return;
  var items = container.querySelectorAll(selector);
  if (!items.length) return;
  delay = delay || 50;
  direction = direction || 'up';
  var className = gmFadeClass(direction);
  gmStagger(items, className, delay, 300);
}

/**
 * Count up a number in a DOM element.
 * @param {Element|string} element - Element or its id.
 * @param {number} targetValue - Final number.
 * @param {number} [duration=400] - Animation duration.
 * @param {function} [onComplete] - Optional callback when done.
 * @returns {function} A cancel function (call to skip to final value).
 */
function animateCountUp(element, targetValue, duration, onComplete) {
  if (typeof element === 'string') {
    element = document.getElementById(element);
  }
  if (!element) return function () {};
  duration = gmResolveDuration(duration || 400);

  // If already at target, just apply pulse
  if (parseInt(element.textContent) === targetValue) {
    gmApply(element, 'gm-count-pulse', 300);
    if (onComplete) onComplete();
    return function () {};
  }

  var startTime = null;
  var startValue = parseInt(element.textContent) || 0;
  var cancelled = false;
  var rafId = null;

  // Make it skippable on click
  element.classList.add('gm-counting');
  var skipHandler = function () {
    cancelAnimationFrame(rafId);
    if (!cancelled) {
      cancelled = true;
      element.textContent = targetValue;
      element.classList.remove('gm-counting');
      gmApply(element, 'gm-count-pulse', 300);
      if (onComplete) onComplete();
    }
  };
  element.addEventListener('click', skipHandler, { once: true });

  function tick(timestamp) {
    if (cancelled) return;
    if (!startTime) startTime = timestamp;
    var elapsed = timestamp - startTime;
    var progress = Math.min(elapsed / duration, 1);
    // Ease-out cubic
    var eased = 1 - Math.pow(1 - progress, 3);
    var current = Math.round(startValue + (targetValue - startValue) * eased);
    element.textContent = current;
    if (progress < 1) {
      rafId = requestAnimationFrame(tick);
    } else {
      element.textContent = targetValue;
      element.classList.remove('gm-counting');
      gmApply(element, 'gm-count-pulse', 300);
      if (onComplete) onComplete();
    }
  }
  rafId = requestAnimationFrame(tick);

  // Return cancel function
  return function () {
    if (!cancelled) {
      cancelled = true;
      cancelAnimationFrame(rafId);
      element.textContent = targetValue;
      element.classList.remove('gm-counting');
      if (onComplete) onComplete();
    }
  };
}

/**
 * Slide an element in from a direction using transform.
 * @param {Element|string} element - Element or CSS selector.
 * @param {string} [direction='up'] - 'up', 'down', 'left', 'right'.
 * @param {number} [duration=200] - Animation duration.
 */
function animateSlideIn(element, direction, duration) {
  if (typeof element === 'string') {
    element = document.querySelector(element);
  }
  if (!element) return;
  direction = direction || 'up';
  duration = gmResolveDuration(duration || 200);

  var className;
  switch (direction) {
    case 'up':    className = 'gm-slide-up'; break;
    case 'right': className = 'gm-slide-right'; break;
    default:      className = 'gm-fade-' + direction; break;
  }
  gmApply(element, className, duration);
}

/**
 * Shake an element with a quick horizontal tremor.
 * @param {Element|string} element - Element or CSS selector.
 * @param {number} [duration=400] - Animation duration.
 */
function animateShake(element, duration) {
  if (typeof element === 'string') {
    element = document.querySelector(element);
  }
  if (!element) return;
  duration = gmResolveDuration(duration || 400);
  element.classList.add('shake');
  setTimeout(function () {
    element.classList.remove('shake');
  }, duration + 50);
}

/**
 * Pulse an element's opacity or glow.
 * @param {Element|string} element - Element or CSS selector.
 * @param {number} [duration=2000] - Duration of one full cycle.
 * @param {string} [type='glow'] - 'glow' (box-shadow) or 'opacity'.
 */
function animatePulse(element, duration, type) {
  if (typeof element === 'string') {
    element = document.querySelector(element);
  }
  if (!element) return;
  duration = gmResolveDuration(duration || 2000);
  var className = type === 'opacity' ? 'gm-pulse-opacity' : 'gm-pulse-glow';

  // Shorten animation-duration via style to match requested cycle
  element.style.animationDuration = duration + 'ms';
  element.classList.add(className);
}

/**
 * Deal cards animation: fly from center with stagger and slight rotation.
 * @param {Element|string} container - Container element or selector.
 * @param {string} selector - CSS selector for card elements.
 * @param {number} [delay=80] - Stagger delay between cards (ms).
 * @param {number} [duration=500] - Animation duration (ms).
 */
function animateDealCards(container, selector, delay, duration) {
  if (typeof container === 'string') {
    container = document.querySelector(container);
  }
  if (!container) return;
  var cards = container.querySelectorAll(selector);
  if (!cards.length) return;
  delay = gmResolveDuration(delay || 80);
  duration = gmResolveDuration(duration || 500);

  Array.prototype.forEach.call(cards, function (card, i) {
    card.style.animationDuration = duration + 'ms';
    card.style.animationDelay = (i * delay) + 'ms';
    card.classList.add('gm-card-deal');
  });
}

/* ═══════════════════════════════════════════════════════════════════════
   SCREEN-SPECIFIC TRIGGER FUNCTIONS
   ═══════════════════════════════════════════════════════════════════════ */

/**
 * Title Screen: animate logo glow, buttons stagger, info card items.
 */
function animateTitleScreen() {
  // Logo glow is handled by CSS (#screen-title.active .title-logo)
  // Buttons stagger is handled by CSS n-th child rules
  // Info card items fade by CSS n-th child rules

  // Modal slide-up: applied when .active class is added
  var modal = document.getElementById('title-how-to-modal');
  if (modal && modal.classList.contains('active')) {
    gmApply(modal, 'gm-slide-up', 200);
  }
}

/**
 * Squad Builder: animate player card grid with row-based stagger.
 */
function animateSquadBuilder() {
  var grid = document.getElementById('player-grid');
  if (!grid) return;

  // Remove old stagger classes so re-render re-triggers
  var existing = grid.querySelectorAll('.gm-fade-up');
  Array.prototype.forEach.call(existing, function (el) {
    el.classList.remove('gm-fade-up');
    el.style.animationDelay = '';
    el.style.opacity = '';
  });

  var cards = grid.querySelectorAll('.player-card');
  if (!cards.length) return;

  // 2 rows per batch, ~4 cards per row = 8 cards per batch
  // 50ms per row = 100ms per batch of 2 rows
  var batchSize = 8;
  var rowDelay = 50;
  Array.prototype.forEach.call(cards, function (card, i) {
    var batch = Math.floor(i / batchSize);
    card.style.animationDelay = (batch * rowDelay) + 'ms';
    card.classList.add('gm-fade-up');
  });
}

/**
 * Formation Select: animate carousel slide, detail panel, badge.
 * @param {Element} activeCard - The currently active formation card.
 * @param {Element} detailPanel - The detail panel element.
 */
function animateFormationSelect(activeCard, detailPanel) {
  if (activeCard) {
    gmApply(activeCard, 'gm-fade-in', 150, true);
  }
  if (detailPanel) {
    gmApply(detailPanel, 'gm-fade-in', 150);
  }
  var badge = document.querySelector('.auto-recommend-badge');
  if (badge) {
    gmApply(badge, 'gm-bounce-in', 300);
  }
}

/**
 * Phase Selection: deal cards from center, then animate picks.
 * @param {Element} cardContainer - Container with phase-card elements.
 * @param {number} [delay=80] - Stagger delay.
 */
function animatePhaseSelection(cardContainer, delay) {
  if (cardContainer) {
    animateDealCards(cardContainer, '.phase-card', delay || 80);
  }
  var scouting = document.querySelector('.scouting-report');
  if (scouting) {
    gmApply(scouting, 'gm-fade-down', 200);
  }
}

/**
 * Animate a card being picked (shrinks and slides to tray).
 * @param {Element} card - The picked card element.
 * @param {function} [onComplete] - Callback when animation ends.
 */
function animatePhaseCardPicked(card, onComplete) {
  if (!card) return;
  gmApply(card, 'gm-card-picked', 200);
  if (onComplete) setTimeout(onComplete, 250);
}

/**
 * Update the combo chain preview with a fade transition.
 * @param {Element} previewEl - The combo chain preview element.
 */
function animateComboChainUpdate(previewEl) {
  if (!previewEl) return;
  previewEl.style.opacity = '0';
  setTimeout(function () {
    previewEl.style.opacity = '1';
    previewEl.style.transition = 'opacity 150ms ease-out';
  }, 20);
}

/**
 * Match Screen: animate dock players slide up, highlight eligible slots.
 * @param {string} [playerSelector='.dock-player']
 */
function animateMatchScreen(playerSelector) {
  playerSelector = playerSelector || '.dock-player';
  var dock = document.querySelector('.dock-scroll');
  if (dock) {
    var players = dock.querySelectorAll(playerSelector);
    gmStagger(players, 'gm-fade-up', 50, 150);
  }
}

/**
 * Animate auto-fill slots with stagger + glow pulse.
 * @param {Element} container - The pitch slots container.
 * @param {number} [slotDelay=80] - ms between each slot fill.
 * @param {number} [maxSlots=11]
 */
function animateAutoFillSlots(container, slotDelay, maxSlots) {
  if (!container) {
    container = document.querySelector('.pitch-canvas');
  }
  if (!container) return;
  slotDelay = slotDelay || 80;
  maxSlots = maxSlots || 11;

  var slots = container.querySelectorAll('.pitch-slot.filled');
  // Only animate newly filled slots (those without the animation class)
  var toAnimate = [];
  Array.prototype.forEach.call(slots, function (slot) {
    if (!slot.classList.contains('slot-fill-animate')) {
      toAnimate.push(slot);
    }
  });
  // Limit to maxSlots
  toAnimate = toAnimate.slice(0, maxSlots);

  Array.prototype.forEach.call(toAnimate, function (slot, i) {
    setTimeout(function () {
      slot.classList.add('slot-fill-animate');
      gmApply(slot, 'gm-fade-up', 80);
    }, i * slotDelay);
  });
}

/**
 * Animate a synergy badge lighting up green.
 * @param {Element} badgeEl
 */
function animateSynergyFlash(badgeEl) {
  if (!badgeEl) return;
  gmApply(badgeEl, 'gm-green-flash', 200);
}

/**
 * Phase Result: animate score count-up, formula columns, accordion, rows.
 * @param {number} finalScore
 * @param {number} [duration=400]
 * @returns {function} Cancel function for the count-up.
 */
function animatePhaseResult(finalScore, duration) {
  duration = duration || 400;
  var cancel = animateCountUp('.pr-score', finalScore, duration);

  var cols = document.querySelectorAll('.pr-formula-col');
  gmStagger(cols, 'gm-fade-up', 100, 400);

  var rows = document.querySelectorAll('.player-result-row');
  gmStagger(rows, 'gm-fade-left', 40, 150);

  return cancel;
}

/**
 * Animate a synergy accordion opening.
 * @param {Element} accordionEl
 */
function animateAccordionOpen(accordionEl) {
  if (!accordionEl) return;
  gmApply(accordionEl, 'gm-accordion-open', 200);
}

/**
 * Shop: stagger items from right, animate morale spend, buy confirm.
 * @param {Element} shopContainer
 */
function animateShopItems(shopContainer) {
  if (typeof shopContainer === 'string') {
    shopContainer = document.querySelector(shopContainer);
  }
  shopContainer = shopContainer || document.querySelector('.shop-list') || document.querySelector('.shop-container');
  if (!shopContainer) return;
  var items = shopContainer.querySelectorAll('.shop-item');
  gmStagger(items, 'gm-fade-right', 100, 300);
}

/**
 * Animate morale count change on spend.
 * @param {Element} moraleEl
 */
function animateMoraleSpend(moraleEl) {
  if (!moraleEl) return;
  moraleEl.classList.add('spend');
  setTimeout(function () {
    moraleEl.classList.remove('spend');
  }, 250);
}

/**
 * Animate buy button confirm scale.
 * @param {Element} btn
 */
function animateBuyConfirm(btn) {
  if (!btn) return;
  gmApply(btn, 'gm-scale-in', 100);
}

/**
 * Animate purchased item dimming with fade.
 * @param {Element} itemEl
 */
function animateItemPurchased(itemEl) {
  if (!itemEl) return;
  itemEl.classList.add('gm-item-dimmed');
}

/**
 * Round Result: dramatic verdict scale-up, score count-up, campaign map.
 * @param {number} yourScore
 * @param {number} targetScore
 * @param {function} [onComplete]
 * @returns {function} Cancel function.
 */
function animateRoundResult(yourScore, targetScore, onComplete) {
  // Verdict scale-up handled by CSS (.rr-verdict)
  var cancel = animateCountUp('.rr-score-value.yours', yourScore, 300);
  var cancel2 = animateCountUp('.rr-score-value.target', targetScore, 300, onComplete);

  var mapLine = document.querySelector('.campaign-map-line');
  if (mapLine) {
    gmApply(mapLine, 'gm-line-draw', 500);
  }

  return function () { cancel(); cancel2(); };
}

/**
 * Campaign Complete: gold sparkle particles, result rows stagger, Play Again pulse.
 * @param {boolean} isVictory
 */
function animateCampaignComplete(isVictory) {
  if (isVictory) {
    createSparkleParticles();
  }

  var rows = document.querySelectorAll('.result-row');
  gmStagger(rows, 'gm-fade-up', 100, 300);

  var btn = document.querySelector('.play-again-btn');
  if (btn) {
    setTimeout(function () {
      btn.classList.add('gm-fade-up');
      btn.style.animationDelay = '0s';
      btn.style.opacity = '1';
      setTimeout(function () {
        btn.classList.add('pulse');
        gmApply(btn, 'gm-pulse-glow-gold', 1500, true);
      }, 500);
    }, 100);
  }
}

/**
 * Spawn golden sparkle particles in a fixed container.
 * @param {number} [count=20]
 */
function createSparkleParticles(count) {
  count = count || 20;
  var container = document.querySelector('.gm-sparkle-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'gm-sparkle-container';
    document.body.appendChild(container);
  }

  var symbols = ['✦', '◆', '·', '✧', '▪'];
  for (var i = 0; i < count; i++) {
    var sparkle = document.createElement('span');
    sparkle.className = 'gm-sparkle';
    sparkle.textContent = symbols[i % symbols.length];
    sparkle.style.left = (10 + Math.random() * 80) + '%';
    sparkle.style.top = (10 + Math.random() * 60) + '%';
    sparkle.style.fontSize = (8 + Math.random() * 10) + 'px';
    sparkle.style.animationDelay = (Math.random() * 0.8) + 's';
    sparkle.style.animationDuration = (1.2 + Math.random() * 0.6) + 's';
    container.appendChild(sparkle);
  }

  // Auto-clean after animation
  setTimeout(function () {
    if (container.parentNode) {
      container.parentNode.removeChild(container);
    }
  }, 4000);
}

/**
 * Animate the budget bar width change with smooth transition.
 * @param {Element} barFill - The budget bar fill element.
 */
function animateBudgetBar(barFill) {
  if (!barFill) return;
  // The transition is handled by CSS class gm-budget-animate on the parent
  // Just ensure the transition class is present
  var parent = barFill.parentElement;
  if (parent) {
    parent.classList.add('gm-budget-animate');
  }
}

/**
 * Animate a modal sliding up from bottom.
 * @param {Element|string} modal - Modal element or selector.
 */
function animateModalUp(modal) {
  if (typeof modal === 'string') {
    modal = document.querySelector(modal);
  }
  if (!modal) return;
  gmApply(modal, 'gm-slide-up', 200);
}

/**
 * Animate sidebar panel sliding in from the right.
 * @param {Element|string} panel - Panel element or selector.
 */
function animateSidebarIn(panel) {
  if (typeof panel === 'string') {
    panel = document.querySelector(panel);
  }
  if (!panel) return;
  gmApply(panel, 'gm-slide-right', 200);
}

/**
 * Animate selected player pill fade-in.
 * @param {Element} pill - The pill element.
 */
function animatePillFadeIn(pill) {
  if (!pill) return;
  gmApply(pill, 'gm-fade-in', 100);
}
