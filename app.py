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
    # ... (rest of the function remains the same)

def generate_random_items():
    # ... (rest of the function remains the same)

def generate_random_receipts(num_receipts, store_name, logo_path, use_bold):
    # ... (rest of the function remains the same)

def create_zip_file(receipts):
    # ... (rest of the function remains the same)

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

        st.write(f"Subtotal: Rp {subtotal:,.2f}")
        st.write(f"PPN (11%): Rp {ppn:,.2f}")
        st.write(f"Total: Rp {total:,.2f}")

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

# Add footer
st.markdown("---")
st.markdown("### 关于应用")
st.write("此应用程序用于生成 Superindo 购物收据。")
st.write("选择手动模式以设置收据详细信息，或选择自动模式以一次生成多个收据。")
st.write("© 2024 收据生成器")
