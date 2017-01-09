from hashlib import sha512
from satchmo.configuration import config_get_group

payment_module = config_get_group('PAYMENT_INGENICO')


def shasign(data):
    """To verify the data that is submitted to its system (in case of
    e-Commerce the hidden fields to the payment page), Ogone requires
    the secure data verification method SHA. For each order, your
    server generates a unique character string (=digest), hashed with
    the SHA algorithm SHA-512.

    A similar calculation can be done after the transaction, to verify
    the parameters returned with the redirection URLs. We call this
    the SHA-OUT.

    """
    secret = payment_module.SECRET.value

    # Join the fields in alphabetical order, using the secret
    # passphrase (and append it to the end too)
    #
    # See https://payment-services.ingenico.com/int/en/ogone/support/guides/integration%20guides/e-commerce#shainsignature
    phrase = secret.join((
        u"{key}={value}".format(
            key=key.upper(),
            value=value
        )
        for key, value
        in sorted(data.items())
        if key != "SHASIGN"
    )) + secret

    digest = sha512(phrase).hexdigest()

    return digest


def verify_shasign(sign, data):
    # This is a naive implementation. It does not run in fixed time
    # and is therefor vulnerable to timing attacks.
    return sign == shasign(data)
