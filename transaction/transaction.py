import json
import requests

def getTransaction(rq, cookie):
    headers = {
        "User-Agent": rq.headers['User-Agent'],
        "referer": rq.headers['referer'],
        "x-api-source": rq.headers['x-api-source'],
        "x-shopee-language": rq.headers['x-shopee-language'],
        "x-requested-with": rq.headers['x-requested-with'],
        "cookie" : cookie
    }

    getalltrs = []

    transaction = requests.get("https://shopee.co.id/api/v4/order/get_all_order_and_checkout_list?limit=20&offset=0",headers=headers).json()

    for i in range(len(transaction['data']['order_data']['details_list'])):
        getalltrs.append(transaction['data']['order_data']['details_list'][i])

    while (transaction['data']['next_offset'] != -1):
        transaction = requests.get("https://shopee.co.id/api/v4/order/get_all_order_and_checkout_list?limit=20&offset={0}".format(transaction['data']['next_offset']),headers=headers).json()
        print(transaction['data']['order_data'])
        if transaction['data']['order_data'] == {}:
            transaction['data']['next_offset']==-1
        else :
            for j in range(len(transaction['data']['order_data']['details_list'])):
                getalltrs.append(transaction['data']['order_data']['details_list'][j])
    
    return getalltrs
    

def getDetailTransaction(rq, cookie, orderid):
    
    headers = {
        "User-Agent": rq.headers['User-Agent'],
        "referer": rq.headers['referer'],
        "x-api-source": rq.headers['x-api-source'],
        "x-shopee-language": rq.headers['x-shopee-language'],
        "x-requested-with": rq.headers['x-requested-with'],
        "cookie" : cookie
    }
    
    gelldetailtrascation = requests.get("https://shopee.co.id/api/v4/order/get_order_detail?order_id={}".format(orderid),headers=headers).json()

    return gelldetailtrascation


def getBalance(rq, cookie):
    headers = {
        "User-Agent": rq.headers['User-Agent'],
        "referer": rq.headers['referer'],
        "x-api-source": rq.headers['x-api-source'],
        "x-shopee-language": rq.headers['x-shopee-language'],
        "x-requested-with": rq.headers['x-requested-with'],
        "cookie" : cookie
    }

    """
    To check balance we need to checkout first so check the cart and if there a item in cart we used it to checkout and check the balance, and if not, we will add some thing item first then checkout
    and delete the item if we have got the balance
    """
    # check cart
    payloadcheckcart = {"pre_selected_item_list":[],
                        "updated_time_filter":{
                        "start_time":0},
                        "version":11}

    checkcart = requests.post("https://shopee.co.id/api/v4/cart/get", headers=headers, data=json.dumps(payloadcheckcart)).json()

    if len(checkcart['data']['shop_orders']) == 0:
        # add the item in cart and get the balance
        itemid = 6233786790
        shopid = 40847197

        datamodel = requests.get("https://shopee.co.id/api/v2/item/get_ratings?filter=0&flag=1&itemid={0}&limit=6&offset=0&shopid={1}&type=0".format(itemid,shopid), headers=headers).json()
        datamodel['data']['ratings'][0]['product_items'][0]['modelid']

        paylodaddtochart = {"quantity":1,
                            "checkout":True,
                            "update_checkout_only":False,
                            "donot_add_quantity":False,
                            "source":"{\"refer_urls\":[]}",
                            "client_source":1,
                            "shopid":shopid,
                            "itemid":itemid,
                            "modelid":datamodel['data']['ratings'][0]['product_items'][0]['modelid']
                            }
        checkout = requests.post("https://shopee.co.id/api/v4/cart/add_to_cart",headers=headers,data=json.dumps(paylodaddtochart)).json()
        
        paylodcheckbalance ={"shoporders":[{
                            "shop":{"shopid":shopid},
                            "items":[{"itemid":itemid,
                            "modelid":checkout['data']['cart_item']['modelid'],
                            "quantity":1,}]
                            }]}
        
        databalance = requests.post("https://shopee.co.id/api/v4/checkout/get",headers=headers, data=json.dumps(paylodcheckbalance)).json()

        payloaddeletecart = {"action_type":2,
                            "updated_shop_order_ids":[{
                            "shopid":shopid,
                            "item_briefs":[{
                                "shopid":shopid,
                                "itemid":itemid,
                                "modelid":checkout['data']['cart_item']['modelid'],
                                "item_group_id":None,
                                "add_on_deal_id":None,
                                "is_add_on_sub_item":None,
                                "quantity":1,
                                "old_modelid":None,
                                "old_quantity":1,
                                "checkout":False,
                                "price":checkout['data']['cart_item']['price']
                                }]
                            }],
                            "version":11}
        clearcart = requests.post("https://shopee.co.id/api/v4/cart/update",headers=headers, data=json.dumps(payloaddeletecart))

        return databalance['payment_channel_info']['channels'][0]['balance']/100000


    else :
        # gotocheckout and get balance
        paylodcheckbalance ={"shoporders":[{
            "shop":{"shopid":checkcart['data']['shop_orders'][0]['shop']['shopid']},
            "items":[{"itemid":checkcart['data']['shop_orders'][0]['items'][0]['itemid'],
            "modelid":checkcart['data']['shop_orders'][0]['items'][0]['modelid'],
            "quantity":1,}]
            }]}

        databalance = requests.post("https://shopee.co.id/api/v4/checkout/get",headers=headers, data=json.dumps(paylodcheckbalance)).json()

        return databalance['payment_channel_info']['channels'][0]['balance']/100000
