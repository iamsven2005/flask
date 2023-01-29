import re

def check_password_strength(password):
    if len(password) < 8:
        return "short password"
    elif re.search("[a-z]", password) is None:
        return "Missing lowercase letter"
    elif re.search("[A-Z]", password) is None:
        return "Missing uppercase letter"
    elif re.search("[0-9]", password) is None:
        return "Missing number"
    elif re.search("[!@#\$%^&*()_\-+=\{\}\[\]:;\"'<>,.?/|\\~`]", password) is None:
        return "Missing special character"
    else:
        return "Strong"

password = input("Enter a password: ")
print(check_password_strength(password))