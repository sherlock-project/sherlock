class InvalidUsernameError(Exception):
    """Lançada quando o username possui caracteres não suportados pelo Sherlock."""
    pass

class ServiceTimeoutError(Exception):
    """Lançada quando a busca atinge o tempo limite estabelecido."""
    pass

class UpstreamError(Exception):
    """Lançada quando há um erro não tratado na CLI do Sherlock."""
    pass
