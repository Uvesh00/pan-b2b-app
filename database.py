"""
Database setup and seeding for Pan & Tobacco Wholesale B2B Web App
"""
import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pan_b2b.db')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Remove existing db if corrupted or re-initializing
    if os.path.exists(DB_FILE):
        try:
            os.remove(DB_FILE)
        except Exception:
            pass

    conn = get_db()
    cursor = conn.cursor()

    # Settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')

    # Wholesalers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wholesalers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        tagline TEXT,
        slug TEXT UNIQUE,
        owner_name TEXT,
        phone TEXT,
        whatsapp TEXT,
        upi_id TEXT,
        address TEXT,
        city TEXT,
        min_order_amount REAL DEFAULT 1000,
        delivery_time TEXT DEFAULT '2-4 Hours',
        delivery_charges REAL DEFAULT 0,
        free_delivery_above REAL DEFAULT 2500,
        rating REAL DEFAULT 4.8,
        theme_color TEXT DEFAULT '#16a34a',
        logo_icon TEXT DEFAULT 'store',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        hindi_name TEXT,
        icon TEXT,
        description TEXT,
        sort_order INTEGER DEFAULT 0
    )''')

    # Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wholesaler_id INTEGER,
        category_id TEXT,
        name TEXT NOT NULL,
        hindi_name TEXT,
        brand TEXT,
        box_size_desc TEXT,
        units_per_box INTEGER DEFAULT 1,
        wholesale_price REAL NOT NULL,
        mrp REAL NOT NULL,
        retailer_margin_amount REAL,
        retailer_margin_pct REAL,
        min_boxes INTEGER DEFAULT 1,
        in_stock INTEGER DEFAULT 1,
        badge TEXT,
        image_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id),
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )''')

    # Retailers table (Pan Shops)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS retailers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        shop_name TEXT NOT NULL,
        owner_name TEXT NOT NULL,
        phone TEXT UNIQUE,
        address TEXT,
        area TEXT,
        city TEXT,
        khata_balance REAL DEFAULT 0,
        credit_limit REAL DEFAULT 20000,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_code TEXT UNIQUE,
        wholesaler_id INTEGER,
        retailer_id INTEGER,
        retailer_name TEXT,
        retailer_phone TEXT,
        retailer_address TEXT,
        total_boxes INTEGER,
        subtotal REAL,
        discount REAL DEFAULT 0,
        delivery_fee REAL DEFAULT 0,
        total_amount REAL,
        total_profit_estimate REAL DEFAULT 0,
        payment_mode TEXT, /* 'COD', 'UPI', 'KHATA' */
        order_status TEXT DEFAULT 'pending', /* 'pending', 'confirmed', 'out_for_delivery', 'delivered', 'cancelled' */
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wholesaler_id) REFERENCES wholesalers (id),
        FOREIGN KEY (retailer_id) REFERENCES retailers (id)
    )''')

    # Order Items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        product_name TEXT,
        brand TEXT,
        box_size_desc TEXT,
        box_qty INTEGER,
        price_per_box REAL,
        mrp_per_box REAL,
        subtotal REAL,
        profit_per_box REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )''')

    # Khata ledger entries
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS khata_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        retailer_id INTEGER,
        wholesaler_id INTEGER,
        order_id INTEGER,
        type TEXT, /* 'debit' (order on credit), 'credit' (payment received) */
        amount REAL,
        balance_after REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    seed_data(cursor, conn)
    conn.close()
    print("Database initialized and seeded successfully.")

