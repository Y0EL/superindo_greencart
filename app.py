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
from datetime import datetime
from reportlab.lib.utils import ImageReader

# Register the fonts
pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
pdfmetrics.registerFont(TTFont('MSGothic', 'msgothic.ttc'))

CASHIERS = ["Raymond", "Sofi", "Derren", "Jack", "Jackuavis", "Septian", "Joel", "Dgueby", "Gerald", "Sintia", "Chia", "Defi"]

def create_receipt(store_name, items, total, payment_method, receipt_date, logo_path):
    buffer = io.BytesIO()
    width, height = 48 * mm, 210 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    # Set initial position
    x = 2 * mm
    y = height - 5 * mm

    # Header
    header_height = 30 * mm
    header_mid = width / 2
    left_indent = 6 * mm

    # Logo
    logo = ImageReader(logo_path)
    logo_width = 10 * mm
    logo_height = 10 * mm
    c.drawImage(logo, x, y - logo_height, width=logo_width, height=logo_height)

    # Store details with hanging indent
    c.setFont("Calibri", 6.5)
    c.drawString(left_indent + logo_width, y, store_name)
    y -= 2.5*mm
    c.drawString(left_indent + logo_width, y, "NPWP: 00.178.137.2-604.000")
    y -= 2.5*mm
    c.drawString(left_indent + logo_width, y, "Tanggal Pengukuhan: 06-06-97")
    y -= 2.5*mm
    c.drawString(left_indent + logo_width, y, "MUARA KARANG RAYA NO. 2")
    y -= 2.5*mm
    c.drawString(left_indent + logo_width, y, "JAKARTA UTARA")
    y -= 2.5*mm
    c.drawString(left_indent + logo_width, y, "JAKARTA UTARA")
    y -= 2.5*mm
    c.drawString(left_indent + logo_width, y, "Telp: 6697927")
    y -= 6*mm

    # Date and receipt number
    c.setFont("MSGothic", 6.5)
    c.drawString(x, y, f"{receipt_date} No: {random.randint(1000, 9999)}")
    y -= 2.5*mm

    # Separator using '='
    separator = '=' * int((width - 2*x) / c.stringWidth('=', "Calibri", 6.5))

    # Items
    c.setFont("MSGothic", 6.5)
    c.drawString(x, y, "DESKRIPSI        QTY    HARGA")
    y -= 3*mm
    c.drawString(x, y, separator)
    y -= 3*mm

    for item in items:
        name, quantity, price = item['name'], item['quantity'], item['price']
        item_total = price * quantity
        item_text = f"{name[:15]:<15} {quantity:>3} {item_total:>10,.0f}"
        c.drawString(x, y, item_text)
        y -= 2*mm

    # Subtotal and payment
    y -= 1*mm
    c.drawString(x, y, separator)
    y -= 3*mm
    
    # Calculate PPN (11% of subtotal)
    ppn = total * 0.11
    total_with_ppn = total + ppn
    
    # Randomly assign BTKP and BKP
    btkp = random.uniform(0, total)
    bkp = total - btkp

    c.drawString(x, y, f"Sub Total: {total:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"BTKP: {btkp:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"BKP: {bkp:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"PPN (11%): {ppn:,.0f}")
    y -= 6*mm
    c.drawString(x, y, f"Total (Termasuk PPN): {total_with_ppn:,.0f}")
    y -= 3*mm
    c.drawString(x, y, f"Pembayaran - {payment_method}: {total_with_ppn:,.0f}")
    y -= 3*mm
    left_indent = 2*mm
    x = 4*mm
    c.drawString(x, y, f"Nomor: {random.randint(100000000, 999999999)}")
    y -= 4*mm

    # Tax breakdown
    c.drawString(x, y, f"Total Item: {len(items)}")
    y -= 4*mm

    # Footer
    c.setFont("Calibri", 6.5)
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
        text_width = c.stringWidth(line, "Calibri", 6.5)
        c.drawString((width - text_width) / 2, y, line)
        y -= 3*mm

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Streamlit app
st.title("Struck Superindo")

store_name = st.text_input("Nama toko:", "PT LION SUPERINDO")

# Upload logo
uploaded_logo = st.file_uploader("Upload logo toko", type=["png", "jpg", "jpeg"])
if uploaded_logo is not None:
    logo_path = "temp_logo.png"
    with open(logo_path, "wb") as f:
        f.write(uploaded_logo.getbuffer())
else:
    logo_path = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS3Dmh9aaEXHrx-s4ewFBPK3a4Eq3FtfOTjNw&s"  # Make sure to have a default logo in your directory

if 'items' not in st.session_state:
    st.session_state['items'] = []

if 'cashier' not in st.session_state:
    st.session_state['cashier'] = random.choice(CASHIERS)

st.subheader("Atur Barang Belanjaan")

def add_item():
    new_item = {"name": "", "quantity": 1, "price": 0}
    st.session_state['items'].append(new_item)

def remove_item(index):
    del st.session_state['items'][index]

if st.button("Tambah Barang"):
    add_item()

for index, item in enumerate(st.session_state['items']):
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        item['name'] = st.text_input(f"Barang ke {index+1}", value=item['name'], key=f"name_{index}")
    with col2:
        item['quantity'] = st.number_input(f"Jumlah {index+1}", min_value=1, value=item['quantity'], step=1, key=f"quantity_{index}")
    with col3:
        item['price'] = st.number_input(f"Harga (Rp) {index+1}", min_value=0, value=item['price'], step=1000, key=f"price_{index}")
    with col4:
        if st.button("Hapus", key=f"remove_{index}"):
            remove_item(index)
            st.rerun()

subtotal = sum(item['quantity'] * item['price'] for item in st.session_state['items'])
ppn = subtotal * 0.11
total = subtotal + ppn

st.subheader(f"Subtotal: Rp {subtotal:,.0f}")
st.subheader(f"PPN (11%): Rp {ppn:,.0f}")
st.subheader(f"Total (Termasuk PPN): Rp {total:,.0f}")

payment_options = ["BNI QRIS", "MANDIRI", "BCA", "OVO", "GOPAY", "CASH"]
selected_payment = st.selectbox("Pilih Metode Pembayaran", payment_options)

use_current_date = st.checkbox("Pakai Tanggal Hari Ini", value=True)
if use_current_date:
    receipt_date = datetime.now().strftime("%y-%m-%d (%H:%M:%S)")
    st.write(f"Tanggal Terpilih: {receipt_date}")
else:
    receipt_date = st.date_input("Pilih Tanggal Kustom", value=datetime.now()).strftime("%y-%m-%d")
    receipt_time = st.time_input("Pilih Waktu", value=datetime.now().time())
    receipt_date = f"{receipt_date} ({receipt_time.strftime('%H:%M:%S')})"

if st.button("Ganti Kasir"):
    st.session_state['cashier'] = random.choice(CASHIERS)
    st.rerun()

st.write(f"Kasir Saat Ini: {st.session_state['cashier']}")

if st.button("Generate Struk"):
    if st.session_state['items']:
        pdf_buffer = create_receipt(store_name, st.session_state['items'], subtotal, selected_payment, receipt_date, logo_path)

        st.download_button(
            label="Download Struk",
            data=pdf_buffer,
            file_name="struk_superindo.pdf",
            mime="application/pdf"
        )

        st.subheader("Preview Struk")
        pdf_bytes = pdf_buffer.getvalue()
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="400" height="600" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.warning("Tambah minimal satu barang untuk membuat struk!")

