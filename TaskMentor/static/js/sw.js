self.addEventListener('push', function (event) {
  let data = { title: "TaskMentor", body: "Новое уведомление!" };

  if (event.data) {
    try { data = event.data.json(); } catch (e) {}
  }

  const options = {
    body: data.body,
    icon: "/static/favicon.ico",
    badge: "/static/favicon.ico",
    vibrate: [100, 50, 100],
    data: { dateOfArrival: Date.now(), primaryKey: 1 },
    actions: [
      { action: "open", title: "Открыть", icon: "/static/favicon.ico" }
    ]
  };

  event.waitUntil(self.registration.showNotification(data.title, options));
});

self.addEventListener('notificationclick', function (event) {
  event.notification.close();
  event.waitUntil(clients.openWindow("/"));
});