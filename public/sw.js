const CACHE = 'pritden-v1';

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    caches.open(CACHE).then(async (cache) => {
      // Documents: network-first. Serving cached HTML for navigations meant a
      // returning visitor never saw a redeploy until they visited twice — the
      // cache is now only an offline fallback, never the source of truth.
      if (request.mode === 'navigate') {
        try {
          const fresh = await fetch(request);
          if (fresh && fresh.ok) cache.put(request, fresh.clone());
          return fresh;
        } catch {
          const cached = await cache.match(request);
          if (cached) return cached;
          throw new Error('offline and no cached page');
        }
      }

      // Static same-origin assets: cache-first, revalidate in the background.
      const cached = await cache.match(request);
      if (cached) {
        event.waitUntil(
          fetch(request)
            .then((resp) => {
              if (resp && resp.ok) cache.put(request, resp.clone());
            })
            .catch(() => {})
        );
        return cached;
      }

      try {
        const fresh = await fetch(request);
        if (fresh && fresh.ok) cache.put(request, fresh.clone());
        return fresh;
      } catch {
        throw new Error('offline and not cached');
      }
    })
  );
});
