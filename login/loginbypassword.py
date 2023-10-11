import requests 
import json
import hashlib
import login.generate_fingerprint as generate_fingerprint
import time
import random

def encrypt_pass(password):
    sha_signature = \
        hashlib.sha256((hashlib.md5(password.encode()).hexdigest()).encode()).hexdigest()
    return sha_signature

def random_str(length):
    character='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join((random.choice(character) for i in range(length)))

def loginbypassword(uname,pw):
    rq = requests.Session()
    csrftoken_gen = random_str(32)
    rq.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "referer": "https://shopee.co.id/buyer/login?next=https://shopee.co.id/",
        "x-api-source": "pc",
        "x-shopee-language": "id",
        "x-requested-with": "XMLHttpRequest",
        "x-csrftoken": csrftoken_gen
    })

    user_type = {
        "@" in uname: "email",
        uname.isdigit(): "phone"
        }.get(True, "username")
    
    if uname.isdigit():
        if uname[:2] == '62' :
            uname = uname
        elif uname[:2] == '08':
            uname = '62'+uname[1:]
    else :
        uname = uname

    payload = {
        user_type: uname,
        "password": encrypt_pass(pw),
        "support_ivs": True,
        "client_identifier":{"security_device_fingerprint":generate_fingerprint.generate_sig()}
        }
    
    rs = rq.post('https://shopee.co.id/api/v4/account/login_by_password', data=json.dumps(payload)).json()

    if rs['error'] == 2:
        return rq, 'error'
    else:
        return rq, rs
        
    

def gen_method(rq, datatoken):

    payload_method = {
        "event": 1,
        "u_token": datatoken['data']['ivs_token']
        }

    getmethod = rq.post('https://shopee.co.id/api/v4/anti_fraud/ivs/methods',data=json.dumps(payload_method))

    return rq, getmethod.json(), datatoken

def send_link(rq,datamethod,datatoken):
    try:
        payload_ver = {
            "msg_type": 2,
            "request_id": datatoken['data']['ivs_token'],
            "v_token" : datamethod['data'][0]['v_token']
        }
        sendlinkver = rq.post('https://shopee.co.id/api/v4/anti_fraud/ivs/link/verify',data=json.dumps(payload_ver))

        return rq, sendlinkver.json(), datatoken, datamethod
    except Exception as e:
        print(e)

        return rq, e, datatoken, datamethod

def check_status(rq, dataver):

    payload_stat = {
        "r_token" : dataver['data']['r_token']
        }
        
    status = 1

    print('wait for verification ...')
    timesec = 0
    while (status == 1) and (timesec < 300):
        rs_profile = rq.post('https://shopee.co.id/api/v4/anti_fraud/ivs/link/get_status', data = json.dumps(payload_stat))
        status = rs_profile.json()['data']['link_status']
        time.sleep(1)
        timesec = timesec + 1
        print('status update',status)
        print('timeout in',timesec)

    if status == 2:
        return 'verification successful'
    else :
        return 'verification tiumeout'
    

def verification_login(rq, dataver, datatoken, datamethod):

    payloadgetstatus = {
        "method_name":datamethod['data'][0]['type'],
        "event":1,
        "u_token":datatoken['data']['ivs_token'],
        "r_token":dataver['data']['r_token'],
        "v_token":datamethod['data'][0]['v_token'],
        "misc":{
            "operation":0
        }
    }

    genertever = rq.post('https://shopee.co.id/api/v4/anti_fraud/ivs/token/verify',data=json.dumps(payloadgetstatus))

    return rq , genertever.json()

def enable_login(rq, datatoken, datamethod, genertever, device_fingerprint):

    datalogin = {
        "is_user_login":True,
        "is_web":True,
        "ivs_flow_no":datatoken['data']['ivs_flow_no'],
        "ivs_signature":genertever['signature'],
        "ivs_method":datamethod['data'][0]['type'],
        "device_sz_fingerprint":device_fingerprint
        }

    logintrue = rq.post('https://shopee.co.id/api/v4/account/basic/login_ivs',data = json.dumps(datalogin))

    return rq

def generatecookie(rq):

    dictlist = []
    for key, value in rq.cookies.iteritems():
        temp = str(key)+'='+str(value)
        dictlist.append(temp)

    return rq, ' ; '.join(dictlist)

def loginShopee(uname, pw):
    rq, datatoken1 = loginbypassword(uname,pw)

    if datatoken1 == 'error':
        return rq, 'error'

    else :
        print('login by password')
        print(datatoken1)
        if datatoken1['data']['ivs_flow_no'] == None:
            rq, generateheader = generatecookie(rq)
            
            return rq, generateheader

        else:
            time.sleep(5)
            rq, datamethod1, datatoken2 = gen_method(rq, datatoken1)
            print('generate method')
            time.sleep(5)
            rq, dataver1, datatoken3, datamethod2 = send_link(rq, datamethod1, datatoken2)
            print('send link to verify')
            time.sleep(1)
            status = check_status(rq, dataver1)
            print('check status ...')

            if status =='verification successful':
                rq , genertever = verification_login(rq, dataver1, datatoken3, datamethod2)
                rq = enable_login(rq, datatoken3, datamethod2, genertever, generate_fingerprint.generate_sig())
                rq, generateheader = generatecookie(rq)

                return rq, generateheader

            else :

                return rq, 'timeout'