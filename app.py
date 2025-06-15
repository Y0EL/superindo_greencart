import streamlit as st
from PIL import Image
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import textwrap
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random
from datetime import datetime, timedelta
from reportlab.lib.utils import ImageReader
import zipfile

pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
pdfmetrics.registerFont(TTFont('MSGothic', 'msgothic.ttc'))
pdfmetrics.registerFont(TTFont('Calibri-Bold', 'calibrib.ttf'))

CASHIERS = ["Raymond", "Sofi", "Derren", "Jack", "Jackuavis", "Septian", "Joel", "Dgueby", "Gerald", "Sintia", "Chia", "Defi"]

# 60% Buah dan Sayuran
FRUITS_VEGETABLES = [
    "Apel Fuji Premium", "Apel Red Delicious", "Apel Malang", "Apel Granny Smith", 
    "Pisang Ambon", "Pisang Raja", "Pisang Kepok", "Pisang Sunpride",
    "Jeruk Mandarin", "Jeruk Sunkist", "Jeruk Pontianak", "Jeruk Nipis",
    "Semangka Merah", "Semangka Baby", "Semangka Kuning", "Melon Honeydew",
    "Melon Golden", "Melon Rock", "Anggur Red Globe", "Anggur Thompson",
    "Wortel Lokal", "Wortel Import Baby", "Brokoli Premium", "Brokoli Baby",
    "Kentang Dieng", "Kentang Granola", "Tomat Cherry", "Tomat Beef",
    "Cabai Keriting Merah", "Cabai Rawit Hijau", "Cabai Merah Besar",
    "Bawang Bombay", "Bawang Merah Brebes", "Bawang Putih Kating",
    "Bayam Hijau Organik", "Kangkung Hidroponik", "Selada Romaine",
    "Selada Keriting", "Sawi Putih", "Sawi Hijau", "Pakcoy Premium",
    "Daun Singkong", "Daun Pepaya", "Kemangi Segar", "Nanas Madu",
    "Mangga Harum Manis", "Pepaya California", "Salak Pondoh", "Jambu Air",
    "Timun Suri", "Labu Siam", "Terong Ungu", "Kacang Panjang"
]

# 20% Minuman dalam kemasan
BEVERAGES = [
    "AQUA Botol 330ml", "AQUA Botol 600ml", "AQUA Botol 1.5L",
    "AQUA Galon 19L", "AQUVIVA Botol 330ml", "AQUVIVA Botol 600ml",
    "AQUVIVA Botol 1L", "AQUVIVA Galon 19L", "LeMinerale Botol 330ml",
    "LeMinerale Botol 600ml", "LeMinerale Botol 1L", "LeMinerale Galon 19L",
    "OASIS Botol 330ml", "OASIS Botol 600ml", "OASIS Botol 1L",
    "OASIS Galon 19L", "AQUA Kemasan Gelas 240ml", "AQUVIVA Kemasan Gelas 240ml",
    "LeMinerale Kemasan Gelas 240ml", "OASIS Kemasan Gelas 240ml"
]

# 20% Produk non-buah dan non-sayur
OTHER_PRODUCTS = [
    "Beras Premium 5kg", "Beras Pandan Wangi 5kg", "Minyak Goreng Tropical 1L",
    "Minyak Goreng Filma 2L", "Gula Pasir Gulaku 1kg", "Garam Kapal Api 500g",
    "Telur Ayam Kampung 1kg", "Telur Ayam Negeri 1kg", "Susu UHT Indomilk 1L",
    "Susu UHT Ultra Milk 1L", "Roti Tawar Sari Roti", "Roti Gandum Sari Roti",
    "Mie Instan Indomie Goreng", "Mie Instan Sedaap", "Kopi Kapal Api 165g",
    "Teh Celup Sariwangi 25pcs", "Detergen Rinso 800g", "Sabun Mandi Lifebuoy",
    "Pasta Gigi Pepsodent", "Shampoo Pantene 170ml", "Tissue Paseo 250sheet",
    "Sabun Cuci Piring Sunlight", "Kecap Manis ABC 620ml", "Saos Sambal ABC 340ml"
]

def get_weighted_items():
    """Menggabungkan semua kategori produk dengan proporsi yang ditentukan"""
    all_items = []
    
    # 60% buah dan sayuran
    fruits_vegetables_count = int(len(FRUITS_VEGETABLES) * 0.6)
    all_items.extend(FRUITS_VEGETABLES[:fruits_vegetables_count])
    
    # 20% minuman
    beverages_count = int(len(BEVERAGES) * 1.0)  # Ambil semua minuman
    all_items.extend(BEVERAGES[:beverages_count])
    
    # 20% produk lainnya
    other_products_count = int(len(OTHER_PRODUCTS) * 1.0)  # Ambil semua produk lainnya
    all_items.extend(OTHER_PRODUCTS[:other_products_count])
    
    return all_items

