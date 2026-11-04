# Nishtronics Soundlabs — Setup Guide

## Site Structure

```
nishtronics/
├── index.html          Homepage
├── about.html          About page
├── services.html       Services page
├── products.html       Product catalog with filters
├── gallery.html        Photo gallery with lightbox
├── booking.html        Appointment booking form
├── cart.html           Cart + WhatsApp checkout
├── contact.html        Contact form
├── admin/
│   └── index.html      Admin CMS panel (Firebase login)
├── firestore.rules     Security rules (paste into Firebase)
├── images/             placeholder.svg, products/ (deploy), _incoming/ (raw, don't deploy)
├── tools/              set-contact.py, prepare-images.py
├── css/
│   └── style.css       Full design system
├── js/
│   ├── main.js         Core JS (nav, cart panel, products, toasts, lightbox)
│   ├── firebase.js     Firebase service layer
│   ├── products.js     Products page filtering
│   └── cart.js         Cart page + WhatsApp order
└── data/
    └── products.json   35+ product catalog (local fallback)
```

---

## Step 1 — Set Your Real Contact Details

Run once from the project root (needs Python 3):

```
python tools/set-contact.py 254712345678 --instagram https://instagram.com/yourshop --facebook https://facebook.com/yourshop
```

This updates the WhatsApp number, the phone number text and the social links in every page and in `js/`. Safe to re-run. Social flags are optional. If you have no Facebook or Instagram page yet, delete those icon links from the footers rather than leaving the generic homepage links.

The site shows no email address. Customers reach you by WhatsApp and phone.

---

## Step 2 — Firebase Setup (Optional but Recommended)

Without Firebase the public site still works from `data/products.json`, but **the admin panel requires Firebase** (there is no local password login). Firebase also stores orders and bookings and lets you edit products without touching files.

### Create Firebase Project

1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Click **Create a project** → name it `nishtronics-soundlabs`
3. Disable Google Analytics (not needed)

### Enable Firestore

1. In Firebase Console → **Build → Firestore Database**
2. Click **Create database**
3. Choose **Production mode** → select a region (e.g., `europe-west1` or `us-central1`)

### Create the one admin account

1. Firebase Console → **Build → Authentication → Get started → Email/Password → Enable**
2. **Users → Add user** with your own email and a strong password
3. Copy that user's **User UID**
4. **Authentication → Settings → User actions**: turn **off** "Enable create (sign-up)". Without this, anyone with your public API key can register an account.

### Set Firestore Rules

1. Open `firestore.rules` from this folder
2. Replace `PASTE_ADMIN_UID_HERE` with the UID from above
3. Firestore → **Rules** tab → paste the whole file → **Publish**

The rules let the public read products, let customers create (only) a validated order or booking, and allow everything else only for your admin UID. Orders/bookings are size-capped and shape-checked to limit spam. The rules have not been run against the Firebase emulator yet, so after publishing, place a test order and a test booking from the site and confirm they appear in the admin panel.

### Get Your Config

1. Firebase Console → **Project Settings** (gear icon) → **General**
2. Scroll to **Your apps** → click **Web** (`</>`)
3. Register app → copy the `firebaseConfig` object

### Paste Config into `js/firebase.js`

```javascript
const FIREBASE_CONFIG = {
  apiKey:            "AIza...",
  authDomain:        "nishtronics-soundlabs.firebaseapp.com",
  projectId:         "nishtronics-soundlabs",
  storageBucket:     "nishtronics-soundlabs.appspot.com",
  messagingSenderId: "12345678",
  appId:             "1:12345678:web:abc123"
};
```

### Seed Products to Firestore

1. Open `admin/index.html` in a browser
2. Sign in with the admin email and password you created above
3. On the Dashboard → click **"Seed Firestore from products.json"**
4. This uploads all 35+ products to Firestore (run once only)

---

## Step 3 — Admin Panel

**URL:** `yoursite.com/admin/index.html` (marked noindex, but not hidden; the Firestore rules are what protect your data)
**Login:** the Firebase email/password account from Step 2. Change the password under **Settings**.

### Admin Features
- **Dashboard** — product count, stock overview, quick actions
- **Products** — add/edit/delete products, toggle stock, update prices inline
- **Orders** — log WhatsApp orders, track status (New / Confirmed / Completed / Cancelled)
- **Bookings** — log booking requests, track appointment status
- **Settings** — change admin password

---

## Step 4 — Deploy

### Option A: Netlify (Recommended, Free)
1. Go to [netlify.com](https://netlify.com) → drag and drop the `nishtronics/` folder
2. Your site is live in seconds with a free URL
3. Add a custom domain in Netlify settings

### Option B: Firebase Hosting
```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Set public directory to: nishtronics/
firebase deploy
```

### Option C: Any Static Host
Upload all files to your host via FTP. No server-side code required.

---

## Product Photos

1. Put raw photos in `images/_incoming/` named after the product id, e.g. `kw-6x9-kfc1669s.jpg`
2. `pip install pillow` (once), then `python tools/prepare-images.py`
3. Compressed WebP files (max 800px, aim under 100 KB) land in `images/products/<id>.webp`. The site finds them by id automatically, in both Firebase and local mode. No data edits needed.
4. `python tools/prepare-images.py --missing` lists products that still have no photo.

Deploy `images/products/`; do **not** upload `images/_incoming/`. Products without a photo show `images/placeholder.svg`. Keep each image small: free hosting plans cap daily bandwidth.

An explicit `image` value on a product (path or URL, set in the admin or JSON) overrides this convention.

## Customising Products

Without Firebase, edit `data/products.json` directly. Each product has:

```json
{
  "id": "unique-id",
  "name": "Kenwood KFC-W3016 12\" Sub",
  "brand": "Kenwood",
  "category": "subwoofers",
  "subcategory": "12inch",
  "price": 12500,
  "description": "Short description…",
  "specs": { "Power": "1500W", "Impedance": "2 Ohm" },
  "badge": "bestseller",
  "inStock": true
}
```

(`image` is optional; see Product Photos.)

**Categories:** `speakers`, `subwoofers`, `headunits`, `amplifiers`, `accessories`, `trackers`, `secondhand`

**Badges:** `bestseller`, `new`, `popular`, `high-end`, `2nd-hand`, `custom`

---

## Design System Notes

The site uses a custom dark luxury design system:

- **Colors:** `--gold: #e8c96a`, `--ink: #05050a`, backgrounds from `--ink-1` to `--ink-4`
- **Fonts:** Barlow Condensed (headings) + Outfit (body) + Space Mono (numbers/prices)
- **Image sections:** `.imgbg` class with `.cut-top` / `.cut-top-r` for diagonal diagonal flows
- **Animations:** `.reveal` class + IntersectionObserver for scroll-triggered entries
- **Cart:** Slide-in panel triggered from nav — no page reload needed
