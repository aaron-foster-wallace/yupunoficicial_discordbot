# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import requests
import json
import time
import datetime
from dateutil import tz
import random

PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

import os
 
TOKEN =os.environ['TOKEN']


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    html="""       
Hi! I'm <b>YUP Bot!</b> You can ask me YUP questions like: 

<code>price       - </code>/price
<code>votelink    - </code>/votelink<code> &lt;voteid&gt;\n\t\t\t  returns the link of given a voteid</code>
<code>postidof    - </code>/link<code> &lt;url&gt; returns the url id</code>
<code>votesof     - </code>/votesof<code> &lt;url&gt;\n\t\t\t Return who vote for an adress\n\t\t\t(lista los que votaron por una direccion)</code>
<code>power       - </code>/power<code> &lt;eos_user&gt;  da la informacion de la carga de la cuenta    </code>    
<code>top_payment - </code>/top_payment<code> &lt;eos_user&gt; [skip] \n\t\t\t  get the last payment, or the nth last payment</code>
<code>tp          - </code>/tp<code> &lt;eos_user&gt; [skip]\n\t\t\t  (top_payment shorthand)</code>
<code>yup         - </code>/yup<code> ?????????</code>
<code>fee         - </code>/fee<code> bridge fees</code>
<code>coffe       - </code>/coffe or /cafe <code>\n\t\t\t Buy me a coffe, donation adress</code>
<code>donar       - </code>/donar<code>\n\t\t\t muestra informacion para hacer una donacion</code>
<code>help        - </code>/help<code> this text</code>


Antiguos/Legacy:

<code>pago        - </code>/pago<code> &lt;voteid&gt;  dice que link pago</code>     
<code>link        - </code>/link<code> &lt;direcion_web&gt; da el postid de la direccion</code>
<code>getpayment  - </code>/getpayment<code> &lt;eos_user&gt; [#n]  obtiene el n-último pago</code>
  

    """
    update.message.reply_html(html)

def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def echo(update, context):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

def postidof(update, context):
    """Echo the user message."""
    #link
    url = " ".join(context.args).strip()
    update.message.reply_text(real_postidof(url))


def real_postidof(url):
    """Echo the user message."""
    #link
    r = requests.post('https://api.yup.io/posts/post/caption', json={"caption": url})
    j = r.json()
    text=" Not Found/ No encontrado"
    
    if isinstance(j, list) and len(j)>0:
        if "_id" in j[0]:
            text = j[0]["_id"]
        else:
            text = "Unk error"
        if "message" in j: 
            text= j["message"]   
    return text

dict_cat={"popularity":"♥️","intelligence":"💡","funny":"😂","easy":"😎","interesting":"⚠️","useful":"🛠️","knowledgeable":"🎓","engaging":"🤔","chill":"❄️","affordable":"💲","beautiful":"🌸","trustworthy": "✅", "wouldelect": "🗳️", "agreewith": "👍", "original": "🦄" }

def votesof(update, context):
    global j
    url = " ".join(context.args).strip()
    postid = real_postidof(url)
    if not ("postid" in postid):
        error=postid
        update.message.reply_text(error)
        return
    
    postid=postid["postid"]
    r = requests.get("http://api.yup.io/votes/post/"+postid)
    j = r.json()
    html=""
    for num, v in enumerate(j, start=1):        
        voter = v["voter"]
        payment = "$ {}".format( v["claimed_curator_rewards"]) if v["processed"] else "⌛pending"   
        val=(int(v["rating"])+2 if v["like"] else 3-int(v["rating"]) )
        valstr="●"*val+"○"*(5-val)
        
        html+=("#{:>3}: <b>{}</b> \n<code>        {} {:>5}{}</code>\n".format(
                num,
                voter,
                dict_cat[v["category"]] if v["category"] in dict_cat else "?" ,
                valstr,
                ""))      
        
    update.message.reply_html(html)