def seed_data(cursor, conn):
    print("Seeding sample data...")

    # Default App Settings
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('platform_mode', 'white_label')")
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('active_wholesaler_id', '1')")
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('app_brand_name', 'Shree Ganesh Wholesale')")

    # Wholesalers
    wholesalers = [
        (1, "Shree Ganesh Pan & Tobacco Wholesalers", "Sabse Bada Stock, Asli Wholesale Rate", "shree-ganesh-wholesale",
         "Rajeshwar Bhai Patel", "+91 98765 43210", "919876543210", "shreeganesh@upi",
         "Shop G-14, Old Galla Mandi, Near Tower Chowk", "Kanpur / Ahmedabad", 1200, "2 - 4 Ghante me Delivery",
         0, 2500, 4.9, "#15803d", "store"),
        (2, "Mahadev Supari & Cigarette Mart", "Branded Cigarettes & Premium Supari Distributor", "mahadev-mart",
         "Suresh Chand Gupta", "+91 98222 11000", "919822211000", "mahadevpan@okaxis",
         "Shop 42, Station Road, Tobacco Line", "Delhi NCR / Jaipur", 2000, "3 - 5 Ghante",
         60, 4000, 4.7, "#2563eb", "flame"),
        (3, "Kailash Brothers FMCG & Tobacco", "Direct Factory Supply - Best Margins for Pan Dukan", "kailash-brothers",
         "Kailashnath Agarwal", "+91 97111 88990", "919711188990", "kailashfmcg@ybl",
         "Block B, APMC Market Yard, Gate 2", "Lucknow / Patna", 1000, "1 - 3 Ghante Superfast",
         0, 2000, 4.8, "#b45309", "truck")
    ]
    cursor.executemany('''
    INSERT INTO wholesalers (id, name, tagline, slug, owner_name, phone, whatsapp, upi_id, address, city,
                             min_order_amount, delivery_time, delivery_charges, free_delivery_above, rating,
                             theme_color, logo_icon)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', wholesalers)

    # Categories
    categories = [
        ("pan_masala", "Pan Masala", "पान मसाला", "sparkles", "Vimal, Kamla Pasand, Tansen, Rajnigandha, RMD Boxes", 1),
        ("tobacco", "Zarda & Tobacco", "जर्दा / तम्बाकू / खैनी", "layers", "Miraj, Baba 120, Chaini Khaini, Raja Chhap", 2),
        ("cigarettes", "Cigarettes & Bidi", "सिगरेट व बीड़ी", "flame", "Gold Flake, Classic, Marlboro, Wave, Pataka 502", 3),
        ("supari", "Supari & Sweet Pan", "सुपारी व मीठा सामग्री", "heart", "Kesar Supari, Tukda, Chaman Bahar, Silver Elaichi", 4),
        ("confectionery", "Mints & Candies", "टॉफ़ी व म‍िंट्स", "gift", "Pulse Candy, Orbit, Center Fresh, Halls, Mentos", 5),
        ("accessories", "Accessories & Papers", "लाइटर, पेपर, चूना", "package", "Cricket/Bic Lighter, OCB/Roor Papers, Chuna Tube", 6)
    ]
    cursor.executemany('''
    INSERT INTO categories (id, name, hindi_name, icon, description, sort_order)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', categories)

    # 30+ Realistic Pan Shop Wholesale Products
    products = [
        # PAN MASALA
        (1, "pan_masala", "Vimal Pan Masala (₹5 Pack)", "विमल पान मसाला (छोटा डब्बा)", "Vimal", "Box of 30 Pouches", 30, 135.0, 150.0, 15.0, 10.0, 2, 1, "Top Seller", "vimal"),
        (1, "pan_masala", "Vimal Pan Masala Master Carton (Pettie)", "विमल पेटी (कार्टन)", "Vimal", "Pettie of 20 Boxes (600 Pouches)", 600, 2600.0, 3000.0, 400.0, 13.3, 1, 1, "Wholesale Bulk", "vimal_box"),
        (1, "pan_masala", "Kamla Pasand Silver Coated (₹10 Pack)", "कमला पसंद सिल्वर कोटेड", "Kamla Pasand", "Box of 25 Pouches", 25, 215.0, 250.0, 35.0, 14.0, 1, 1, "High Demand", "kamla_pasand"),
        (1, "pan_masala", "Tansen Blue Premium Pan Masala", "तानसेन ब्लू मसाला डब्बा", "Tansen", "Box of 20 Pouches", 20, 180.0, 200.0, 20.0, 10.0, 2, 1, "Trending", "tansen"),
        (1, "pan_masala", "Rajnigandha Pan Masala (Tin Cans 50g)", "रजनीगंधा टिन कैन (डब्बा)", "Rajnigandha", "Outer of 12 Tins x 50g", 12, 2160.0, 2400.0, 240.0, 10.0, 1, 1, "Premium", "rajnigandha"),
        (1, "pan_masala", "RMD Manikchand Gutkha / Pan Masala", "आरएमडी माणिकचंद मसाला", "RMD", "Box of 30 Pouches", 30, 165.0, 180.0, 15.0, 8.3, 2, 1, "Popular", "rmd"),
        (1, "pan_masala", "Shikhar Pan Masala (Standard Box)", "शिखर पान मसाला डब्बा", "Shikhar", "Box of 30 Pouches", 30, 138.0, 150.0, 12.0, 8.0, 1, 1, "Fast Move", "shikhar"),

        # ZARDA & TOBACCO
        (1, "tobacco", "Baba 120 Zarda Zafrani (Tin 50g)", "बाबा 120 जर्दा जाफरानी", "Baba", "Outer of 10 Tins", 10, 850.0, 1000.0, 150.0, 15.0, 1, 1, "Must Have", "baba"),
        (1, "tobacco", "Miraj Tobacco / Zarda (Pouch Box)", "मिराज तम्बाकू डब्बा", "Miraj", "Box of 50 Pouches", 50, 220.0, 250.0, 30.0, 12.0, 2, 1, "Fast Moving", "miraj"),
        (1, "tobacco", "Chaini Khaini Filter Pack", "चैनी खैनी फ़िल्टर पैक", "Chaini", "Box of 20 Pouches", 20, 170.0, 200.0, 30.0, 15.0, 2, 1, "Hot Choice", "chaini"),
        (1, "tobacco", "Raja Chhap Desi Khaini", "राजा छाप खैनी बंडल", "Raja Chhap", "Bundle of 40 Pouches", 40, 190.0, 240.0, 50.0, 20.8, 1, 1, "High Margin", "khaini"),
        (1, "tobacco", "Kuber Tobacco Premium Zarda", "कुबेर खैनी व जर्दा", "Kuber", "Box of 30 Pouches", 30, 210.0, 240.0, 30.0, 12.5, 2, 1, "Regular", "kuber"),

        # CIGARETTES & BIDI
        (1, "cigarettes", "Gold Flake Super Star (10s Pack Dabba)", "गोल्ड फ्लेक सुपर स्टार डब्बा", "Gold Flake", "Outer Dabba of 10 Packs (100 Sticks)", 10, 1180.0, 1300.0, 120.0, 9.2, 1, 1, "Daily Top Seller", "cigarettes"),
        (1, "cigarettes", "Gold Flake Kings / Lights (20s Pack)", "गोल्ड फ्लेक किंग्स (10 पैकेट)", "Gold Flake", "Outer Dabba of 10 Packs (200 Sticks)", 10, 3100.0, 3400.0, 300.0, 8.8, 1, 1, "Premium", "gold_flake"),
        (1, "cigarettes", "Classic Regular / Milds (20s Pack)", "क्लासिक रेगुलर / माइल्ड्स", "Classic", "Outer Dabba of 10 Packs", 10, 3200.0, 3500.0, 300.0, 8.6, 1, 1, "Top Brand", "classic"),
        (1, "cigarettes", "Marlboro Advance (20s Pack Outer)", "मर्लबोरो एडवांस (आउटर)", "Marlboro", "Outer of 10 Packs (200 Sticks)", 10, 3250.0, 3600.0, 350.0, 9.7, 1, 1, "High Demand", "marlboro"),
        (1, "cigarettes", "Wave Compact Cigarettes (10s Pack)", "वेव कॉम्पैक्ट सिगरेट", "Wave", "Outer Dabba of 10 Packs", 10, 680.0, 800.0, 120.0, 15.0, 2, 1, "Budget Hero", "wave"),
        (1, "cigarettes", "502 Pataka Special Bidi (Bale)", "502 पटाका स्पेशल बीड़ी गड्डी", "Pataka 502", "Bale / Gaddi of 20 Bundles", 20, 480.0, 600.0, 120.0, 20.0, 1, 1, "Bumper Margin", "bidi"),
        (1, "cigarettes", "Chhap 27 Desi Bidi (Carton)", "27 छाप बीड़ी कट्टा", "Chhap 27", "Carton of 50 Bundles", 50, 750.0, 950.0, 200.0, 21.0, 1, 1, "Bulk Seller", "bidi_bundle"),

        # SUPARI & SWEET PAN
        (1, "supari", "Kesar Tukda Supari Grade-A (1 Kg Sack)", "केसर टुकड़ा सुपारी (1 किलो पैक)", "Royal Supari", "1 Kg Sealed Bag", 1, 580.0, 700.0, 120.0, 17.1, 1, 1, "Pure Quality", "supari"),
        (1, "supari", "Chaman Bahar Pan Chutney (Jar)", "चमन बहार पान चटनी", "Chaman Bahar", "Box of 12 Glass Bottles", 12, 420.0, 480.0, 60.0, 12.5, 1, 1, "Sweet Pan Must", "chutney"),
        (1, "supari", "Silver Coated Elaichi Baba Pearls", "बाबा सिल्वर इलाइची पाउच", "Baba", "Box of 30 Sachets", 30, 270.0, 300.0, 30.0, 10.0, 2, 1, "Quick Move", "elaichi"),
        (1, "supari", "Shahi Meetha Masala Dry Mix (500g)", "शाही मीठा पान मसाला ड्राई", "Shahi", "Box of 5 Packs x 100g", 5, 340.0, 450.0, 110.0, 24.4, 1, 1, "Huge Profit", "sweet_pan"),

        # CONFECTIONERY & MINTS
        (1, "confectionery", "Pass Pass Mint Mouth Freshener", "पास पास मिंट माउथ फ्रेशनर", "DS Group", "Jar of 60 Pouches", 60, 240.0, 300.0, 60.0, 20.0, 1, 1, "Counter Top", "pass_pass"),
        (1, "confectionery", "Pulse Candy Kaccha Aam (Big Jar)", "पल्स कच्चा आम कैंडी जार", "Pass Pass Pulse", "Jar of 150 Candies", 150, 115.0, 150.0, 35.0, 23.3, 2, 1, "Kids & Adults", "pulse"),
        (1, "confectionery", "Orbit Spearmint Sugarfree Gum", "ऑर्बिट च्युइंग गम बॉक्स", "Orbit", "Box of 20 Packs", 20, 160.0, 200.0, 40.0, 20.0, 2, 1, "High Margin", "orbit"),
        (1, "confectionery", "Center Fresh Spearmint (Box 30s)", "सेंटर फ्रेश गम बॉक्स", "Center Fresh", "Box of 30 Packs", 30, 120.0, 150.0, 30.0, 20.0, 2, 1, "Everyday", "center_fresh"),

        # ACCESSORIES & PAPERS
        (1, "accessories", "Cricket Gas Flint Lighters (Display Tray)", "क्रिकेट गैस लाइटर (ट्रे)", "Cricket", "Display Tray of 50 Pcs", 50, 420.0, 750.0, 330.0, 44.0, 1, 1, "44% Margin!", "lighter"),
        (1, "accessories", "BIC Maxi Electronic Lighters (Box)", "बिक ओरिजिनल लाइटर बॉक्स", "BIC", "Box of 50 Pcs", 50, 1100.0, 1500.0, 400.0, 26.6, 1, 1, "Imported Quality", "bic"),
        (1, "accessories", "OCB Slim King Size Rolling Papers", "ओसीबी रोलिंग पेपर (बॉक्स)", "OCB", "Box of 50 Booklets", 50, 1250.0, 2500.0, 1250.0, 50.0, 1, 1, "50% Margin!", "rolling_paper"),
        (1, "accessories", "Homelite Matchboxes (Carton Bale)", "होमलाइट माचिस बंडल", "ITC", "Bale of 100 Matchboxes", 100, 140.0, 200.0, 60.0, 30.0, 1, 1, "Essential", "matchbox"),
        (1, "accessories", "Refined Ready Chuna Tubes (No-Mess)", "तैयार चूना ट्यूब (बॉक्स)", "Standard", "Box of 100 Tubes", 100, 180.0, 300.0, 120.0, 40.0, 1, 1, "Super Margin", "chuna")
    ]

    cursor.executemany('''
    INSERT INTO products (wholesaler_id, category_id, name, hindi_name, brand, box_size_desc, units_per_box,
                          wholesale_price, mrp, retailer_margin_amount, retailer_margin_pct, min_boxes, in_stock, badge, image_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', products)

    # Populate Wholesaler 2 & 3 with variation for marketplace comparison
    for p in products[:15]:
        # Wholesaler 2
        w2_price = round(p[7] * 0.99, 1)
        w2_margin = round(p[8] - w2_price, 1)
        w2_pct = round((w2_margin / p[8]) * 100, 1)
        cursor.execute('''
        INSERT INTO products (wholesaler_id, category_id, name, hindi_name, brand, box_size_desc, units_per_box,
                              wholesale_price, mrp, retailer_margin_amount, retailer_margin_pct, min_boxes, in_stock, badge, image_url)
        VALUES (2, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p[1], p[2], p[3], p[4], p[5], p[6], w2_price, p[8], w2_margin, w2_pct, p[11], p[12], p[13], p[14]))

    for p in products[8:22]:
        # Wholesaler 3
        w3_price = round(p[7] * 1.01, 1)
        w3_margin = round(p[8] - w3_price, 1)
        w3_pct = round((w3_margin / p[8]) * 100, 1)
        cursor.execute('''
        INSERT INTO products (wholesaler_id, category_id, name, hindi_name, brand, box_size_desc, units_per_box,
                              wholesale_price, mrp, retailer_margin_amount, retailer_margin_pct, min_boxes, in_stock, badge, image_url)
        VALUES (3, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (p[1], p[2], p[3], p[4], p[5], p[6], w3_price, p[8], w3_margin, w3_pct, p[11], p[12], p[13], p[14]))

    # Retailers (Pan Shops)
    retailers = [
        (1, "Ramesh Pan Bhandar & Cold Drinks", "Ramesh Kumar Sharma", "+91 98111 22334", "Opposite City Cinema, Main Road", "Sadar Bazar", "Kanpur", 4850.0, 25000.0),
        (2, "Jai Balaji Pan Palace", "Sunil Bhai Chaurasia", "+91 97222 33445", "Near Bus Terminal Gate 3", "Station Road", "Ahmedabad", 0.0, 20000.0),
        (3, "Mahalaxmi Pan & Chai Corner", "Pramod Tiwari", "+91 99333 44556", "Plot 12, Gandhi Market Chowk", "APMC Area", "Delhi NCR", 1850.0, 15000.0),
        (4, "Royal Smoke & Pan Studio", "Imran Ali", "+91 98444 55667", "Shop 5, VIP Circle Complex", "Civil Lines", "Lucknow", 8200.0, 30000.0),
        (5, "Shankar Special Banarasi Pan", "Gopal Das", "+91 96555 66778", "Shop 2, Ghat Road", "Old City", "Varanasi", 0.0, 10000.0)
    ]
    cursor.executemany('''
    INSERT INTO retailers (id, shop_name, owner_name, phone, address, area, city, khata_balance, credit_limit)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', retailers)

    # Orders
    sample_orders = [
        (1, "ORD-9401", 1, 1, "Ramesh Pan Bhandar & Cold Drinks", "+91 98111 22334", "Opposite City Cinema, Main Road, Sadar Bazar",
         8, 4850.0, 0, 0, 4850.0, 680.0, "KHATA", "delivered", "Delivered via Chhotu Delivery Boy"),
        (2, "ORD-9402", 1, 2, "Jai Balaji Pan Palace", "+91 97222 33445", "Near Bus Terminal Gate 3, Station Road",
         4, 5780.0, 50, 0, 5730.0, 620.0, "UPI", "confirmed", "Wholesale rate verified, packed in carton"),
        (3, "ORD-9403", 1, 3, "Mahalaxmi Pan & Chai Corner", "+91 99333 44556", "Plot 12, Gandhi Market Chowk",
         12, 6120.0, 0, 0, 6120.0, 840.0, "COD", "pending", "New order placed! Needs dispatch approval.")
    ]
    cursor.executemany('''
    INSERT INTO orders (id, order_code, wholesaler_id, retailer_id, retailer_name, retailer_phone, retailer_address,
                        total_boxes, subtotal, discount, delivery_fee, total_amount, total_profit_estimate, payment_mode, order_status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_orders)

    # Order Items
    cursor.execute('''
    INSERT INTO order_items (order_id, product_id, product_name, brand, box_size_desc, box_qty, price_per_box, mrp_per_box, subtotal, profit_per_box)
    VALUES
    (1, 1, 'Vimal Pan Masala (₹5 Pack)', 'Vimal', 'Box of 30 Pouches', 5, 135.0, 150.0, 675.0, 15.0),
    (1, 13, 'Gold Flake Super Star (10s Pack Dabba)', 'Gold Flake', 'Outer Dabba of 10 Packs', 3, 1180.0, 1300.0, 3540.0, 120.0),
    (1, 28, 'Cricket Gas Flint Lighters (Display Tray)', 'Cricket', 'Display Tray of 50 Pcs', 1, 420.0, 750.0, 420.0, 330.0),
    (2, 2, 'Vimal Pan Masala Master Carton (Pettie)', 'Vimal', 'Pettie of 20 Boxes', 2, 2600.0, 3000.0, 5200.0, 400.0),
    (2, 4, 'Tansen Blue Premium Pan Masala', 'Tansen', 'Box of 20 Pouches', 3, 180.0, 200.0, 540.0, 20.0)
    ''')

    # Khata Ledger
    cursor.execute('''
    INSERT INTO khata_ledger (retailer_id, wholesaler_id, order_id, type, amount, balance_after, notes)
    VALUES
    (1, 1, 1, 'debit', 4850.0, 4850.0, 'Order ORD-9401 taken on 7-Day Udhaar')
    ''')

    conn.commit()

if __name__ == '__main__':
    init_db()
