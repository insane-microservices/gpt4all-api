# Configuration
import requests

CLIENT_ID = 'api-auth'
CLIENT_SECRET = 'Fj7EePgcf1HxedsKC54fT3nERXGtQ2FL'
TOKEN_ENDPOINT = 'http://localhost:8080/auth/realms/raksha/protocol/openid-connect/token'
INTROSPECTION_ENDPOINT = 'http://localhost:8080/realms/raksha/protocol/openid-connect/token/introspect'

def authenticate_request(func):
    def wrapper(*args, **kwargs):
        args_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        authenticate_token = ''
        for idx, arg_name in enumerate(args_names):
            if arg_name == 'authorization':
                authenticate_token = args[idx]
                break
        if not authenticate_token:
            return jsonify({'message': 'Missing token'}), 401

        authenticate_token = authenticate_token.split('Bearer')[1]
        
        # Validate token using Keycloak introspection endpoint
        response = requests.post(INTROSPECTION_ENDPOINT, data={
            'token': authenticate_token,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        })
        if response.status_code == 200:
            token_info = response.json()
            if token_info['active']:
                return func(*args, **kwargs)
            else:
                return jsonify({'message': 'Invalid token'}), 401
        else:
            return jsonify({'message': 'Unable to validate token'}), 500
    
    wrapper.__name__ = func.__name__
    return wrapper