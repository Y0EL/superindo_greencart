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
"APEL FJI PRM", "APEL RED DEL", "APEL MLG", "APEL GRN SMT", "PISANG AMB", "PISANG RAJ",
"PISANG KPK", "PISANG SPRD", "JERUK MND", "JERUK SNK", "JERUK PNT", "JERUK NPS", "SEMANGKA MRH",
"SEMANGKA BBY", "SEMANGKA KNG", "MELON HNYDW", "MELON GLD", "MELON RCK", "ANGGUR RED GLB", "ANGGUR THMP",
"WORTEL LKL", "WORTEL IMP BBY", "BROKOLI PRM", "BROKOLI BBY", "KENTANG DNG", "KENTANG GRN", "TOMAT CHRY",
"TOMAT BEEF", "CABAI KRT MRH", "CABAI RWT HJU", "CABAI MRH BSR", "BAWANG BMB", "BAWANG MRH BRB", "BAWANG PUT KTNG", "BYM HJU ORG", "KNGKUNG HDRPNK", "SELADA RMN", "SELADA KRT", "SAWI PTH", "SAWI HJU",
"PKCY PRM", "DAUN SKG", "DAUN PPY", "KEMANGI SGR", "APEL ORG", "PISANG ORG", "JERUK ORG",
"WORTEL ORG", "KENTANG ORG", "TOMAT ORG", "BROKOLI ORG", "SELADA ORG", "KNGKUNG ORG", "SAWI ORG"
]

# Company information options
COMPANY_INFO = [
    {
        "name": "PT SUPERINDO JAYA PRIMA",
        "address1": "GEDUNG GRAHA SUPER",
        "address2": "JL. ANCOL BARAT BLOK A",
        "address3": "JAKARTA UTARA",
        "tax_id": "NPWP: 021 458 932 7-092 000"
    },
    {
        "name": "PT MAJU BERSAMA SUKSES",
        "address1": "GEDUNG MENARA MAJU",
        "address2": "JL. GATOT SUBROTO KAV 12",
        "address3": "JAKARTA SELATAN",
        "tax_id": "NPWP: 085 392 647 1-073 000"
    },
    {
        "name": "PT BERKAH SWALAYAN NUSANTARA",
        "address1": "GEDUNG NUSANTARA TOWER",
        "address2": "JL. SUDIRMAN KAV 54-55",
        "address3": "JAKARTA PUSAT",
        "tax_id": "NPWP: 091 475 621 3-082 000"
    },
    {
        "name": "PT INDO RETAIL MAKMUR",
        "address1": "MENARA INDAH KAPUK LT 12",
        "address2": "JL. BOULEVARD TIMUR",
        "address3": "TANGERANG",
        "tax_id": "NPWP: 073 182 495 8-065 000"
    },
    {
        "name": "PT SENTOSA NIAGA SEJAHTERA",
        "address1": "GEDUNG SENTOSA PLAZA",
        "address2": "JL. PLUIT SAKTI RAYA No.28",
        "address3": "JAKARTA UTARA",
        "tax_id": "NPWP: 062 549 871 3-074 000"
    }
]

