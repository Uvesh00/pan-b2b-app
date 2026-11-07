#!/usr/bin/env python3
"""
Pan & Tobacco Wholesale B2B Web App - High Performance REST Server
Zero external dependencies, runs directly on Python 3 standard library.
"""
import os
import sys
import json
import sqlite3
import mimetypes
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from database import get_db, init_db, DB_FILE

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

def dict_from_row(row):
    return dict(row) if row else None

class PanB2BRequestHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local dev flexibility
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def read_json_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode('utf-8'))
        except Exception:
            return {}

    def send_json(self, data, status=200):
        response_bytes = json.dumps(data, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def send_error_json(self, message, status=400):
        self.send_json({"error": message, "success": False}, status=status)

    def serve_static(self, filepath):
        if filepath == '/' or not filepath:
            filepath = '/index.html'
        
        # Clean path to prevent directory traversal
        rel_path = filepath.lstrip('/')
        clean_path = os.path.normpath(os.path.join(STATIC_DIR, rel_path))
        if not clean_path.startswith(STATIC_DIR) or not os.path.isfile(clean_path):
            clean_path = os.path.join(STATIC_DIR, 'index.html')

        mime_type, _ = mimetypes.guess_type(clean_path)
        if not mime_type:
            mime_type = 'application/octet-stream'

        try:
            with open(clean_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', f"{mime_type}; charset=utf-8")
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(404, f"File not found: {e}")

    # ROUTING
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # Static assets
        if not path.startswith('/api'):
            self.serve_static(path)
            return

        conn = get_db()
        cursor = conn.cursor()

        try:
            # 1. Config endpoint
            if path == '/api/config':
                cursor.execute("SELECT key, value FROM app_settings")
                settings = dict(cursor.fetchall())
                mode = settings.get('platform_mode', 'white_label')
                active_wid = int(settings.get('active_wholesaler_id', 1))

                cursor.execute("SELECT * FROM wholesalers WHERE id = ?", (active_wid,))
                active_w = dict_from_row(cursor.fetchone())

                self.send_json({
                    "success": True,
                    "platform_mode": mode,
                    "active_wholesaler": active_w,
                    "app_brand_name": settings.get('app_brand_name', 'Ganesh Pan Wholesale')
                })

            # 2. Wholesalers list
            elif path == '/api/wholesalers':
                cursor.execute("SELECT * FROM wholesalers WHERE is_active = 1 ORDER BY rating DESC")
                wholesalers = [dict_from_row(r) for r in cursor.fetchall()]
                self.send_json({"success": True, "wholesalers": wholesalers})

            # 3. Wholesaler details
            elif path.startswith('/api/wholesalers/'):
                wid = path.split('/')[-1]
                cursor.execute("SELECT * FROM wholesalers WHERE id = ?", (wid,))
                w = dict_from_row(cursor.fetchone())
                if not w:
                    self.send_error_json("Wholesaler not found", 404)
                else:
                    self.send_json({"success": True, "wholesaler": w})

            # 4. Categories list with product counts
            elif path == '/api/categories':
                wid = query.get('wholesaler_id', [None])[0]
                if wid:
                    cursor.execute('''
                    SELECT c.*, COUNT(p.id) as product_count 
                    FROM categories c
                    LEFT JOIN products p ON c.id = p.category_id AND p.wholesaler_id = ?
                    GROUP BY c.id ORDER BY c.sort_order ASC
                    ''', (wid,))
                else:
                    cursor.execute('''
                    SELECT c.*, COUNT(p.id) as product_count 
                    FROM categories c
                    LEFT JOIN products p ON c.id = p.category_id
                    GROUP BY c.id ORDER BY c.sort_order ASC
                    ''')
                cats = [dict_from_row(r) for r in cursor.fetchall()]
                self.send_json({"success": True, "categories": cats})

            # 5. Products list
            elif path == '/api/products':
                wid = query.get('wholesaler_id', [None])[0]
                cat_id = query.get('category_id', [None])[0]
                search = query.get('search', [None])[0]

                sql = "SELECT p.*, c.name as category_name, w.name as wholesaler_name FROM products p JOIN categories c ON p.category_id = c.id JOIN wholesalers w ON p.wholesaler_id = w.id WHERE 1=1"
                params = []

                if wid:
                    sql += " AND p.wholesaler_id = ?"
                    params.append(wid)
                if cat_id and cat_id != 'all':
                    sql += " AND p.category_id = ?"
                    params.append(cat_id)
                if search:
                    sql += " AND (p.name LIKE ? OR p.hindi_name LIKE ? OR p.brand LIKE ?)"
                    term = f"%{search}%"
                    params.extend([term, term, term])

                sql += " ORDER BY p.id ASC"
                cursor.execute(sql, params)
                products = [dict_from_row(r) for r in cursor.fetchall()]
                self.send_json({"success": True, "products": products})

            # 6. Retailers list
            elif path == '/api/retailers':
                cursor.execute("SELECT * FROM retailers ORDER BY shop_name ASC")
                retailers = [dict_from_row(r) for r in cursor.fetchall()]
                self.send_json({"success": True, "retailers": retailers})

            # 7. Orders list
            elif path == '/api/orders':
                wid = query.get('wholesaler_id', [None])[0]
                status = query.get('status', [None])[0]

                sql = "SELECT o.*, w.name as wholesaler_name FROM orders o JOIN wholesalers w ON o.wholesaler_id = w.id WHERE 1=1"
                params = []
                if wid:
                    sql += " AND o.wholesaler_id = ?"
                    params.append(wid)
                if status and status != 'all':
                    sql += " AND o.order_status = ?"
                    params.append(status)

                sql += " ORDER BY o.id DESC"
                cursor.execute(sql, params)
                orders = []
                for row in cursor.fetchall():
                    od = dict_from_row(row)
                    # fetch items
                    cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (od['id'],))
                    od['items'] = [dict_from_row(i) for i in cursor.fetchall()]
                    orders.append(od)

                self.send_json({"success": True, "orders": orders})

            # 8. Single order
            elif path.startswith('/api/orders/'):
                order_id = path.split('/')[-1]
                cursor.execute("SELECT o.*, w.name as wholesaler_name, w.phone as wholesaler_phone, w.whatsapp as wholesaler_whatsapp, w.upi_id FROM orders o JOIN wholesalers w ON o.wholesaler_id = w.id WHERE o.id = ? OR o.order_code = ?", (order_id, order_id))
                od = dict_from_row(cursor.fetchone())
                if not od:
                    self.send_error_json("Order not found", 404)
                else:
                    cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (od['id'],))
                    od['items'] = [dict_from_row(i) for i in cursor.fetchall()]
                    self.send_json({"success": True, "order": od})

            # 9. Wholesaler Dashboard Stats
            elif path == '/api/stats':
                wid = query.get('wholesaler_id', ['1'])[0]
                cursor.execute("SELECT COUNT(*) as total_orders, COALESCE(SUM(total_amount), 0) as total_sales, COALESCE(SUM(total_profit_estimate), 0) as total_profit FROM orders WHERE wholesaler_id = ?", (wid,))
                order_stats = dict_from_row(cursor.fetchone())

                cursor.execute("SELECT COUNT(*) as pending_orders FROM orders WHERE wholesaler_id = ? AND order_status = 'pending'", (wid,))
                pending = cursor.fetchone()[0]

                cursor.execute("SELECT COALESCE(SUM(khata_balance), 0) as total_khata_due FROM retailers")
                khata_due = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM products WHERE wholesaler_id = ?", (wid,))
                total_products = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM retailers")
                total_retailers = cursor.fetchone()[0]

                self.send_json({
                    "success": True,
                    "stats": {
                        "total_orders": order_stats['total_orders'],
                        "total_sales": order_stats['total_sales'],
                        "total_profit": order_stats['total_profit'],
                        "pending_orders": pending,
                        "total_khata_due": khata_due,
                        "total_products": total_products,
                        "total_retailers": total_retailers
                    }
                })

            else:
                self.send_error_json("Endpoint not found", 404)

        except Exception as e:
            self.send_error_json(str(e), 500)
        finally:
            conn.close()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        conn = get_db()
        cursor = conn.cursor()

        try:
            # 1. Update config (toggle white_label vs marketplace, change active wholesaler)
            if path == '/api/config':
                if 'platform_mode' in body:
                    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('platform_mode', ?)", (body['platform_mode'],))
                if 'active_wholesaler_id' in body:
                    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('active_wholesaler_id', ?)", (str(body['active_wholesaler_id']),))
                if 'app_brand_name' in body:
                    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('app_brand_name', ?)", (body['app_brand_name'],))
                conn.commit()
                self.send_json({"success": True, "message": "Settings updated"})

            # 2. Place New Order
            elif path == '/api/orders':
                items = body.get('items', [])
                if not items:
                    self.send_error_json("Cart is empty")
                    return

                wholesaler_id = body.get('wholesaler_id', 1)
                retailer_id = body.get('retailer_id')
                retailer_name = body.get('retailer_name', 'Customer Pan Shop')
                retailer_phone = body.get('retailer_phone', '')
                retailer_address = body.get('retailer_address', '')
                payment_mode = body.get('payment_mode', 'COD') # COD, UPI, KHATA
                notes = body.get('notes', '')

                # Fetch wholesaler details
                cursor.execute("SELECT * FROM wholesalers WHERE id = ?", (wholesaler_id,))
                wholesaler = dict_from_row(cursor.fetchone())
                if not wholesaler:
                    self.send_error_json("Wholesaler not found")
                    return

                # Calculate totals
                subtotal = 0.0
                total_boxes = 0
                total_profit = 0.0
                order_items_to_insert = []

                for it in items:
                    pid = it.get('product_id')
                    cursor.execute("SELECT * FROM products WHERE id = ?", (pid,))
                    p = dict_from_row(cursor.fetchone())
                    if not p:
                        continue
                    
                    qty = int(it.get('box_qty', 1))
                    price = float(p['wholesale_price'])
                    mrp = float(p['mrp'])
                    profit_per_box = mrp - price
                    line_subtotal = price * qty

                    total_boxes += qty
                    subtotal += line_subtotal
                    total_profit += (profit_per_box * qty)

                    order_items_to_insert.append({
                        "product_id": p['id'],
                        "product_name": p['name'],
                        "brand": p['brand'],
                        "box_size_desc": p['box_size_desc'],
                        "box_qty": qty,
                        "price_per_box": price,
                        "mrp_per_box": mrp,
                        "subtotal": line_subtotal,
                        "profit_per_box": profit_per_box
                    })

                delivery_fee = 0 if subtotal >= wholesaler['free_delivery_above'] else wholesaler['delivery_charges']
                discount = float(body.get('discount', 0))
                total_amount = round(subtotal + delivery_fee - discount, 2)

                # Generate unique order code ORD-XXXX
                cursor.execute("SELECT MAX(id) FROM orders")
                max_id = cursor.fetchone()[0] or 0
                new_id = max_id + 1
                order_code = f"ORD-{9400 + new_id}"

                # Insert Order
                cursor.execute('''
                INSERT INTO orders (order_code, wholesaler_id, retailer_id, retailer_name, retailer_phone,
                                    retailer_address, total_boxes, subtotal, discount, delivery_fee,
                                    total_amount, total_profit_estimate, payment_mode, order_status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                ''', (order_code, wholesaler_id, retailer_id, retailer_name, retailer_phone,
                      retailer_address, total_boxes, subtotal, discount, delivery_fee,
                      total_amount, total_profit, payment_mode, notes))

                order_db_id = cursor.lastrowid

                # Insert Order Items
                for o_item in order_items_to_insert:
                    cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, product_name, brand, box_size_desc,
                                            box_qty, price_per_box, mrp_per_box, subtotal, profit_per_box)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (order_db_id, o_item['product_id'], o_item['product_name'], o_item['brand'],
                          o_item['box_size_desc'], o_item['box_qty'], o_item['price_per_box'],
                          o_item['mrp_per_box'], o_item['subtotal'], o_item['profit_per_box']))

                # If Khata (Udhaar/Credit) payment, update retailer ledger & balance
                if payment_mode == 'KHATA' and retailer_id:
                    cursor.execute("SELECT khata_balance FROM retailers WHERE id = ?", (retailer_id,))
                    curr_bal = cursor.fetchone()
                    new_bal = (curr_bal[0] if curr_bal else 0) + total_amount
                    cursor.execute("UPDATE retailers SET khata_balance = ? WHERE id = ?", (new_bal, retailer_id))
                    cursor.execute('''
                    INSERT INTO khata_ledger (retailer_id, wholesaler_id, order_id, type, amount, balance_after, notes)
                    VALUES (?, ?, ?, 'debit', ?, ?, ?)
                    ''', (retailer_id, wholesaler_id, order_db_id, total_amount, new_bal, f"Order {order_code} added to Khata"))

                conn.commit()

                # Build formatted WhatsApp order message
                items_summary = "\n".join([f"📦 {it['product_name']} - {it['box_qty']} Box @ ₹{it['price_per_box']}" for it in order_items_to_insert])
                wa_msg = (
                    f"🛒 *Naya Wholesale Order: {order_code}*\n"
                    f"🏪 *Dukan:* {retailer_name}\n"
                    f"📞 *Phone:* {retailer_phone}\n"
                    f"📍 *Pata:* {retailer_address}\n"
                    f"------------------------\n"
                    f"*Items Ordered:*\n{items_summary}\n"
                    f"------------------------\n"
                    f"📦 *Total Boxes:* {total_boxes}\n"
                    f"💰 *Total Amount:* ₹{total_amount:.2f}\n"
                    f"💳 *Payment Mode:* {payment_mode}\n"
                    f"🚚 *Estimated Delivery:* {wholesaler['delivery_time']}\n\n"
                    f"Kripya order pack karke dispatch karein! 🙏"
                )
                wa_phone = wholesaler['whatsapp'].replace('+', '').replace(' ', '')
                wa_url = f"https://api.whatsapp.com/send?phone={wa_phone}&text={urllib.parse.quote(wa_msg)}"

                self.send_json({
                    "success": True,
                    "order_id": order_db_id,
                    "order_code": order_code,
                    "total_amount": total_amount,
                    "total_boxes": total_boxes,
                    "whatsapp_url": wa_url,
                    "message": "Order placed successfully!"
                })

            # 3. Add New Product
            elif path == '/api/products':
                wid = body.get('wholesaler_id', 1)
                name = body.get('name')
                hindi_name = body.get('hindi_name', '')
                brand = body.get('brand', '')
                cat_id = body.get('category_id', 'pan_masala')
                box_desc = body.get('box_size_desc', 'Box')
                units = int(body.get('units_per_box', 1))
                price = float(body.get('wholesale_price', 0))
                mrp = float(body.get('mrp', price))
                min_boxes = int(body.get('min_boxes', 1))
                margin_amount = mrp - price
                margin_pct = round((margin_amount / mrp * 100), 1) if mrp > 0 else 0

                cursor.execute('''
                INSERT INTO products (wholesaler_id, category_id, name, hindi_name, brand, box_size_desc,
                                      units_per_box, wholesale_price, mrp, retailer_margin_amount,
                                      retailer_margin_pct, min_boxes, in_stock, badge, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, 'custom')
                ''', (wid, cat_id, name, hindi_name, brand, box_desc, units, price, mrp,
                      margin_amount, margin_pct, min_boxes, body.get('badge', 'New Arrival')))

                new_pid = cursor.lastrowid
                conn.commit()
                self.send_json({"success": True, "product_id": new_pid, "message": "Product added"})

            # 4. Add/Register Retailer
            elif path == '/api/retailers':
                shop_name = body.get('shop_name')
                owner_name = body.get('owner_name')
                phone = body.get('phone')
                address = body.get('address', '')
                area = body.get('area', '')
                city = body.get('city', '')

                cursor.execute('''
                INSERT INTO retailers (shop_name, owner_name, phone, address, area, city)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (shop_name, owner_name, phone, address, area, city))
                rid = cursor.lastrowid
                conn.commit()
                self.send_json({"success": True, "retailer_id": rid, "message": "Retailer registered"})

            # 5. Khata Payment Settlement
            elif path == '/api/khata/payment':
                rid = body.get('retailer_id')
                amount = float(body.get('amount', 0))
                notes = body.get('notes', 'Khata Payment Received')

                cursor.execute("SELECT khata_balance FROM retailers WHERE id = ?", (rid,))
                row = cursor.fetchone()
                if not row:
                    self.send_error_json("Retailer not found")
                    return

                old_bal = row[0]
                new_bal = max(0.0, old_bal - amount)
                cursor.execute("UPDATE retailers SET khata_balance = ? WHERE id = ?", (new_bal, rid))
                cursor.execute('''
                INSERT INTO khata_ledger (retailer_id, wholesaler_id, order_id, type, amount, balance_after, notes)
                VALUES (?, 1, NULL, 'credit', ?, ?, ?)
                ''', (rid, amount, new_bal, notes))
                conn.commit()
                self.send_json({"success": True, "new_balance": new_bal, "message": "Payment recorded successfully"})

            else:
                self.send_error_json("Endpoint not found", 404)

        except Exception as e:
            self.send_error_json(str(e), 500)
        finally:
            conn.close()

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        conn = get_db()
        cursor = conn.cursor()

        try:
            # 1. Update Wholesaler Profile / White-label branding
            if path.startswith('/api/wholesalers/'):
                wid = path.split('/')[-1]
                fields = []
                params = []
                updatable = ['name', 'tagline', 'owner_name', 'phone', 'whatsapp', 'upi_id', 'address',
                             'city', 'min_order_amount', 'delivery_time', 'theme_color', 'logo_icon', 'free_delivery_above']
                for key in updatable:
                    if key in body:
                        fields.append(f"{key} = ?")
                        params.append(body[key])

                if fields:
                    params.append(wid)
                    cursor.execute(f"UPDATE wholesalers SET {', '.join(fields)} WHERE id = ?", params)
                    conn.commit()
                self.send_json({"success": True, "message": "Wholesaler details updated"})

            # 2. Update Order Status
            elif '/status' in path and path.startswith('/api/orders/'):
                # /api/orders/:id/status
                order_id = path.split('/')[3]
                new_status = body.get('status')
                valid = ['pending', 'confirmed', 'out_for_delivery', 'delivered', 'cancelled']
                if new_status not in valid:
                    self.send_error_json("Invalid status")
                    return

                cursor.execute("UPDATE orders SET order_status = ? WHERE id = ?", (new_status, order_id))
                conn.commit()
                self.send_json({"success": True, "message": f"Order status updated to {new_status}"})

            # 3. Update Product (Price, Stock, Margin)
            elif path.startswith('/api/products/'):
                pid = path.split('/')[-1]
                fields = []
                params = []
                for key in ['wholesale_price', 'mrp', 'in_stock', 'name', 'hindi_name', 'box_size_desc']:
                    if key in body:
                        fields.append(f"{key} = ?")
                        params.append(body[key])

                # Recalculate margin if prices updated
                if 'wholesale_price' in body or 'mrp' in body:
                    cursor.execute("SELECT wholesale_price, mrp FROM products WHERE id = ?", (pid,))
                    cur = cursor.fetchone()
                    price = float(body.get('wholesale_price', cur[0]))
                    mrp = float(body.get('mrp', cur[1]))
                    margin = mrp - price
                    margin_pct = round((margin / mrp * 100), 1) if mrp > 0 else 0
                    fields.extend(["retailer_margin_amount = ?", "retailer_margin_pct = ?"])
                    params.extend([margin, margin_pct])

                if fields:
                    params.append(pid)
                    cursor.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", params)
                    conn.commit()
                self.send_json({"success": True, "message": "Product updated"})

            else:
                self.send_error_json("Endpoint not found", 404)

        except Exception as e:
            self.send_error_json(str(e), 500)
        finally:
            conn.close()

def run_server(port=8080):
    init_db()
    os.makedirs(STATIC_DIR, exist_ok=True)
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, PanB2BRequestHandler)
    print(f"============================================================")
    print(f" Pan & Tobacco B2B Wholesale Web App Running on http://localhost:{port}")
    print(f" Database: {DB_FILE}")
    print(f" Static Dir: {STATIC_DIR}")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
