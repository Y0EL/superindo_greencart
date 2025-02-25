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

st.title("Struck Superindo")

mode = st.radio("Pilih Mode", ["Manual", "Otomatis"])
use_bold = st.checkbox("Gunakan Teks Bold", value=False)

store_name = st.text_input("Nama toko:", "PT LION SUPERINDO")

uploaded_logo = st.file_uploader("Upload logo toko", type=["png", "jpg", "jpeg"])
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

if mode == "Manual":
    st.subheader("Atur Barang Belanjaan")
    num_items = st.number_input("Jumlah barang:", min_value=1, value=5, step=1)

    if st.button("Generate Barang"):
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
        st.write("Daftar Barang:")
        for item in st.session_state['items']:
            if item.get('hemat', 0) > 0:
                st.write(f"{item['name']} - Jumlah: {item['quantity']} - "
                        f"Harga: Rp {item['price']:,} "
                        f"(HEMAT: Rp {item['hemat']:,})")
            else:
                st.write(f"{item['name']} - Jumlah: {item['quantity']} - "
                        f"Harga: Rp {item['price']:,}")

    use_current_date = st.checkbox("Pakai Tanggal Hari Ini", value=True)
    if use_current_date:
        receipt_date = datetime.now().strftime("%y-%m-%d (%H:%M:%S)")
        st.write(f"Tanggal Terpilih: {receipt_date}")
    else:
        receipt_date = st.date_input("Pilih Tanggal Kustom", value=datetime.now()).strftime("%y-%m-%d")
        receipt_time = st.time_input("Pilih Waktu", value=datetime.now().time())
        receipt_date = f"{receipt_date} ({receipt_time.strftime('%H:%M:%S')})"

    if st.session_state['items']:
        subtotal = sum(item['quantity'] * item['price'] for item in st.session_state['items'])
        ppn = subtotal * 0.11
        total = subtotal + ppn


        st.write(f"Subtotal: Rp {subtotal:,.2f}")
        st.write(f"PPN (11%): Rp {ppn:,.2f}")
        st.write(f"Total: Rp {total:,.2f}")

        payment_methods = ["BNI QRIS", "MANDIRI", "BCA", "OVO", "GOPAY", "CASH"]
        payment_method = st.selectbox("Metode Pembayaran:", payment_methods)

        if st.button("Generate Struk"):
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

            # Create download button for PDF
            st.download_button(
                label="Download Struk PDF",
                data=pdf_buffer,
                file_name=f"receipt_{receipt_date.replace('/', '').replace(':', '').replace(' ', '_').replace('(', '').replace(')', '')}.pdf",
                mime="application/pdf"
            )

elif mode == "Otomatis":
    st.subheader("Generate Multiple Receipts")
    
    num_receipts = st.number_input("Jumlah struk yang akan dibuat:", min_value=1, max_value=50, value=5)
    
    if st.button("Generate Struk"):
        receipts = generate_random_receipts(num_receipts, store_name, logo_path, use_bold)
        
        # Create zip file containing all receipts
        zip_buffer = create_zip_file(receipts)
        
        # Create download button for ZIP
        st.download_button(
            label="Download Semua Struk (ZIP)",
            data=zip_buffer,
            file_name="superindo_receipts.zip",
            mime="application/zip"
        )

        # Display summary
        st.subheader("Ringkasan Struk:")
        total_sales = 0
        for i, receipt in enumerate(receipts, 1):
            st.write(f"Struk {i}:")
            st.write(f"Tanggal: {receipt['date']}")
            st.write(f"Kasir: {receipt['cashier']}")
            st.write(f"Metode Pembayaran: {receipt['payment_method']}")
            st.write(f"Total: Rp {receipt['total']:,.2f}")
            st.write(f"Jumlah Item: {len(receipt['items'])}")
            st.write("---")
            total_sales += receipt['total']
        
        st.write(f"Total Penjualan: Rp {total_sales:,.2f}")
        st.write(f"Rata-rata per Struk: Rp {(total_sales/num_receipts):,.2f}")

# Add footer
st.markdown("---")
st.markdown("### Tentang Aplikasi")
st.write("Aplikasi ini dibuat untuk menghasilkan struk belanja Superindo.")
st.write("Pilih mode Manual untuk mengatur detail struk atau mode Otomatis untuk menghasilkan multiple struk sekaligus.")
st.write("© 2024 Receipt Generator")
