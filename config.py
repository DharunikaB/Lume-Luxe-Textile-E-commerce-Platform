import razorpay

# Replace these with your Test Mode API keys from Razorpay Dashboard
RAZORPAY_KEY_ID = "rzp_test_UJOyiCZ1FFC00z"
RAZORPAY_KEY_SECRET = "x3fieBJG2VVKs0FSwcpAeosh"

# Initialize Razorpay Client
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

