import razorpay

# Replace these with your Test Mode API keys from Razorpay Dashboard
RAZORPAY_KEY_ID = "YOUR_KEY"
RAZORPAY_KEY_SECRET = "YOUR_SECRET_KEY_HERE"

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

