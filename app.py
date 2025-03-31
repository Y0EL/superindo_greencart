import streamlit as st
from PIL import Image
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import textwrap
import random
from datetime import datetime, timedelta
from reportlab.lib.utils import ImageReader
import zipfile
import os

# Using built-in fonts
REGULAR_FONT = 'Helvetica'
BOLD_FONT = 'Helvetica-Bold'
MONO_FONT = 'Courier'

CASHIERS = ["Raymond", "Sofi", "Derren", "Jack", "Jackuavis", "Septian", "Joel", "Dgueby", "Gerald", "Sintia", "Chia", "Defi"]

ITEMS = [
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
    "Daun Singkong", "Daun Pepaya", "Kemangi Segar"
]



def generate_random_date():
    days_ago = random.randint(0, 7)
    random_date = datetime.now() - timedelta(days=days_ago)
    random_time = datetime.strptime(f"{random.randint(8, 21)}:{random.randint(0, 59)}:{random.randint(0, 59)}", "%H:%M:%S").time()
    return random_date.strftime("%y-%m-%d") + f" ({random_time.strftime('%H:%M:%S')})"

def apply_discount(items):
    discounted_items = []
    for item in items:
        if random.random() < 0.6:
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

def create_receipt(store_name, items, subtotal, payment_method, receipt_date, logo_path, use_bold, cashier):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(80*mm, 297*mm))
    
    # Set transparency for header company info
    c.saveState()
    c.setFillAlpha(0.5)
    c.setFont(REGULAR_FONT, 7)
    
    # Header with minimal spacing
    y = 280
    spacing = 3
    c.drawString(5*mm, y*mm, "PT INDOMARCO PRISMATAMA")
    y -= spacing
    c.drawString(5*mm, y*mm, "GEDUNG MENARA INDOMARET")
    y -= spacing
    c.drawString(5*mm, y*mm, "BOULEVARD PANTAI INDAH KAPUK")
    y -= spacing
    c.drawString(5*mm, y*mm, "JAKARTA UTARA")
    y -= spacing
    c.drawString(5*mm, y*mm, "NPWP: 001 387 994 6-092 000")
    c.restoreState()
    
    # Draw logo on the right side
    y = 280
    spacing = 3
    logo = ImageReader(logo_path)
    c.drawImage(logo, 53*mm, 271*mm, width=24*mm, height=12*mm)
 

    # Store info (without spacing)
    c.setFont(MONO_FONT, 9)
    y = 260
    store_text = "FRESH BOUTIQUE PIK"
    text_width = c.stringWidth(store_text, MONO_FONT, 9)
    x = (80*mm - text_width) / 2
    c.drawString(x, y*mm, store_text)
    
    y -= spacing
    c.drawString(5*mm, y*mm, "JL. PANTAI MAJU BERSAMA KAMAL MUARA")
    y -= spacing
    c.drawString(5*mm, y*mm, "PENJARINGAN JAKARTA UTARA, 14470")
    
    # Separator
    c.setFont(MONO_FONT, 8)
    y -= spacing
    c.drawString(5*mm, y*mm, "-" * 42)
    
    # Transaction info with random components
    random_digit1 = random.randint(0, 9)
    random_digit2 = random.randint(0, 9)
    random_alphanum = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
    random_5digits = ''.join(random.choices('0123456789', k=5))
    random_2digits = ''.join(random.choices('0123456789', k=2))
    
    current_datetime = datetime.now()
    transaction_info = (
        f"{current_datetime.strftime('%d/%m/%Y %H:%M')} "
        f"{random_digit1}/{random_digit2}/{current_datetime.strftime('%y')}/"
        f"{random_alphanum}-{random_5digits}/{cashier}/{random_2digits}"
    )
    y -= spacing
    c.drawString(5*mm, y*mm, transaction_info)
    
    # Second separator
    y -= spacing
    c.drawString(5*mm, y*mm, "-" * 42)
    
    # Items
    y = 246
    total_hemat = 0
    for item in items:
        item_total = item['quantity'] * item['price']
        c.drawString(5*mm, y*mm, f"{item['name'][:24]}")
        c.drawString(5*mm, (y-4)*mm, f"{item['quantity']} {item['price']:,} {item_total:,}")
        if 'hemat' in item and item['hemat'] > 0:
            total_hemat += item['hemat']
            c.drawString(50*mm, (y-4)*mm, f"DISKON: ({item['hemat']:,})")
        y -= 8
    
    # Totals
    y -= spacing
    c.drawString(5*mm, y*mm, "-" * 42)

    c.drawString(5*mm, (y-4)*mm, "HARGA JUAL :".ljust(20) + f"{subtotal:,}")
    y -= spacing
    c.drawString(5*mm, (y-5)*mm, "-" * 42)
    c.drawString(5*mm, (y-8)*mm, "TOTAL :".ljust(20) + f"{subtotal:,}")
    
    if payment_method != "CASH":
        c.drawString(5*mm, (y-12)*mm, "NON TUNAI :".ljust(20) + f"{subtotal:,}")
    
    if total_hemat > 0:
        c.drawString(5*mm, (y-16)*mm, "ANDA HEMAT :".ljust(20) + f"{total_hemat:,}")
    
    # Tax information
    ppn_base = round(subtotal / 1.11)
    ppn = subtotal - ppn_base
    c.drawString(5*mm, (y-24)*mm, f"PPN : DPP= {ppn_base:,} PPN= {ppn:,}")
    c.drawString(5*mm, (y-28)*mm, f"PJK RST.: DPP= {ppn_base*2:,} PJK= {ppn*2:,}")
    
    # Payment info
    if payment_method != "CASH":
        c.drawString(5*mm, (y-32)*mm, f"QR {payment_method}-TRXID:{datetime.now().strftime('%Y%m%d%H%M%S')}")
        c.drawString(5*mm, (y-36)*mm, f"NO:{'*'*20}AAAG,PURCHASE:{subtotal:,}")
    
    # Footer
    c.setFont(REGULAR_FONT, 7)
    c.drawString(5*mm, (y-44)*mm, "LAYANAN KONSUMEN")
    y -= spacing
    c.drawString(5*mm, (y-44.5)*mm, "SMS/WA 08111500280 TELP 1500280")
    y -= spacing
    c.drawString(5*mm, (y-45)*mm, "KONTAK@INDOMARET.CO.ID")
    y -= spacing 
    c.drawString(5*mm, (y-45.5)*mm, "BELANJA LEBIH MUDAH DI")
    y -= spacing
    c.drawString(5*mm, (y-46)*mm, "KLIKINDOMARET")
    y -= spacing
    c.drawString(5*mm, (y-46.5)*mm, "GRATIS ONGKIR 1 JAM SAMPAI")
    y -= spacing   
    c.save()
    buffer.seek(0)
    return buffer

def generate_random_items():
    num_items = random.randint(19, 22)
    items = []
    selected_items = random.sample(ITEMS, num_items)

    for item in selected_items:
        quantity = random.randint(1, 5)
        if "Premium" in item:
            price = random.randint(3500, 12900)
        else:
            price = random.randint(1500, 4900)
        
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

if mode == "手动":
    st.subheader("设置购物商品")
    num_items = st.number_input("商品数量:", min_value=1, value=5, step=1)

    if st.button("生成商品"):
        st.session_state['items'] = []
        selected_items = random.sample(ITEMS, min(num_items, len(ITEMS)))
        for item in selected_items:
            quantity = random.randint(1, 5)
            if "Premium" in item:
                price = random.randint(3500, 12900)
            else:
                price = random.randint(1500, 4900)
            
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
st.write("© 2024 收据生成器")
