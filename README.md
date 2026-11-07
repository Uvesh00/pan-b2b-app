# Pan & Tobacco B2B Wholesale Web Application 🏪📦

A modern, full-stack B2B wholesale ordering platform built specifically for **Indian FMCG, Pan Masala, Tobacco, Cigarettes, Supari, and Accessories distributors and Pan Shop retailers**.

---

## 🚀 Live Demo & Quick Start

The application runs with **zero external dependencies** using Python's standard library and SQLite3.

```bash
# 1. Navigate to the project directory
cd /home/uvesh/.gemini/antigravity/scratch/pan-b2b-app

# 2. Run the server (default port: 8080)
./start.sh 8080
# Or directly:
python3 server.py 8080

# 3. Open in your browser
http://localhost:8080
```

---

## 💡 Business Strategy: "Zomato Wala" vs "Each Wholesaler (White-Label)"

### 1. The Dilemma
> **User Question:** *"Which one is a better idea: Zomato-style marketplace or a dedicated white-label app for each wholesaler where we change the name & logo?"*

### 2. Comparison Breakdown

| Parameter | 🌐 Zomato-Style (Multi-Wholesaler Marketplace) | 🏪 Single Wholesaler (White-Label Dedicated App) |
| :--- | :--- | :--- |
| **Wholesaler Acceptance** | ❌ **High Resistance**: Wholesalers fear competitor wholesalers will see their rates or poach their pan shop clients. | 🏆 **Loved by Wholesalers**: "Yeh meri apni dukan ki official app hai!" Gives pride & digital presence. |
| **Wholesale Margin Secrecy** | ❌ Hard to maintain: Wholesalers work on razor-thin 1% to 3% margins and hate public price disclosure. | 🏆 **100% Private**: Prices & credit terms are only visible between the wholesaler and their approved retailers. |
| **Khata / Udhaar (Credit)** | ❌ Difficult: Strangers won't extend ₹20,000 credit to unknown pan shops. | 🏆 **Seamless**: Wholesaler manages their existing 100-300 pan shops' credit limits directly. |
| **Your Revenue Model** | High initial risk: Needs deep marketing, logistics coordination, and commission friction. | 🏆 **Immediate Cash & Recurring SaaS**: <br>• Setup Fee: ₹5,000 - ₹25,000 per wholesaler<br>• Monthly AMC: ₹1,500 - ₹3,000/month |
| **Sales Pitch Ease** | Hard to convince 20 wholesalers at once in the same mandi. | 🏆 **Very Easy**: Pitch 1 wholesaler, customize their name & logo in 30 seconds, close the deal! |

### 3. The Winning Recommendation: **"White-Label First, Marketplace Built-in"**
**Go with the White-Label Model first!**
- Sell each wholesaler their dedicated, branded ordering app.
- Give them an ordering link like `ganeshwholesale.in` or an APK/PWA.
- Their 100-300 retailers stop sending messy handwritten slips or 6 AM WhatsApp voice notes and order directly by box count.
- **The app you have now includes a 1-Click Toggle**: You can demonstrate both the **Dedicated Storefront** and the **Multi-Wholesaler Zomato Mandi** live in your client presentation!

---

## 🌟 Key Features of this Ready-to-Use Web App

### For Retailers (Pan Shop Owners):
1. **B2B Box & Carton Ordering**: All items are sold in wholesale units (Box of 30 Pouches, Master Pettie of 600, Outer Dabba of 10 Cigarette Packs, Bidi Bales, Lighter Display Trays).
2. **Transparent Margin Calculator**: Every product shows the **Pan Shop Munafa (₹ & % Margin)** so retailers see their profit upfront.
3. **Multi-Payment Modes**:
   - 💵 **Cash on Delivery (COD)**
   - 📱 **Instant UPI QR Code** (Direct to Wholesaler's VPA)
   - 📒 **7-Day Khata (Udhaar)** with real-time credit limit checking
4. **1-Click WhatsApp Order Forwarding**: Generates formatted, emoji-rich WhatsApp orders ready to send to the wholesaler with one click.
5. **Instant Kutcha Bill / Invoice Printing**: Print 3-inch thermal POS receipts or A4 invoices.

### For Wholesalers (Godown & Cash Counter):
1. **Live Order Dispatch Queue**: Receive orders in real-time, accept, pack, dispatch (`Pending` → `Confirmed` → `Out for Delivery` → `Delivered`).
2. **Wholesale Rate Manager**: Update prices on volatile items (like Vimal, Gold Flake) instantly.
3. **Retailer Khata Ledger**: Track credit balance for every pan shop and record cash/UPI settlements.
4. **White-Label Studio**: Live editor to change the shop name, owner name, WhatsApp number, UPI ID, logo, and theme colors in 10 seconds.

---

## 🗄️ Database Architecture (SQLite3)

- `wholesalers`: Wholesaler profiles, branding, UPI, delivery policies, min order amounts.
- `categories`: Pan Masala, Zarda & Tobacco, Cigarettes & Bidi, Supari & Sweet Pan, Mints & Candies, Accessories.
- `products`: 60+ pre-seeded authentic Indian brands (Vimal, Kamla Pasand, Tansen, Rajnigandha, RMD, Miraj, Baba 120, Gold Flake, Classic, Marlboro, Wave, Cricket, BIC, OCB, etc.).
- `retailers`: Pan shop profiles, owner contact, area, and running Khata balance.
- `orders` & `order_items`: Full transactional records with box quantities and profit estimates.
- `khata_ledger`: Double-entry style credit/debit audit trail for retailer Udhaar.

---

## 🛠️ Project Structure

```
pan-b2b-app/
├── server.py              # Zero-dependency Python 3 HTTP REST Server
├── database.py            # SQLite schema & realistic Indian B2B data seeder
├── pan_b2b.db             # SQLite persistent database
├── start.sh               # One-click startup script
├── static/
│   ├── index.html         # Responsive Single Page Application
│   ├── app.js             # Client controller, state & cart management
│   └── styles.css         # Print & UI stylesheets
└── README.md              # Documentation & pitch guide
```
