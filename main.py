import login.loginbypassword as log_ins
import transaction.transaction as tr
from colorama import Fore, init

def main():

    init()
    INFO = Fore.LIGHTBLUE_EX + "[*]" + Fore.BLUE
    INPUT = Fore.LIGHTGREEN_EX + "[?]" + Fore.GREEN
    WARNING = Fore.LIGHTGREEN_EX + "[!]" + Fore.RED

    print(INFO, "Enter username / email / phone number")
    user = input(INPUT + " username / email / number: " + Fore.WHITE)
    print(INFO, "Enter the password")
    password = input(INPUT + " password: " + Fore.WHITE)
    print(INFO, "Logging in ...")

    rq, cookie = log_ins.loginShopee(user, password)

    if cookie == 'error':
        print(WARNING,"Error invalid username/phone or password")
    
    elif cookie == 'timeout':
        print(WARNING,"Timeout for verification link")

    else :
        print(INFO, "Logging Success ...")

        # get transaction
        gelltr = tr.getTransaction(rq, cookie)
        print('count transaction result :', len(gelltr))
        orderid = gelltr[0]['info_card']['order_id']
        print('first order id :',orderid)
        get_detail = tr.getDetailTransaction(rq, cookie, orderid)
        print('detail tr ex :', get_detail)

        #getshopeepay balance
        balanceshopeepay = tr.getBalance(rq, cookie)
        print('balance : Rp.',balanceshopeepay)

if __name__ == "__main__":
    main()