def votedump(update, context):
 
    """ the user message."""   
    voteid = " ".join(context.args).strip()
    r = requests.post('https://eos.greymass.com/v1/chain/get_table_rows', json=  {"json":"true",  "code":"yupyupyupyup",  "scope":"yupyupyupyup",  "table":"votev2",  "table_key":"",  "lower_bound":voteid,  "upper_bound":"null",  "index_position":1,  "key_type":"",  "limit":"1",  "reverse":"false",  "show_payer":"false"})
    j= r.json()
    
    resp=""
    if not ("rows" in j and j["rows"] and "postid" in j["rows"][0]):
        update.message.reply_text("Voteid not found")
        return
    resp+="\n=================\n VOTE ON EOS BLOCK:\n"
    resp+=json.dumps(j["rows"][0], indent=4, sort_keys=True)    
    postid=j["rows"][0]["postid"]
    
    r2 = requests.get("https://api.yup.io/posts/post/"+str(postid))
    

        
    j2=r2.json()
    
    if "catVotes" in j2:
        resp+="\n=================\n POST ON YUP.IO SERVER:\n"    
        #resp+=json.dumps(j2["catVotes"], indent=4, sort_keys=True)    
        for c in cats:
            if cats[c]["up"]!=0 or cats[c]["down"]!=0:
                resp+=" "+(c+":\t (+)"+str(cats[c]["up"])+"\t(-)"+str(cats[c]["down"]))+"\n"
        
    if "caption" in j2:
        resp+="\n=================\n POST ORIGINAL" 
        resp+=j2["caption"]
    else:
        resp+="\n=================\nErr: Post not found"
    update.message.reply_text(resp)



def votelink(update, context):
    """ the user message."""   
    voteid = " ".join(context.args).strip()
    update.message.reply_text( pago_real(voteid))
     

def fee(update, context):
    txt=""
    #https://api.yup.io/bridge/status    tru if bridge active
    r = requests.get("https://api.yup.io/bridge/fee-yup")
    update.message.reply_text(r.text)

def pago_real(voteid):
    txt=""
    r = requests.post('https://eos.greymass.com/v1/chain/get_table_rows', json=  {"json":"true",  "code":"yupyupyupyup",  "scope":"yupyupyupyup",  "table":"votev2",  "table_key":"",  "lower_bound":voteid,  "upper_bound":"null",  "index_position":1,  "key_type":"",  "limit":"1",  "reverse":"false",  "show_payer":"false"})
    j= r.json()

    if not ("rows" in j and j["rows"] and "postid" in j["rows"][0]):
        return "Voteid not found"
        
    
    postid=j["rows"][0]["postid"]
    r2 = requests.get("https://api.yup.io/posts/post/"+str(postid))
    j2=r2.json()
    
    if "caption" in j2:
        return j2["caption"]
    else:
        return "Errore: Post not found"

def top_payment(update, context):
    text=""
    if(len(context.args)<1):
       update.message.reply_text("usage: /top_payment eos_user \n"   
                                 +"usage: /top_payment eos_user position_number##\n")
       return
 
    user = context.args[0]
    pos = 0
    if(len(context.args)>1):
        pos = context.args[1]
    r = requests.get("https://eos.hyperion.eosrio.io/v2/history/get_actions?account={}&limit=1&skip={}&filter=*:transfer&transfer.to={}".format(user,pos,user))
    j=r.json()
    a=j["actions"][0]
    text+="==============="
    text+="\n"    
    text+="    PAGO:"
    text+="\n"
    text+="==============="
    text+="\n"    
    text+="\n"    
    text+="FECHA HORA:"+a["timestamp"][:16]
    text+="\n"   
    trx_id=a["trx_id"]
    act=a["act"]
    d=act["data"]
    text+="quantity:"+d["quantity"]
    text+="\n"
    text+="Reason:"+d["memo"]
    text+="\n"
    """
         "amount": 0.0001,
          "symbol": "YUP",
          "memo": "Yup Curator Rewards",
          "quantity": "0.0001 YUP"
    """
    r2 = requests.get("https://eosauthority.com/api/spa/dfuse/transactions/{}?network=eos".format(trx_id))
    global j2
    
    j2=r2.json()
    voteid= j2["execution_trace"]["action_traces"][0]["act"]["data"]["voteid"]
    text+="POSTURL: "
    text+=pago_real(voteid) 
    update.message.reply_text(text)

