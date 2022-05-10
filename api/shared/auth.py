import jwt


def verify(token, jwks_url, audience, issuer, algorithms=['RS256']):
    try:
        jwt.decode(
            token,
            jwt.PyJWKClient(jwks_url).get_signing_key_from_jwt(token).key,
            algorithms=algorithms,
            audience=audience,
            issuer=issuer,
            options={"verify_signature": True}
        )

        return True

    except Exception:
        return False
