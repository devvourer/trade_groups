from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice


def get_user_totp_device(user, confirmed=True):
    devices = devices_for_user(user, confirmed=confirmed)
    for device in devices:
        if isinstance(device, TOTPDevice):
            return device


def get_roe(capital: float, pnl: float):
    result = pnl / capital
    return round(result * 100, 2)


cript_symbols = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'DOGEUSDT', 'GMTUSDT', 'XRPUSDT', 'GALUSDT', 'DOTUSDT', 'ADAUSDT',
                 'FTMUSDT']