ITEMS = get_weighted_items()

def get_item_price(item_name):
    """Menentukan harga berdasarkan kategori produk"""
    if any(beverage in item_name for beverage in ["AQUA", "AQUVIVA", "LeMinerale", "OASIS"]):
        if "Galon 19L" in item_name:
            return random.randint(15000, 25000)
        elif "1.5L" in item_name or "1L" in item_name:
            return random.randint(3000, 6000)
        elif "600ml" in item_name:
            return random.randint(2000, 4000)
        elif "330ml" in item_name or "240ml" in item_name:
            return random.randint(1500, 3000)
    elif any(product in item_name for product in ["Beras", "Minyak", "Susu", "Detergen"]):
        return random.randint(8000, 35000)
    elif "Premium" in item_name:
        return random.randint(3500, 12900)
    else:
        return random.randint(1500, 8900)

def generate_random_date():
    days_ago = random.randint(0, 7)
    random_date = datetime.now() - timedelta(days=days_ago)
    random_time = datetime.strptime(f"{random.randint(8, 21)}:{random.randint(0, 59)}:{random.randint(0, 59)}", "%H:%M:%S").time()
    return random_date.strftime("%y-%m-%d") + f" ({random_time.strftime('%H:%M:%S')})"

def apply_discount(items):
    discounted_items = []
    for item in items:
        if random.random() < 0.2:
            discount_percentage = random.choice([10, 15, 20, 25])
            original_price = item['price']
            discounted_price = round(original_price * (1 - discount_percentage/100))
            savings = original_price - discounted_price
            discounted_items.append({
                **item,
                'price': discounted_price,
                'hemat': savings,
                'original_price': original_price
            })
        else:
            discounted_items.append({**item, 'hemat': 0})
    return discounted_items

