import requests

def print_Result(type, test, res):
    if res == 'Failed':
        prRed(f'{type}test{test}: {res}')
    elif res == 'Success':
        prGreen(f'{type}test{test}: {res}')
    else:
        prRed('WARNING! TEST IS UNDEFINED')

url = 'http://10.130.66.174:5000/login'

r = requests.get(url)

#Color terminal
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))
def prGreen(skk): print("\033[92m {}\033[00m" .format(skk))

print('status code:', r.status_code)

logins = [{'username':'Bob','password':'Pass1234'},
          {'username':'carsten','password':'pass1234'}]

i = 0
for login in logins:
    test = 'Failed'
    r = requests.post(url, data=login)
    
    #-- Early Sample --#
    #if r.url != url:
    #    test = 'Success'
    #    prGreen(f'test{i}: {test}')
    #else:
    #    prRed(f'test{i}: {test}')

    if r.cookies.values() != []: #Check for cookies, if there is none, login = false
        test = 'Success'

    i = i + 1

    print_Result('Login', i, test)