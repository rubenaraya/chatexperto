const currentCache = 'v0';

const cacheFirst = (event) => {
  event.respondWith(
    caches.match(event.request).then((cacheResponse) => {
      return cacheResponse || fetch(event.request).then((networkResponse) => {
        return caches.open(currentCache).then((cache) => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        })
      })
    })
  );
};

const networkFirst = (event) => {
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        return caches.open(currentCache).then((cache) => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        })
      })
      .catch(() => {
        return caches.match(event.request);
      })
  )
};

const networkOnly = (event) => {
  event.respondWith(fetch(event.request));
};

const staleWhileRevalidate = (event) => {
  event.respondWith(
    caches.match(event.request).then((cacheResponse) => {
      if (cacheResponse) {
        fetch(event.request).then((networkResponse) => {
          return caches.open(currentCache).then((cache) => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          })
        });
        return cacheResponse;
      } else {
        return fetch(event.request).then((networkResponse) => {
          return caches.open(currentCache).then((cache) => {
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          })
        });
      }
    })
  );
};

const strategy = {
  cacheFirst,
  networkFirst,
  networkOnly,
  staleWhileRevalidate,
};

const router = {
	find: (url) => router.routes.find(it => url.match(it.url)),
	routes: [
	]
};

var contentToCache = [
];

self.addEventListener( 'install', event => {
	event.waitUntil(
		caches.open(currentCache)
		.then( (cache) => {
			return cache.addAll(contentToCache);
		})
		.then( () => {
			return self.skipWaiting();
		})
	);
});

self.addEventListener( 'activate', event => {
	event.waitUntil(
		caches.keys().then(cacheNames => Promise.all(
			cacheNames
			.filter(cacheName => cacheName !== currentCache)
			.map(cacheName => caches.delete(cacheName))
		))
	);
	self.clients.claim();
});

self.addEventListener( 'fetch', event => {
	const found = router.find(event.request.url);
	if (found) found.handle(event);
});

self.addEventListener( 'message', (event) => {
	if (event.data && event.data.type === 'DIR') {
		var dir = event.data.payload;
	}
});
