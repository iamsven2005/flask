import secrets
import string

def generate_otp(length=6):
  # Get a random string of letters and digits
  alphabet = string.ascii_letters + string.digits
  return ''.join(secrets.choice(alphabet) for i in range(length))

otp = generate_otp()
print(otp)  # prints something like "aB1cDe2"
