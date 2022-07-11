from base64 import b64decode

class Config:
    httponly_nats_cookie: boolean = True
    nats_cookie_name = 'nats_cookie'
    krb5_service_name = ''

CONFIG: Config

def _gssapi_authenticate(token):
    rc, state = None, None
    user, krb5_token = None, None
    try:
        rc, state = kerberos.authGSSServerInit(CONFIG.krb5_service_name)
        if rc == kerberos.AUTH_GSS_COMPLETE:
            rc = kerberos.authGSSServerStep(state, token)
            if rc == kerberos.AUTH_GSS_COMPLETE:
                krb5_token = kerberos.authGSSServerResponse(state)
                user = kerberos.authGSSServerUserName(state)
    except kerberos.GSSError:
        pass
    finally:
        if state:
            kerberos.authGSSServerClean(state)
    return rc, user, krb5_token

def _ldap_authenticate(user, credentials):
    return True

Jwt = NewType('Jwt', str)

def validate(cookie) -> bool:
    #validate with NSC ?
    return False

def _unauthorized(error=''):
    response.set_header('WWW-Authenticate', 'Negotiate')
    response.status = 401
    request.session['return_to'] = quote(request.url)


def _forbidden():
    response.status = 403

def _actual_user(user: str) -> str:
    return user


def check():
    cookie = request.get_cookie(CONFIG.nats_cookie_name)
    if cookie and validate(cookie):
        return cookie

    header = request.headers.get("Authorization")
    if !header:
        _unauthorized()
        return cookie

    kind, credentials = header.split(maxsplit=1)
    if kind == 'Kerberos':
        rc, krb5_user, krb5_token = _gssapi_authenticate(credentials)
        elif rc == kerberos.AUTH_GSS_COMPLETE:
            user = _actual_user(krb5_user)
            response.set_header('WWW-Authenticate', f'negotiate {krb5_token}')
            return user
        elif rc == kerberos.AUTH_GSS_CONTINUE:
            _unauthorized()
        else:
            _forbidden()
    elif kind == 'Basic':
        user, password = b64decode(credentials).split(':', maxsplit=1)
        if user not in allowed_basic_auth:
            _unauthorized()
            return None
        _ldap_authenticate(user, password)
        return user


def requires_authentication(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        if (user := check()):
            return function(user, *args, **kwargs)
    return decorated

@requires_authentication
@route('nats_token')
async def nats_token(user):
    nsc = await subprocess.exec(f'nsc describe user --raw {user}')
    if nsc.result.error:
        raise RuntimeError(nsc.stderr)
    cookie = nsc.stdout
    http_only: bool = request.params.get('http_only', True) or CONFIG.httponly_nats_cookie
    response.set_cookie(CONFIG.nats_cookie_name, cookie, secure=True, httponly=http_only)

