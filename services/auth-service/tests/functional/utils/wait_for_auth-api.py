import socket

from tests.functional.core.config_log import get_logger
from tests.functional.core.settings import test_conf
from tests.functional.utils.decorators import backoff

logger = get_logger("wait_for_api")


@backoff(exception=(ConnectionRefusedError, socket.timeout, ValueError))
def check_api():
    host = test_conf.auth.host
    port = test_conf.auth.port
    path = "/auth/api/openapi.json"

    with socket.create_connection((host, port), timeout=2) as sock:
        request = f"GET {path} HTTP/1.1\r\n" f"Host: {host}\r\n" f"Connection: close\r\n\r\n"
        sock.send(request.encode())

        response = sock.recv(1024).decode()
        code = response.split(" ")[1]
        if code == "200":
            logger.debug("API готов к тестированию")
            return True
        raise ValueError(f"API вернул код {code}, ожидался 200")


if __name__ == "__main__":
    check_api()
