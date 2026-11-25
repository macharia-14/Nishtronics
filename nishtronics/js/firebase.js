// ════════════════════════════════════════════════════════════
// NISHTRONICS SOUNDLABS — FIREBASE SERVICE LAYER
// ════════════════════════════════════════════════════════════
//
// SETUP STEPS:
//   1. Go to console.firebase.google.com
//   2. Create project "nishtronics-soundlabs"
//   3. Enable Firestore Database (start in production mode)
//   4. Enable Authentication → Email/Password
//   5. Copy your config object into FIREBASE_CONFIG below
//   6. On the Admin panel → Dashboard → click "Seed Firestore"
//
// FIRESTORE COLLECTIONS:
//   /products  — product catalog
//   /orders    — WhatsApp order log
//   /bookings  — appointment bookings
//
// FALLBACK: If Firebase is not configured, the public site falls back to
// data/products.json. The ADMIN PANEL requires Firebase (no local login).
// ════════════════════════════════════════════════════════════

const FIREBASE_CONFIG = {
  apiKey:            "REPLACE_WITH_YOUR_API_KEY",
  authDomain:        "REPLACE.firebaseapp.com",
  projectId:         "REPLACE_WITH_PROJECT_ID",
  storageBucket:     "REPLACE.appspot.com",
  messagingSenderId: "REPLACE",
  appId:             "REPLACE_WITH_APP_ID"
};

let db = null;
let auth = null;
let FIREBASE_READY = false;

async function initFirebase() {
  if (FIREBASE_CONFIG.apiKey === "REPLACE_WITH_YOUR_API_KEY") {
    console.info('[Nishtronics] Firebase not configured — running in local mode.');
    updateFirebaseStatus();
    return false;
  }
  try {
    const { initializeApp } = await import('https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js');
    const { getFirestore, collection, getDocs, addDoc, updateDoc, deleteDoc, doc, query, orderBy, onSnapshot }
      = await import('https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js');
    const authMod = await import('https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js');
    const { getAuth } = authMod;
    window.FSAuth = authMod;

    const app = initializeApp(FIREBASE_CONFIG);
    db   = getFirestore(app);
    auth = getAuth(app);
    FIREBASE_READY = true;
    window.FIREBASE_READY = true;   // `let` globals are not window props; cart.js reads window.FIREBASE_READY

    window.FS = { collection, getDocs, addDoc, updateDoc, deleteDoc, doc, query, orderBy, onSnapshot, db };
    console.info('[Nishtronics] Firebase connected');
    updateFirebaseStatus();
    return true;
  } catch (err) {
    console.warn('[Nishtronics] Firebase init failed:', err.message);
    updateFirebaseStatus();
    return false;
  }
}

function updateFirebaseStatus() {
  document.querySelectorAll('.fb-dot').forEach(el => el.classList.toggle('live', FIREBASE_READY));
  document.querySelectorAll('.fb-label').forEach(el => {
    el.textContent = FIREBASE_READY ? 'Live (Firestore)' : 'Local mode';
  });
}

// ── Products ──────────────────────────────────────────
async function fsGetProducts() {
  await window.firebaseReady;   // init is async; without this the catalog always fell back to products.json
  if (!FIREBASE_READY) return null;
  const { collection, getDocs, query, orderBy } = window.FS;
  const snap = await getDocs(query(collection(db, 'products'), orderBy('brand')));
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}

async function fsAddProduct(data) {
  if (!FIREBASE_READY) return null;
  const { collection, addDoc } = window.FS;
  return addDoc(collection(db, 'products'), { ...data, createdAt: Date.now() });
}

async function fsUpdateProduct(id, data) {
  if (!FIREBASE_READY) return null;
  const { doc, updateDoc } = window.FS;
  return updateDoc(doc(db, 'products', id), data);
}

async function fsDeleteProduct(id) {
  if (!FIREBASE_READY) return null;
  const { doc, deleteDoc } = window.FS;
  return deleteDoc(doc(db, 'products', id));
}

async function fsSeedProducts(products) {
  if (!FIREBASE_READY) { alert('Firebase not configured yet.'); return 0; }
  const { collection, addDoc } = window.FS;
  let count = 0;
  for (const p of products) {
    await addDoc(collection(db, 'products'), p);
    count++;
  }
  return count;
}

// ── Orders ────────────────────────────────────────────
async function fsAddOrder(data) {
  await window.firebaseReady;
  if (!FIREBASE_READY) return null;
  const { collection, addDoc } = window.FS;
  return addDoc(collection(db, 'orders'), { ...data, createdAt: Date.now() });
}

async function fsGetOrders() {
  if (!FIREBASE_READY) return null;
  const { collection, getDocs, query, orderBy } = window.FS;
  const snap = await getDocs(query(collection(db, 'orders'), orderBy('createdAt', 'desc')));
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}

async function fsUpdateOrder(id, data) {
  if (!FIREBASE_READY) return null;
  const { doc, updateDoc } = window.FS;
  return updateDoc(doc(db, 'orders', id), data);
}

// ── Bookings ──────────────────────────────────────────
async function fsAddBooking(data) {
  await window.firebaseReady;
  if (!FIREBASE_READY) return null;
  const { collection, addDoc } = window.FS;
  return addDoc(collection(db, 'bookings'), { ...data, createdAt: Date.now() });
}

async function fsGetBookings() {
  if (!FIREBASE_READY) return null;
  const { collection, getDocs, query, orderBy } = window.FS;
  const snap = await getDocs(query(collection(db, 'bookings'), orderBy('createdAt', 'desc')));
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}

// ── Admin Auth (Firebase Authentication) ──────────────
// The ONLY thing that protects write access is Firestore security rules
// (see firestore.rules). The login screen just collects credentials.
async function fsAdminLogin(email, password) {
  if (!FIREBASE_READY) throw new Error('not-configured');
  return window.FSAuth.signInWithEmailAndPassword(auth, email, password);
}

async function fsAdminLogout() {
  if (!FIREBASE_READY) return;
  return window.FSAuth.signOut(auth);
}

// Calls cb(user|null) now and whenever the session changes (restores login on refresh)
function fsOnAuth(cb) {
  if (!FIREBASE_READY) { cb(null); return; }
  window.FSAuth.onAuthStateChanged(auth, cb);
}

async function fsChangePassword(newPassword) {
  if (!FIREBASE_READY || !auth.currentUser) throw new Error('not-signed-in');
  return window.FSAuth.updatePassword(auth.currentUser, newPassword);
}

// Auto-init on load. Pages that need to wait for it can `await window.firebaseReady`.
window.firebaseReady = initFirebase();
