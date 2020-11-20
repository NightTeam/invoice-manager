import binascii
import hashlib
import hmac
import sys
from datetime import datetime

if sys.version_info.major < 3:
    from urllib import quote, unquote


    def hmacsha256(keyByte, message):
        return hmac.new(keyByte, message, digestmod=hashlib.sha256).digest()


    # Create a "String to Sign".
    def StringToSign(canonicalRequest, t):
        bytes = HexEncodeSHA256Hash(canonicalRequest)
        str = datetime.strftime(t, BasicDateFormat)
        return "%s\n%s\n%s" % (Algorithm, datetime.strftime(t, BasicDateFormat), bytes)

else:
    from urllib.parse import quote, unquote


    def hmacsha256(keyByte, message):
        return hmac.new(keyByte.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()


    # Create a "String to Sign".
    def StringToSign(canonicalRequest, t):
        bytes = HexEncodeSHA256Hash(canonicalRequest.encode('utf-8'))
        str = datetime.strftime(t, BasicDateFormat)

        return "%s\n%s\n%s" % (Algorithm, datetime.strftime(t, BasicDateFormat), bytes)


def urlencode(s):
    return quote(s, safe='~')


# HexEncodeSHA256Hash returns hexcode of sha256
def HexEncodeSHA256Hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


# HWS API Gateway Signature
class HttpRequest:
    def __init__(self):
        self.method = ""
        self.scheme = ""  # http/https
        self.host = ""  # example.com
        self.uri = ""  # /request/uri
        self.query = {}
        self.headers = {}
        self.body = ""


BasicDateFormat = "%Y%m%dT%H%M%SZ"
Algorithm = "SDK-HMAC-SHA256"
HeaderXDate = "X-Sdk-Date"
HeaderHost = "host"
HeaderAuthorization = "Authorization"
HeaderContentSha256 = "x-sdk-content-sha256"


def CanonicalRequest(r):
    canonicalHeaders = CanonicalHeaders(r)
    if HeaderContentSha256 in r.__headers:
        hexencode = r.__headers[HeaderContentSha256]
    else:
        hexencode = HexEncodeSHA256Hash(r.body)
    return "%s\n%s\n%s\n%s\n%s\n%s" % (
        r.method, CanonicalURI(r), CanonicalQueryString(r), canonicalHeaders, SignedHeaders(r), hexencode)


def CanonicalURI(r):
    pattens = unquote(r.uri).split('/')
    uri = []
    for v in pattens:
        uri.append(urlencode(v))
    urlpath = "/".join(uri)
    if urlpath[-1] != '/':
        urlpath = urlpath + "/"  # always end with /
    return urlpath


def CanonicalQueryString(r):
    a = []
    for key in r.query:
        value = r.query[key]
        if value == "":
            kv = urlencode(key)
        else:
            kv = urlencode(key) + "=" + urlencode(value)
        a.append(kv)
    a.sort()
    return '&'.join(a)


def CanonicalHeaders(r):
    a = []
    __headers = {}
    for key in r.headers:
        value = r.headers[key]
        keyEncoded = key.lower()
        valueEncoded = value.strip()
        a.append(keyEncoded + ":" + valueEncoded)
        __headers[keyEncoded] = valueEncoded
        if sys.version_info.major == 3:
            r.headers[key] = valueEncoded.encode("utf-8").decode('iso-8859-1')

    a.sort()
    r.__headers = __headers
    return '\n'.join(a) + "\n"


def SignedHeaders(r):
    a = []
    for key in r.headers:
        a.append(key.lower())
    a.sort()
    return ";".join(a)


# Create the HWS Signature.
def SignStringToSign(stringToSign, signingKey):
    hm = hmacsha256(signingKey, stringToSign)
    return binascii.hexlify(hm).decode()


# Get the finalized value for the "Authorization" header.  The signature
# parameter is the output from SignStringToSign
def AuthHeaderValue(signature, AppKey, signedHeaders):
    return "%s Access=%s, SignedHeaders=%s, Signature=%s" % (
        Algorithm, AppKey, signedHeaders, signature)


class SignerError(Exception):
    pass


class Signer:
    def __init__(self):
        self.AppKey = ""
        self.AppSecret = ""

    # SignRequest set Authorization header
    def Sign(self, r):
        if sys.version_info.major == 3 and isinstance(r.body, str):
            r.body = r.body.encode('utf-8')
        headerTime = r.headers.get(HeaderXDate)
        if headerTime is None:
            t = datetime.utcnow()
            r.headers[HeaderXDate] = datetime.strftime(t, BasicDateFormat)
        else:
            t = datetime.strptime(headerTime, BasicDateFormat)

        haveHost = False
        for key in r.headers:
            if key.lower() == 'host':
                haveHost = True
                break
        if not haveHost:
            r.headers["host"] = r.host

        canonicalRequest = CanonicalRequest(r)
        stringToSign = StringToSign(canonicalRequest, t)
        signature = SignStringToSign(stringToSign, self.AppSecret)
        signedHeaders = SignedHeaders(r)
        authValue = AuthHeaderValue(signature, self.AppKey, signedHeaders)
        r.headers[HeaderAuthorization] = authValue
        r.headers["content-length"] = str(len(r.body))
        queryString = CanonicalQueryString(r)
        if queryString != "":
            r.uri = r.uri + "?" + queryString
