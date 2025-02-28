import streamlit as st
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import random
from datetime import datetime, timedelta
import zipfile

# Inisialisasi font
try:
    pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
    pdfmetrics.registerFont(TTFont('Calibri-Bold', 'calibrib.ttf'))
except:
    st.warning("Font files not found. Using default fonts.")

CASHIERS = ["Emma", "Liam", "Olivia", "Noah", "Ava", "Ethan", "Sophia", "Mason", "Isabella", "William", "Mia", "James"]

ITEMS = [
    "Fuji Apples", "Red Delicious Apples", "Granny Smith Apples", "Golden Delicious Apples",
    "Cavendish Bananas", "Red Bananas", "Plantains", "Dragon Fruit",
    "Navel Oranges", "Mandarin Oranges", "Lemons", "Limes",
    "Honeydew Melon", "Cantaloupe", "Watermelon", "Galia Melon",
    "Red Grapes", "Green Grapes", "Black Grapes", "Cotton Candy Grapes",
    "Roma Tomatoes", "Cherry Tomatoes", "Beefsteak Tomatoes", "Heirloom Tomatoes",
    "Romaine Lettuce", "Iceberg Lettuce", "Arugula", "Spinach",
    "Broccoli", "Cauliflower", "Brussels Sprouts", "Asparagus",
    "Russet Potatoes", "Red Potatoes", "Sweet Potatoes", "Yukon Gold Potatoes",
    "Yellow Onions", "Red Onions", "Shallots", "Green Onions",
    "Carrots", "Baby Carrots", "Parsnips", "Turnips",
    "Red Bell Peppers", "Green Bell Peppers", "Yellow Bell Peppers", "Jalapeno Peppers",
    "Organic Seaweed Snacks", "Dried Seaweed Sheets", "Roasted Seaweed", "Seaweed Salad",
    "Atlantic Salmon Fillet", "Tuna Steak", "Cod Fillet", "Tilapia Fillet",
    "Chicken Breast", "Ground Beef", "Pork Chops", "Lamb Chops",
    "Tofu", "Tempeh", "Seitan", "Beyond Meat Burger Patties",
    "Cheddar Cheese", "Mozzarella Cheese", "Gouda Cheese", "Feta Cheese",
    "Greek Yogurt", "Almond Milk", "Oat Milk", "Coconut Milk",
    "Whole Wheat Bread", "Sourdough Bread", "Rye Bread", "Gluten-Free Bread",
    "Pasta Sauce", "Olive Oil", "Balsamic Vinegar", "Soy Sauce",
    "Canned Tomatoes", "Canned Beans", "Canned Tuna", "Canned Soup",
    "Breakfast Cereal", "Oatmeal", "Granola", "Protein Bars",
    "Coffee Beans", "Green Tea", "Black Tea", "Herbal Tea",
    "Potato Chips", "Tortilla Chips", "Popcorn", "Pretzels",
    "Chocolate Bar", "Candy", "Chewing Gum", "Mints",
    "Laundry Detergent", "Dish Soap", "Hand Soap", "Paper Towels",
    "Toilet Paper", "Tissues", "Trash Bags", "Aluminum Foil"
]

def generate_random_date():
    days_ago = random.randint(0, 7)
    random_date = datetime.now() - timedelta(days=days_ago)
    random_time = datetime.strptime(f"{random.randint(8, 21)}:{random.randint(0, 59)}:{random.randint(0, 59)}", "%H:%M:%S").time()
    return random_date.strftime("%y-%m-%d") + f" ({random_time.strftime('%H:%M:%S')})"

def apply_discount(items):
    discounted_items = []
    discount_count = 0
    for item in items:
        if random.random() < 0.3 or (len(items) - len(discounted_items) <= 4 - discount_count):
            discount_percentage = random.choice([10, 15, 20, 25])
            original_price = item['price']
            discounted_price = round(original_price * (1 - discount_percentage/100), 2)
            savings = round(original_price - discounted_price, 2)
            discounted_items.append({
                **item,
                'price': discounted_price,
                'savings': savings,
                'original_price': original_price
            })
            discount_count += 1
        else:
            discounted_items.append({**item, 'savings': 0})
    return discounted_items