# Footer information options
FOOTER_INFO = [
    {
        "line1": "LAYANAN PELANGGAN",
        "line2": "SMS/WA 08119876543 TELP 1500123", 
        "line3": "INFO@SUPERINDO.CO.ID",
        "line4": "BELANJA ONLINE DI",
        "line5": "SUPERSHOPONLINE",
        "line6": "GRATIS ONGKIR MIN. BELANJA 100RB"
    },
    {
        "line1": "CUSTOMER SERVICE",
        "line2": "SMS/WA 08112345678 CALL 14045", 
        "line3": "HELP@GROSIR.CO.ID",
        "line4": "DOWNLOAD APLIKASI KAMI",
        "line5": "GROSIR ONLINE",
        "line6": "POIN 2X LIPAT SETIAP JUMAT"
    },
    {
        "line1": "PUSAT BANTUAN",
        "line2": "WA 08123456789 CALL 1500456", 
        "line3": "CARE@FRESHMART.COM",
        "line4": "TEMUKAN KAMI DI",
        "line5": "WWW.FRESHMART.COM",
        "line6": "DISKON 10% UNTUK MEMBER"
    },
    {
        "line1": "HUBUNGI KAMI",
        "line2": "TELP 021-5437890 HP 081234567", 
        "line3": "SUPPORT@EASYMART.ID",
        "line4": "BELANJA LEBIH MUDAH DI",
        "line5": "APLIKASI EASYMART",
        "line6": "PENGIRIMAN CEPAT AREA JABODETABEK"
    },
    {
        "line1": "BANTUAN PELANGGAN",
        "line2": "SMS/WA 08567891234 CALL 14789", 
        "line3": "SERVICE@FAMILYMART.COM",
        "line4": "PROMO MENARIK DI",
        "line5": "FAMILYMART APP",
        "line6": "PROGRAM TUKAR POIN DI KASIR"
    }
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
    
    # Randomly select company info and footer info
    company_info = random.choice(COMPANY_INFO)
    footer_info = random.choice(FOOTER_INFO)
    
    # Set transparency for header company info
    c.saveState()
    c.setFillAlpha(0.5)
    c.setFont(REGULAR_FONT, 7)
    
    # Header with minimal spacing
    y = 280
    spacing = 3
    c.drawString(5*mm, y*mm, company_info["name"])
    y -= spacing
    c.drawString(5*mm, y*mm, company_info["address1"])
    y -= spacing
    c.drawString(5*mm, y*mm, company_info["address2"])
    y -= spacing
    c.drawString(5*mm, y*mm, company_info["address3"])
    y -= spacing
    c.drawString(5*mm, y*mm, company_info["tax_id"])
    c.restoreState()
    
    # Draw logo on the right side with different aspect ratios based on logo number
    y = 280
    spacing = 3
    logo = ImageReader(logo_path)
    
    # Set different dimensions based on logo file
    if logo_path == "logo1.png" or logo_path == "logo2.png":
        # Square aspect ratio (1:1)
        c.drawImage(logo, 58*mm, 271*mm, width=15*mm, height=15*mm)
    else:
        # Standard rectangle aspect ratio
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
    
    # Items - Modified layout to show quantity and price on same line as item name
    y = 242
    total_hemat = 0
    for item in items:
        item_total = item['quantity'] * item['price']
        # Format item details on one line: NAME       QTY PRICE TOTAL
        item_name = item['name'][:18]  # Shortened to make room for price info
        qty_price_total = f"{item['quantity']} x {item['price']:,} = {item_total:,}"
        
        # Draw the item name on the left
        c.drawString(5*mm, y*mm, item_name)
        
        # Draw quantity, price and total on the right side of the same line
        c.drawRightString(70*mm, y*mm, qty_price_total)
        
        # Add discount line if applicable
        if 'hemat' in item and item['hemat'] > 0:
            total_hemat += item['hemat']
            y -= 4
            c.drawString(15*mm, y*mm, f"DISKON: ({item['hemat']:,})")
        
        y -= 6  # Reduce spacing between items
    
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
        # Generate 4 random uppercase letters instead of fixed AAAG
        random_4letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
        c.drawString(5*mm, (y-36)*mm, f"NO:{'*'*20}{random_4letters},PURCHASE:{subtotal:,}")
    
    # Footer
    c.setFont(REGULAR_FONT, 7)
    c.drawString(5*mm, (y-44)*mm, footer_info["line1"])
    y -= spacing
    c.drawString(5*mm, (y-44.5)*mm, footer_info["line2"])
    y -= spacing
    c.drawString(5*mm, (y-45)*mm, footer_info["line3"])
    y -= spacing 
    c.drawString(5*mm, (y-45.5)*mm, footer_info["line4"])
    y -= spacing
    c.drawString(5*mm, (y-46)*mm, footer_info["line5"])
    y -= spacing
    c.drawString(5*mm, (y-46.5)*mm, footer_info["line6"])
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

def get_random_logo():
    # Randomly select a logo from logo1.png to logo5.png
    logo_number = random.randint(1, 5)
    return f"logo{logo_number}.png"

def generate_random_receipts(num_receipts, store_name, use_bold):
    receipts = []
    for _ in range(num_receipts):
        items = generate_random_items()
        receipt_date = generate_random_date()
        cashier = random.choice(CASHIERS)
        subtotal = sum(item['quantity'] * item['price'] for item in items)
        payment_method = random.choice(["BNI QRIS", "MANDIRI", "BCA", "OVO", "GOPAY", "CASH"])
        
        # Get random logo for each receipt
        logo_path = get_random_logo()
        
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
            'payment_method': payment_method,
            'logo': logo_path
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
            summary += f"Logo: {receipt['logo']}\n"
            summary += f"Total: Rp {receipt['total']:,.2f}\n"
            summary += f"Items: {len(receipt['items'])}\n\n"
        
        zip_file.writestr("summary.txt", summary)

    zip_buffer.seek(0)
    return zip_buffer

st.title("收据生成器")

mode = st.radio("选择模式", ["手动", "自动"])
use_bold = st.checkbox("使用粗体文本", value=True)
store_name = st.text_input("商店名称:", "PT LION SUPERINDO")

# For manual mode, allow selecting a specific logo
if mode == "手动":
    logo_choice = st.selectbox("选择商店标志:", ["logo1.png", "logo2.png", "logo3.png", "logo4.png", "logo5.png", "自定义"])
    if logo_choice == "自定义":
        uploaded_logo = st.file_uploader("上传您的商店标志", type=["png", "jpg", "jpeg"])
        if uploaded_logo is not None:
            logo_path = "temp_logo.png"
            with open(logo_path, "wb") as f:
                f.write(uploaded_logo.getbuffer())
        else:
            logo_path = "logo1.png"
    else:
        logo_path = logo_choice
else:
    # For automatic mode, we'll use the random logo selection in generate_random_receipts
    logo_path = None

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
        receipts = generate_random_receipts(num_receipts, store_name, use_bold)
        
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
            st.write(f"标志: {receipt['logo']}")
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