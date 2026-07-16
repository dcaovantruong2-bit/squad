const CACHE_NAME = 'squad-v1';
const urlsToCache = [
  '/',
  '/game.html',
  '/game-engine.js',
  '/game-ui.js',
  '/game.css',
  '/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
