// Service Worker для push-уведомлений
self.addEventListener('push', function(event) {
  let data = {};
  if (event.data) {
    data = event.data.json();
  } else {
    data = {
      title: "TaskMentor",
      body: "Новое уведомление!"
    };
  }

  const options = {
    body: data.body,
    icon: '/static/favicon.ico',  // можешь заменить на свою иконку
    badge: '/static/favicon.ico',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'open',
        title: 'Открыть',
        icon: '/static/favicon.ico'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  if (event.action === 'open') {
    clients.openWindow('/');
  } else {
    clients.openWindow('/');
  }
});