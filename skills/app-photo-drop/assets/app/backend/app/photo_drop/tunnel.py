import asyncio
import os

import ngrok


class TunnelError(RuntimeError):
    pass


class NgrokTunnel:
    def __init__(self, guest_port: int):
        self.guest_port = guest_port
        self.listener = None

    async def start(self) -> str:
        if not os.environ.get("NGROK_AUTHTOKEN", "").strip():
            raise TunnelError("NGROK_AUTHTOKEN is required to start the public tunnel")
        try:
            self.listener = await asyncio.to_thread(
                ngrok.forward,
                f"http://127.0.0.1:{self.guest_port}",
                authtoken_from_env=True,
            )
            public_origin = self.listener.url().rstrip("/")
        except Exception as error:
            raise TunnelError("Ngrok tunnel failed to start") from error
        if not public_origin.startswith("https://"):
            raise TunnelError("Ngrok did not return an HTTPS origin")
        return public_origin

    async def stop(self) -> None:
        if self.listener is None:
            return
        listener = self.listener
        try:
            await listener.close()
        except Exception as error:
            raise TunnelError("Could not close ngrok tunnel") from error
        self.listener = None
