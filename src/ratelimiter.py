from slowapi import Limiter
from slowapi.util import get_remote_address
# todo: подумать как сделать так чтобы проект не ломался.
limiter = Limiter(key_func=get_remote_address)