def yup(update, context):
    update.message.reply_text(
        random.choice(
            ["Give Me Yups Human DArme YUPSSSSSsssss!!!!!!",
            "YAP YAP YAP YAP YAP YAP",
            "DOGE BRIDGE WHEN???",
            "DOGE BRIDGE WHEN???",
            "YDOWN",
            "ELON ELON VOTASTE A ELON OTRA VEZ AAOASAFFAFSFSFASFSAFSA",
            "{ ｡ ^ ◕ ‿ ◕ ^ ｡ }",
            "( ◕ ^ ^ ◕ )",
            "▆ ▇ █ █ VIVING!!",
            "NOP NOP",
            """
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⠟⠩⠶⣾⣿⡿⢯⣍⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⠏⠀⠀⠈⠉⠀⣠⢤⠈⠋⠀⢠⣄⠉⢻⣿⣿⣿⣿⠃⠈⢿⣿⣿⣿⣿⣿
⣿⡟⠁⠀⠀⠀⣹⣦⣀⣙⣈⣀⢶⣤⣈⣁⣠⣾⣿⣿⣿⡿⠀⠀⠼⢿⣿⣿⣿⣿
⡏⠀⠀⠠⣤⠦⣭⣙⣛⠛⠋⠁⠀⠙⠛⢉⣻⣿⣿⣿⠋⠁⠀⠀⠀⠀⠀⠀⠈⣿
⡇⠀⠀⠀⠛⠮⣽⣒⣻⣭⢽⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿
⡇⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠉⠉⣼⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿
⡟⠳⢤⣤⣀⣀⣀⠀⠀⠀⣀⣀⣤⣴⣾⣿⣿⣿⣿⣿⣷⣦⣤⣤⣤⣤⣤⣴⣾⣿
⣇⠀⠀⠀⠀⠉⠉⠈⠁⠈⠉⠉⡙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
"""
        ]))
      
def coffe(update, context):
    html="""
<b>Buy Me a Coffe:</b>    

    You can donate some EOS or YUP    to <b>yupxtelegram</b>  EOS Account

<b>Camprame un café:</b>    

    Puede donar algunos EOS o YUP a la cuenta de <b>yupxtelegram</b> EOS
    
    ✌(◕‿-)✌     \\̅_̅/̷̚ʾ \\̅_̅/̷̚ʾ. 
stating by just  0.1 YUP 
"""

    update.message.reply_html(html)

def power(update, context):
 
    """ the user message."""   
    user = " ".join(context.args).strip()    
    r = requests.get("https://api.yup.io/accounts/actionusage/"+str(user))
            
    j=r.json()
    j["lastReset_UTC"]=datetime.datetime.utcfromtimestamp( int(j["lastReset"])/1000).isoformat()[:16]
    j["lastReset_VNZ"]=datetime.datetime.fromtimestamp( int(j["lastReset"])/1000,tz=tz.gettz('America/Caracas')).isoformat()[:16]
    #time.strftime("%x %X", time.localtime(j["lastReset"]/1000 ))
    
    update.message.reply_text(json.dumps(j, indent=4, sort_keys=True) )

def priceold(update, context):
     
    """ the user message."""   
    r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum,yup&vs_currencies=usd,eth")
    j=r.json()
    #time.strftime("%x %X", time.localtime(j["lastReset"]/1000 ))
    txt="1 YUP = "+ str(j["yup"]["usd"] )+ " USD\n"
    txt+=" \" \"  = "+ str(j["yup"]["eth"] )+ " ETH\n\n"
    txt+="1 ETH  = "+ str(j["ethereum"]["usd"] )+ " USD\n"
    update.message.reply_text(txt)

def price(update, context):
     
    """ the user message."""   
    r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=ethereum,yup&vs_currencies=usd,eth")
    j=r.json()

    html="""   
    <B>PRICE OF YUP/ETH VIA COINGECKO:</B><pre><code>
   1 YUP  :   {} USD
   "   "  :   {} ETH
   1 ETH  :   {} USD
   </code></pre>

    yup yeah yap!
    """.format(str(j["yup"]["usd"] ),str(j["yup"]["eth"]),str(j["ethereum"]["usd"] ) )
    update.message.reply_html(html)
     
    

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("postidof", postidof))
    dp.add_handler(CommandHandler("votelink", votelink))    
    dp.add_handler(CommandHandler("yup", yup))    
    #dp.add_handler(CommandHandler("votedump", votedump))    
    dp.add_handler(CommandHandler("power", power))    
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("top_payment", top_payment))       
    dp.add_handler(CommandHandler("tp", top_payment))  

    dp.add_handler(CommandHandler("votesof", votesof))  
    dp.add_handler(CommandHandler("votosde", votesof))  
    dp.add_handler(CommandHandler("coffe", coffe))  
    dp.add_handler(CommandHandler("cafe", coffe))      
    dp.add_handler(CommandHandler("donar", coffe))  
    dp.add_handler(CommandHandler("fee", fee))  
    #dp.add_handler(CommandHandler("pricehtml", pricehtml))      


    #Legacy
    dp.add_handler(CommandHandler("pago", votelink))
    dp.add_handler(CommandHandler("getpayment", top_payment))   
    dp.add_handler(CommandHandler("link", postidof))    
    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, echo))
    
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
    updater.bot.setWebhook('https://yupyupyupyup.herokuapp.com/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
