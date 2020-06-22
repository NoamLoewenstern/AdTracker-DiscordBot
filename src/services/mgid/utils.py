from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit


def add_token_to_uri(uri: str, token: str) -> str:
    """ add token to uri """
    parsed_url = urlparse(uri)
    if not parsed_url.query:
        uri += '?token=' + token
    elif 'token=' not in parsed_url.query:
        uri += '&token=' + token
    elif '{token}' in parsed_url.query:
        uri = uri.format(token=token)
    elif '%7Btoken%7D' in uri:  # uri-encoded {token}
        uri = uri.replace('%7Btoken%7D', token)

    return uri


def update_client_id_in_uri(uri: str, client_id: str) -> str:
    """ update client_id in uri """

    if '{client_id}' in uri:
        uri = uri.format(client_id=client_id)
    elif '%7Bclient_id%7D' in uri:  # uri-encoded {client_id}
        uri = uri.replace('%7Bclient_id%7D', client_id)

    return uri