def create_receipt(store_name, items, total, payment_method, receipt_date, use_bold=False, cashier_name=None, logo=None):
    buffer = io.BytesIO()
    width, height = 45 * mm, 210 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))

    font = "Calibri-Bold" if use_bold else "Calibri"

    left_indent = 2 * mm
    x = left_indent
    y = height - 5 * mm

    # Draw logo
    if logo:
        logo_width = 10 * mm
        logo_height = 10 * mm
        c.drawImage(ImageReader(logo), x, y - logo_height, width=logo_width, height=logo_height)
        x += logo_width + 2 * mm

    c.setFont(font, 8)
    c.drawString(x, y, store_name)
    y -= 3*mm
    c.drawString(x, y, "TIN: 12-3456789")
    y -= 3*mm
    c.drawString(x, y, "Established: 01-01-2000")
    y -= 3*mm
    c.drawString(x, y, "123 MAIN STREET")
    y -= 3*mm
    c.drawString(x, y, "NEW YORK, NY 10001")
    y -= 3*mm
    c.drawString(x, y, "Tel: (555) 123-4567")
    y -= 8*mm

    x = left_indent  # Reset x to left indent
    c.drawString(x, y, f"{receipt_date} No: {random.randint(1000, 9999)}")
    if cashier_name:
        c.drawString(x, y - 3*mm, f"Cashier: {cashier_name}")
        y -= 3*mm
    y -= 1*mm

    separator = '=' * int((width - 2*left_indent) / c.stringWidth('=', font, 8))
    y -= 2*mm

    c.drawString(x, y, "DESCRIPTION      QTY    PRICE")
    y -= 3*mm
    c.drawString(x, y, separator)
    y -= 3*mm

    for item in items:
        name = item['name'][:15]
        quantity = item['quantity']
        price = item['price']
        item_total = price * quantity
        
        item_text = f"{name:<15} {quantity:>3} ${item_total:>6.2f}"
        c.drawString(x, y, item_text)
        y -= 3*mm
        
        if item.get('savings', 0) > 0:
            original_price = item.get('original_price', price)
            savings_text = f"SAVE: ${item['savings']:.2f}"
            c.setFillColorRGB(1, 0, 0)
            c.drawString(x + 2*mm, y, savings_text)
            c.setFillColorRGB(0, 0, 0)
            y -= 3*mm

    y -= 1*mm
    c.drawString(x, y, separator)
    y -= 3*mm

    tax = total * 0.08
    total_with_tax = total + tax

    c.drawString(x, y, f"Subtotal: ${total:.2f}")
    y -= 3*mm
    c.drawString(x, y, f"Tax (8%): ${tax:.2f}")
    y -= 3*mm
    c.drawString(x, y, f"Total (Including Tax): ${total_with_tax:.2f}")
    y -= 3*mm
    c.drawString(x, y, f"Payment - {payment_method}: ${total_with_tax:.2f}")
    y -= 3*mm
    c.drawString(x, y, f"Number: T{random.randint(100000000, 999999999)}")
    y -= 4*mm

    c.drawString(x, y, f"Total Items: {len(items)}")
    y -= 4*mm

    footer_lines = [
        "**Thank you for shopping with us**",
        "YOUR FEEDBACK IS OUR PRIORITY",
        "TOLL-FREE: 1-800-123-4567",
        "WHATSAPP: +1 (555) 987-6543 (CALL ONLY)",
        "MONDAY - FRIDAY 8:00 AM - 5:00 PM EST",
        "Email: customer.service@freshmarket.com",
        "www.freshmarket.com"
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
    num_items = random.randint(10, 15)
    items = []
    selected_items = random.sample(ITEMS, num_items)

    for item in selected_items:
        quantity = random.randint(1, 3)
        if "Organic" in item or "Premium" in item or "Fillet" in item or "Chops" in item:
            price = round(random.uniform(5.99, 15.99), 2)
        elif "Detergent" in item or "Soap" in item or "Paper" in item or "Trash" in item or "Foil" in item:
            price = round(random.uniform(3.99, 9.99), 2)
        else:
            price = round(random.uniform(1.50, 4.99), 2)
        
        items.append({
            "name": item,
            "quantity": quantity,
            "price": price
        })

    return apply_discount(items)

def generate_random_receipts(num_receipts, store_name, use_bold, logo):
    receipts = []
    for _ in range(num_receipts):
        items = generate_random_items()
        receipt_date = generate_random_date()
        cashier = random.choice(CASHIERS)
        subtotal = sum(item['quantity'] * item['price'] for item in items)
        payment_method = random.choice(["VISA", "MASTERCARD", "AMEX", "APPLE PAY", "GOOGLE PAY", "CASH"])
        
        pdf_buffer = create_receipt(
            store_name,
            items,
            subtotal,
            payment_method,
            receipt_date,
            use_bold,
            cashier,
            logo
        )
        
        receipts.append({
            'buffer': pdf_buffer,
            'date': receipt_date,
            'cashier': cashier,
            'items': items,
            'total': subtotal + (subtotal * 0.08),
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
            summary += f"Total: ${receipt['total']:.2f}\n"
            summary += f"Items: {len(receipt['items'])}\n\n"
        
        zip_file.writestr("summary.txt", summary)

    zip_buffer.seek(0)
    return zip_buffer

st.title("Receipt Generator")

mode = st.radio("Select Mode", ["Manual", "Automatic"])
use_bold = st.checkbox("Use Bold Text", value=True)
store_name = st.text_input("Store Name:", "FRESH MARKET")

# Logo upload
uploaded_logo = st.file_uploader("Upload store logo (optional)", type=["png", "jpg", "jpeg"])
if uploaded_logo:
    logo = Image.open(uploaded_logo)
else:
    # Create a default logo
    logo = Image.new('RGB', (100, 100), color='green')
    pixels = logo.load()
    for i in range(logo.size[0]):
        for j in range(logo.size[1]):
            if (i + j) % 2 == 0:
                pixels[i, j] = (255, 255, 255)

if 'items' not in st.session_state:
    st.session_state['items'] = []
if 'cashier' not in st.session_state:
    st.session_state['cashier'] = random.choice(CASHIERS)

if mode == "Manual":
    st.subheader("Set Shopping Items")
    num_items = st.number_input("Number of Items:", min_value=1, value=10, step=1)

    if st.button("Generate Items"):
        st.session_state['items'] = []
        selected_items = random.sample(ITEMS, min(num_items, len(ITEMS)))
        for item in selected_items:
            quantity = random.randint(1, 3)
            if "Organic" in item or "Premium" in item or "Fillet" in item or "Chops" in item:
                price = round(random.uniform(5.99, 15.99), 2)
            elif "Detergent" in item or "Soap" in item or "Paper" in item or "Trash" in item or "Foil" in item:
                price = round(random.uniform(3.99, 9.99), 2)
            else:
                price = round(random.uniform(1.50, 4.99), 2) 
            else:
                price = round(random.uniform(1.50, 4.99), 2) 
            
            st.session_state['items'].append({
                "name": item,
                "quantity": quantity,
                "price": price
            })
        
        st.session_state['items'] = apply_discount(st.session_state['items'])

    if st.session_state['items']:
        st.write("Item List:")
        for item in st.session_state['items']:
            if item.get('savings', 0) > 0:
                st.write(f"{item['name']} - Quantity: {item['quantity']} - "
                         f"Price: ${item['price']:.2f} "
                         f"(SAVE: ${item['savings']:.2f})")
            else:
                st.write(f"{item['name']} - Quantity: {item['quantity']} - "
                         f"Price: ${item['price']:.2f}")

    use_current_date = st.checkbox("Use Current Date and Time", value=False)
    if use_current_date:
        receipt_date = datetime.now().strftime("%y-%m-%d (%H:%M:%S)")
        st.write(f"Selected Date: {receipt_date}")
    else:
        receipt_date = generate_random_date()
        st.write(f"Randomly Generated Date: {receipt_date}")

    if st.session_state['items']:
        subtotal = sum(item['quantity'] * item['price'] for item in st.session_state['items'])
        tax = subtotal * 0.08
        total = subtotal + tax

        st.write(f"Subtotal: ${subtotal:.2f}")
        st.write(f"Tax (8%): ${tax:.2f}")
        st.write(f"Total: ${total:.2f}")

        payment_methods = ["VISA", "MASTERCARD", "AMEX", "APPLE PAY", "GOOGLE PAY", "CASH"]
        payment_method = st.selectbox("Payment Method:", payment_methods)

        if st.button("Generate Receipt"):
            pdf_buffer = create_receipt(
                store_name,
                st.session_state['items'],
                subtotal,
                payment_method,
                receipt_date,
                use_bold,
                st.session_state['cashier'],
                logo
            )

            st.download_button(
                label="Download Receipt PDF",
                data=pdf_buffer,
                file_name=f"receipt_{receipt_date.replace('/', '').replace(':', '').replace(' ', '_').replace('(', '').replace(')', '')}.pdf",
                mime="application/pdf"
            )

elif mode == "Automatic":
    st.subheader("Generate Multiple Receipts")

    num_receipts = st.number_input("Number of Receipts to Generate:", min_value=1, max_value=50, value=5)

    if st.button("Generate Receipts"):
        receipts = generate_random_receipts(num_receipts, store_name, use_bold, logo)
        
        zip_buffer = create_zip_file(receipts)
        
        st.download_button(
            label="Download All Receipts (ZIP)",
            data=zip_buffer,
            file_name="fresh_market_receipts.zip",
            mime="application/zip"
        )

        st.subheader("Receipts Summary:")
        total_sales = 0
        for i, receipt in enumerate(receipts, 1):
            st.write(f"Receipt {i}:")
            st.write(f"Date: {receipt['date']}")
            st.write(f"Cashier: {receipt['cashier']}")
            st.write(f"Payment Method: {receipt['payment_method']}")
            st.write(f"Total: ${receipt['total']:.2f}")
            st.write(f"Items: {len(receipt['items'])}")
            st.write("---")
            total_sales += receipt['total']
        
        st.write(f"Total Sales: ${total_sales:.2f}")
        st.write(f"Average per Receipt: ${(total_sales/num_receipts):.2f}")

if st.button("Again"):
    st.session_state['items'] = []
    st.session_state['cashier'] = random.choice(CASHIERS)
    st.rerun()

st.markdown("---")
st.markdown("### About the App")
st.write("This application is used to generate Fresh Market shopping receipts.")
st.write("Choose manual mode to set receipt details or automatic mode to generate multiple receipts at once.")
st.write("© 2024 Receipt Generator")