def create_receipt(store_name, items, total, payment_method, receipt_date, logo_path, use_bold=False, cashier_name=None):
    buffer = io.BytesIO()
    width, height = 45 * mm, 210 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))

    font = "Calibri-Bold" if use_bold else "Calibri"

    left_indent = 2 * mm
    x = left_indent
    y = height - 5 * mm

    logo = ImageReader(logo_path)
    logo_width = 10 * mm
    logo_height = 10 * mm
    c.drawImage(logo, x, y - logo_height, width=logo_width, height=logo_height)

    text_start = x + logo_width + 2 * mm

    c.setFont(font, 8)
    c.drawString(text_start, y, store_name)
    y -= 3*mm
    c.drawString(text_start, y, "NPWP: 00.178.137.2-604.000")
    y -= 3*mm
    c.drawString(text_start, y, "Tanggal Pengukuhan: 06-06-97")
    y -= 3*mm
    c.drawString(text_start, y, "MUARA KARANG RAYA NO. 2")
    y -= 3*mm
    c.drawString(text_start, y, "JAKARTA UTARA")
    y -= 3*mm
    c.drawString(text_start, y, "Telp: 6697927")
    y -= 8*mm

    c.setFont(font, 8)
    c.drawString(x, y, f"{receipt_date} No: {random.randint(1000, 9999)}")
    if cashier_name:
        c.drawString(x, y - 3*mm, f"Kasir: {cashier_name}")
        y -= 3*mm
    y -= 1*mm

    separator = '=' * int((width - 2*x) / c.stringWidth('=', font, 8))
    y -= 2*mm

    c.setFont("MSGothic", 8)
    c.drawString(x, y, "DESKRIPSI        QTY    HARGA")
    y -= 3*mm
    c.drawString(x, y, separator)
    y -= 3*mm

    for item in items:
        name = item['name'][:15]
        quantity = item['quantity']
        price = item['price']
        item_total = price * quantity
        
        item_text = f"{name:<15} {quantity:>3} {item_total:>8,.0f}"
        c.drawString(x, y, item_text)
        y -= 3*mm
        
        if item.get('hemat', 0) > 0:
            original_price = item.get('original_price', price)
            hemat_text = f"HEMAT: {item['hemat']:,.0f}"
            c.setFillColorRGB(1, 0, 0)
            c.drawString(x + 2*mm, y, hemat_text)
            c.setFillColorRGB(0, 0, 0)
            y -= 3*mm

    y -= 1*mm
    c.drawString(x, y, separator)
    y -= 3*mm

    ppn = total * 0.11
    total_with_ppn = total + ppn

    c.drawString(x, y, f"Sub Total: {total:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"PPN (11%): {ppn:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"Total (Termasuk PPN): {total_with_ppn:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"Pembayaran - {payment_method}: {total_with_ppn:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"Nomor: B{random.randint(100000000, 999999999)}")
    y -= 4*mm

    c.drawString(x, y, f"Total Item: {len(items)}")
    y -= 4*mm

    c.setFont(font, 8)
    footer_lines = [
        "**Terima kasih**",
        "SARAN ANDA KEPUASAN KAMI",
        "TELP BEBAS PULSA: 0800 1403 210",
        "WHATSAPP: 081213137035 (CALL ONLY)",
        "SENIN - JUMAT 08:00 - 17:00 WIB",
        "Email: cs@superindo.co.id",
        "www.superindo.co.id"
    ]

    for line in footer_lines:
        text_width = c.stringWidth(line, font, 8)
        c.drawString((width - text_width) / 2, y, line)
        y -= 3*mm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_random_items():
    num_items = random.randint(19, 22)
    items = []
    
    # Memastikan proporsi kategori dalam setiap struk
    fruits_veg_count = int(num_items * 0.6)  # 60%
    beverages_count = max(1, int(num_items * 0.2))  # 20%, minimal 1
    others_count = num_items - fruits_veg_count - beverages_count  # sisanya
    
    selected_items = []
    
    # Ambil items sesuai proporsi
    if fruits_veg_count > 0:
        selected_items.extend(random.sample(FRUITS_VEGETABLES, min(fruits_veg_count, len(FRUITS_VEGETABLES))))
    if beverages_count > 0:
        selected_items.extend(random.sample(BEVERAGES, min(beverages_count, len(BEVERAGES))))
    if others_count > 0:
        selected_items.extend(random.sample(OTHER_PRODUCTS, min(others_count, len(OTHER_PRODUCTS))))
    
    for item in selected_items:
        quantity = random.randint(1, 5)
        price = get_item_price(item)
        
        items.append({
            "name": item,
            "quantity": quantity,
            "price": price
        })

    return apply_discount(items)

def generate_random_receipts(num_receipts, store_name, logo_path, use_bold):
    receipts = []
    for _ in range(num_receipts):
        items = generate_random_items()
        receipt_date = generate_random_date()
        cashier = random.choice(CASHIERS)
        subtotal = sum(item['quantity'] * item['price'] for item in items)
        payment_method = random.choice(["BNI QRIS", "MANDIRI", "BCA", "OVO", "GOPAY", "CASH"])
        
        pdf_buffer = create_receipt(
            store_name,
            items,
            subtotal,
            payment_method,
            receipt_date,
            logo_path,
            use_bold,
            cashier
        )
        
        receipts.append({
            'buffer': pdf_buffer,
            'date': receipt_date,
            'cashier': cashier,
            'items': items,
            'total': subtotal + (subtotal * 0.11),
            'payment_method': payment_method
        })

    return receipts

def create_zip_file(receipts):
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for i, receipt in enumerate(receipts):
            timestamp = receipt['date'].replace('/', '').replace(':', '').replace(' ', '_').replace('(', '').replace(')', '')
            filename = f"receipt_{timestamp}_cashier_{receipt['cashier']}.pdf"
            zip_file.writestr(filename, receipt['buffer'].getvalue())
        
        summary = "Receipts Summary:\n\n"
        for i, receipt in enumerate(receipts, 1):
            summary += f"Receipt {i}:\n"
            summary += f"Date: {receipt['date']}\n"
            summary += f"Cashier: {receipt['cashier']}\n"
            summary += f"Payment Method: {receipt['payment_method']}\n"
            summary += f"Total: Rp {receipt['total']:,.2f}\n"
            summary += f"Items: {len(receipt['items'])}\n\n"
        
        zip_file.writestr("summary.txt", summary)

    zip_buffer.seek(0)
    return zip_buffer

st.title("收据生成器")

mode = st.radio("选择模式", ["手动", "自动"])
use_bold = st.checkbox("使用粗体文本", value=True)
store_name = st.text_input("商店名称:", "PT LION SUPERINDO")
uploaded_logo = st.file_uploader("上传您的商店标志", type=["png", "jpg", "jpeg"])
if uploaded_logo is not None:
    logo_path = "temp_logo.png"
    with open(logo_path, "wb") as f:
        f.write(uploaded_logo.getbuffer())
else:
    logo_path = "default_logo.png"

if 'items' not in st.session_state:
    st.session_state['items'] = []
if 'cashier' not in st.session_state:
    st.session_state['cashier'] = random.choice(CASHIERS)

# Tampilkan informasi kategori produk
st.sidebar.header("Kategori Produk")
st.sidebar.write(f"🥬 Buah & Sayuran: {len(FRUITS_VEGETABLES)} items")
st.sidebar.write(f"🥤 Minuman: {len(BEVERAGES)} items")
st.sidebar.write(f"🛍️ Produk Lainnya: {len(OTHER_PRODUCTS)} items")
st.sidebar.write(f"📊 Total Produk: {len(ITEMS)} items")

if mode == "手动":
    st.subheader("设置购物商品")
    num_items = st.number_input("商品数量:", min_value=1, value=5, step=1)

    if st.button("生成商品"):
        st.session_state['items'] = []
        
        # Menentukan proporsi untuk mode manual
        fruits_veg_count = int(num_items * 0.6)
        beverages_count = max(1, int(num_items * 0.2))
        others_count = num_items - fruits_veg_count - beverages_count
        
        selected_items = []
        
        if fruits_veg_count > 0:
            selected_items.extend(random.sample(FRUITS_VEGETABLES, min(fruits_veg_count, len(FRUITS_VEGETABLES))))
        if beverages_count > 0:
            selected_items.extend(random.sample(BEVERAGES, min(beverages_count, len(BEVERAGES))))
        if others_count > 0:
            selected_items.extend(random.sample(OTHER_PRODUCTS, min(others_count, len(OTHER_PRODUCTS))))
        
        for item in selected_items:
            quantity = random.randint(1, 5)
            price = get_item_price(item)
            
            st.session_state['items'].append({
                "name": item,
                "quantity": quantity,
                "price": price
            })
        
        st.session_state['items'] = apply_discount(st.session_state['items'])

    if st.session_state['items']:
        st.write("商品列表:")
        for item in st.session_state['items']:
            if item.get('hemat', 0) > 0:
                st.write(f"{item['name']} - Jumlah: {item['quantity']} - "
                         f"Harga: Rp {item['price']:,} "
                         f"(HEMAT: Rp {item['hemat']:,})")
            else:
                st.write(f"{item['name']} - Jumlah: {item['quantity']} - "
                         f"Harga: Rp {item['price']:,}")

    use_current_date = st.checkbox("使用当前日期和时间", value=False)
    if use_current_date:
        receipt_date = datetime.now().strftime("%y-%m-%d (%H:%M:%S)")
        st.write(f"选定日期: {receipt_date}")
    else:
        receipt_date = generate_random_date()
        st.write(f"随机生成的日期: {receipt_date}")

    if st.session_state['items']:
        subtotal = sum(item['quantity'] * item['price'] for item in st.session_state['items'])
        ppn = subtotal * 0.11
        total = subtotal + ppn

        st.write(f"小计: Rp {subtotal:,.2f}")
        st.write(f"PPN (11%): Rp {ppn:,.2f}")
        st.write(f"总计: Rp {total:,.2f}")

        payment_methods = ["BNI QRIS", "MANDIRI", "BCA", "OVO", "GOPAY", "CASH"]
        payment_method = st.selectbox("支付方式:", payment_methods)

        if st.button("生成收据"):
            pdf_buffer = create_receipt(
                store_name,
                st.session_state['items'],
                subtotal,
                payment_method,
                receipt_date,
                logo_path,
                use_bold,
                st.session_state['cashier']
            )

            st.download_button(
                label="下载收据 PDF",
                data=pdf_buffer,
                file_name=f"receipt_{receipt_date.replace('/', '').replace(':', '').replace(' ', '_').replace('(', '').replace(')', '')}.pdf",
                mime="application/pdf"
            )

elif mode == "自动":
    st.subheader("生成多个收据")

    num_receipts = st.number_input("要生成的收据数量:", min_value=1, max_value=50, value=5)

    if st.button("生成收据"):
        receipts = generate_random_receipts(num_receipts, store_name, logo_path, use_bold)
        
        zip_buffer = create_zip_file(receipts)
        
        st.download_button(
            label="下载所有收据 (ZIP)",
            data=zip_buffer,
            file_name="superindo_receipts.zip",
            mime="application/zip"
        )

        st.subheader("收据摘要:")
        total_sales = 0
        for i, receipt in enumerate(receipts, 1):
            st.write(f"收据 {i}:")
            st.write(f"日期: {receipt['date']}")
            st.write(f"收银员: {receipt['cashier']}")
            st.write(f"支付方式: {receipt['payment_method']}")
            st.write(f"总计: Rp {receipt['total']:,.2f}")
            st.write(f"商品数量: {len(receipt['items'])}")
            st.write("---")
            total_sales += receipt['total']
        
        st.write(f"总销售额: Rp {total_sales:,.2f}")
        st.write(f"每张收据平均: Rp {(total_sales/num_receipts):,.2f}")

st.markdown("---")
st.markdown("### 关于应用")
st.write("此应用程序用于生成 Superindo 购物收据。")
st.write("选择手动模式以设置收据详细信息，或选择自动模式以一次生成多个收据。")
st.write("产品分类:")
st.write("• 60% 水果和蔬菜")
st.write("• 20% 饮用水 (AQUA, AQUVIVA, LeMinerale, OASIS)")
st.write("• 20% 其他产品 (米、油、牛奶、洗涤剂等)")
st.write("© 2024 收据生成器")
