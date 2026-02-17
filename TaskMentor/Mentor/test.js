function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

async function subscribeUserToPush() {
  console.log("✅ push.js loaded");
  console.log("➡️ subscribeUserToPush called");

  if (!('serviceWorker' in navigator)) {
    console.log("❌ no serviceWorker");
    return;
  }
  if (!('PushManager' in window)) {
    console.log("❌ no PushManager");
    return;
  }

  try {
    console.log("🟦 registering SW...");
    let reg;
    try {
      reg = await navigator.serviceWorker.register('/sw.js');
      console.log("✅ SW registered:", reg);
    } catch (e) {
      console.error("❌ SW register failed:", e);
      return;
    }

    let registration;
    try {
      registration = await navigator.serviceWorker.ready;
      console.log("✅ SW ready:", registration);
    } catch (e) {
      console.error("❌ SW ready failed:", e);
      return;
    }

    const perm = await Notification.requestPermission();
    console.log("🔔 Notification permission:", perm);
    if (perm !== "granted") return;

    const vapidPublicKey = window.PUSH_CONFIG && window.PUSH_CONFIG.VAPID_PUBLIC_KEY;
    console.log("🔑 VAPID key present:", !!vapidPublicKey);
    if (!vapidPublicKey) {
      console.log("❌ VAPID public key missing");
      return;
    }

    // ✅ не создаём новую подписку, если уже есть
    let subscription = await registration.pushManager.getSubscription();
    if (!subscription) {
      console.log("🧷 creating new subscription...");
      subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey),
      });
      console.log("✅ subscription created");
    } else {
      console.log("✅ existing subscription reused");
    }

    const csrftoken = getCookie("csrftoken");
    console.log("🍪 csrftoken present:", !!csrftoken);

    console.log("📡 sending subscription to backend...");
    const response = await fetch('/save-push-subscription/', {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken,
      },
      body: JSON.stringify(subscription),
    });

    console.log("📨 backend status:", response.status);
    console.log("📨 backend text:", await response.text());
  } catch (err) {
    console.error('❌ Push ошибка:', err);
  }
}

document.addEventListener('DOMContentLoaded', function () {
  subscribeUserToPush();
});
