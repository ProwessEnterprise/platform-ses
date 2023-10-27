""" Generate a random alphanumeric OTP of a given length """
import secrets
import string

OTP_LENGTH = 8


def generate_alphanumeric_otp():
    """ Generate a random alphanumeric OTP of a given length """
    # Include uppercase letters, \lowercase letters, and digits
    characters = string.ascii_letters + string.digits
    otp = ''.join(secrets.choice(characters) for _ in range(OTP_LENGTH))
    return otp
