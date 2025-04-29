self.addEventListener('install', function(e) {
  console.log('[ServiceWorker] Install');
});

self.addEventListener('fetch', function(e) {
  // Let all requests go to the network for now
});