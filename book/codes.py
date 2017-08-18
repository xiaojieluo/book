'''
api codes
'''

CODES = {
    107: b'Malformed json object. A json dictionary is expected.',
}

CODES.update({
    200: b'Username is missing or empty',
    201: b'Password is missing or empty.',
    202: b'Username has already been taken.',
    206: b'The user cannot be altered by a client without the session.',
    210: b'The username and password mismatch.',
    211: b'Could not find user.',
    219: b'If the number of login failures exceeds the limit, please try again, or reset your password by forgetting your password',
})

CODES.update({
    500 : 'The value type is incorrect',
})

if __name__ == '__main__':
    print(CODES[200])
