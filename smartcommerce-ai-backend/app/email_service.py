import yagmail

# Set up yagmail SMTP client
yag = yagmail.SMTP(user="your-email@gmail.com", password="your-email-password")

# Function to send email using yagmail
def send_order_confirmation_email(to_email, order):
    try:
        # Prepare email content
        subject = "Order Confirmation"
        content = f"""
        Hi,
        Thank you for your purchase! Your order ID is {order.order_id}.
        Total price: ${order.total_price}
        """
        
        html_content = f"""
        <html>
        <body>
            <p>Hi,<br>
            Thank you for your purchase!<br>
            Your order ID is <strong>{order.order_id}</strong>.<br>
            Total price: <strong>${order.total_price}</strong>.<br>
            </p>
        </body>
        </html>
        """
        
        # Send email
        yag.send(to=to_email, subject=subject, contents=[content, html_content])
        
        print("Order confirmation email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
