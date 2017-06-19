from Crypto.Hash import MD5


def md5(str):
    h = MD5.new(str)
    return h.hexdigest()


def sign_md5(params):
    if type(params) is list or type(params) is tuple:
        return md5(''.join(params))
    else:
        return md5('%s' % params)

