"""Explicitly managed, optional ngrok tunnel for the local Streamlit server."""

from threading import RLock

from config import get_ngrok_auth_token


_LOCK = RLock()
_ACTIVE_TUNNEL = None


def start_ngrok(port: int = 8501) -> str:
    global _ACTIVE_TUNNEL
    token = get_ngrok_auth_token()
    if not token:
        raise ValueError(
            "NGROK_AUTHTOKEN is missing. Add it to .env to enable public access."
        )

    try:
        from pyngrok import conf, ngrok
    except ImportError as error:
        raise RuntimeError(
            "pyngrok is not installed. Install dependencies from requirements.txt."
        ) from error

    with _LOCK:
        if _ACTIVE_TUNNEL is not None:
            return _ACTIVE_TUNNEL.public_url
        try:
            _ACTIVE_TUNNEL = ngrok.connect(
                addr=port,
                proto="http",
                pyngrok_config=conf.PyngrokConfig(auth_token=token),
            )
        except Exception as error:
            _ACTIVE_TUNNEL = None
            raise RuntimeError(
                f"Could not start ngrok ({type(error).__name__}). "
                "Confirm Streamlit is running on port 8501 and check your ngrok setup."
            ) from error
        return _ACTIVE_TUNNEL.public_url


def stop_ngrok() -> None:
    global _ACTIVE_TUNNEL
    with _LOCK:
        if _ACTIVE_TUNNEL is None:
            return
        tunnel = _ACTIVE_TUNNEL
        _ACTIVE_TUNNEL = None
        try:
            from pyngrok import ngrok

            ngrok.disconnect(tunnel.public_url)
        except Exception as error:
            raise RuntimeError(
                f"Could not stop ngrok ({type(error).__name__})."
            ) from error
