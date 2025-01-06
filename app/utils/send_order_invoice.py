from fpdf import FPDF
from flask import render_template, current_app as app

def send_order_invoice(email, order):
    if not email:
        app.logger.warning("No email provided for sending the invoice.")
        return

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="Order Invoice", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Order ID: {order.id}", ln=True)
        pdf.cell(200, 10, txt=f"Pickup Location: {order.pickup_location}", ln=True)
        pdf.cell(200, 10, txt=f"Dropoff Location: {order.dropoff_location}", ln=True)
        pdf.cell(200, 10, txt=f"Price: £{order.price:.2f}", ln=True)
        pdf.cell(200, 10, txt=f"Payment Method: {order.payment_method}", ln=True)

        invoice_filename = f"invoice_{order.id}.pdf"
        pdf.output(invoice_filename)

        app.logger.info(f"Invoice saved as {invoice_filename} (email sending disabled)")
        os.remove(invoice_filename)
    except Exception as e:
        app.logger.error(f"Failed to process order invoice: {e}")
