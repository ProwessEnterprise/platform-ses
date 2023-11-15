""" Enum classes for the application """
from enum import Enum

class PlatformUserStatus(Enum):
    """ Platform User status enum class"""
    SIGNUP_INITIATED = "SIGNUP-INITIATED"
    SIGNUP_OTP_SENT = "SIGNUP-OTP-SENT"
    SIGNUP_OTP_FAILED = "SIGNUP-OTP-FAILED"
    SIGNUP_VALIDATED = "SIGNUP-VALIDATED"
    SIGNUP_COMPLETED = "SIGNUP-COMPLETED"
    SIGNUP_FAILED = "SIGNUP-FAILED"
