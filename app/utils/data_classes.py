"""Data classes for the project."""
from dataclasses import dataclass

@dataclass
class ConnectionInfo:
    """ ConnectionInfo class """
    rabbitmq_broker_id: str
    rabbitmq_user: str
    rabbitmq_password: str


@dataclass
class DBConnectionInfo:
    """ DBConnectionInfo class """
    host_name: str
    user_name: str
    database_password: str
    database: str


@dataclass
class IndentRequestInfo:
    """ IndentRequestInfo class """
    asset_type: str
    model: str
    make: str
    os: str
    processor: str
    ram: str
    screen_size: str
    vendor_name: str


@dataclass
class AssetInfo:
    """ AssetInfo class """
    asset_type: str
    asset_id: str
    asset_model: str


@dataclass
class SignupOtpInfo:
    """ SignupOtp info"""
    signup_user: str
    otp: str

@dataclass
class RegisterCompleteInfo:
    """ RegisterCompleteInfo info"""
    account_name: str
