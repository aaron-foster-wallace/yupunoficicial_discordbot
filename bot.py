# -*- coding: utf-8 -*-
import discord
import os
import logging
import os
import requests
import json
import time
import datetime
from dateutil import tz
import random
from markdownify import markdownify




#### BEGIN TELEGRAM PACH ########


class TeleWrapperMessage(object):
    def __init__(self, message):
        self.ms=message
    async def reply_text(self,text):
        await self.ms.channel.send(text)

    async def reply_html(self,text):
        await self.ms.channel.send(markdownify(text))

    
class TeleWrapper(object):
    def __init__(self, message):        
        self.message = TeleWrapperMessage(message)

class TeleContext(object):
    def __init__(self, args):        
        self.args = args


#### END TELEGRAM PACH ########


async def start(update, context):
    """Send a message when the command /start is issued."""
    html="""       
Hi! I'm <b>YUP Bot!</b> You can ask me YUP questions like: 
<ul>
<li><code>price       - </code>$price</li>
<li><code>votelink    - </code>$votelink<code> &lt;voteid&gt;\n\t\t\t  returns the link of given a voteid</code></li>
<li><code>postidof    - </code>$link<code> &lt;url&gt; returns the url id</code></li>
<li><code>votesof     - </code>$votesof<code> &lt;url&gt;\n\t\t\t Return who vote for an adress\n\t\t\t(lista los que votaron por una direccion)</code></li>
<li><code>power       - </code>$power<code> &lt;eos_user&gt;  da la informacion de la carga de la cuenta    </code>    </li>
<li><code>top_payment - </code>$top_payment<code> &lt;eos_user&gt; [skip] \n\t\t\t  get the last payment, or the nth last payment</code></li>
<li><code>tp          - </code>$tp<code> &lt;eos_user&gt; [skip]\n\t\t\t  (top_payment shorthand)</code></li>
<li><code>yup         - </code>$yup<code> ?????????</code></li>
<li><code>fee         - </code>$fee<code> bridge fees</code></li>
<li><code>help        - </code>$help<code> this text</code></li>
</ul>
    """
    await update.message.reply_html(html)

async def help(update, context):
    """Send a message when the command /help is issued."""
    await start(update, context)

async def echo(update, context):
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def postidof(update, context):
    """Echo the user message."""
    #link
    url = " ".join(context.args).strip()
    await update.message.reply_text(real_postidof(url))


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

async def votesof(update, context):
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
        
    await update.message.reply_html(html)




async def votedump(update, context):
 
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
    await update.message.reply_text(resp)



async def votelink(update, context):
    """ the user message."""   
    voteid = " ".join(context.args).strip()
    await update.message.reply_text( pago_real(voteid))
     

async def fee(update, context):
    txt=""
    #https://api.yup.io/bridge/status    tru if bridge active
    r = requests.get("https://api.yup.io/bridge/fee-yup")
    await update.message.reply_text(r.text)

async def pago_real(voteid):
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

async def top_payment(update, context):
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

    text+="<b>PAGO:</b>"
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
 
    r2 = requests.get("https://eos.hyperion.eosrio.io/v2/history/get_transaction?id={}".format(trx_id))
    global j2
    
    j2=r2.json()
    acs=j2.get('actions', False) or False
    if not acs: raise "Err bad response"
    i=0
    while i<len(acs) and  acs[i]["act"]["name"]=="noop": i+=1
    act=acs[i]["act"]
    if "from" in act["data"] and act["data"]["from"] == 'pool.yup':
        await update.message.reply_text("Payment #{}: Recived a tip from YUP TEAM of: {}".format(pos,act["data"]["quantity"]))
        return
    if "voteid" not in act["data"]:
        await update.message.reply_text("Payment #{}: Unknow payment type".format(pos))        
        return    
    
    voteid= act["data"]["voteid"]
    text+="POSTURL: "
    text+="<code>"+ (await pago_real(voteid)) +"</code>"
    await update.message.reply_html(text)
 
async def yup(update, context):
    await update.message.reply_text(
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
      


async def power(update, context):
 
    """ the user message."""   
    user = " ".join(context.args).strip()    
    r = requests.get("https://api.yup.io/accounts/actionusage/"+str(user))
            
    j=r.json()
    j["lastReset_UTC"]=datetime.datetime.utcfromtimestamp( int(j["lastReset"])/1000).isoformat()[:16]
    j["lastReset_VNZ"]=datetime.datetime.fromtimestamp( int(j["lastReset"])/1000,tz=tz.gettz('America/Caracas')).isoformat()[:16]
    #time.strftime("%x %X", time.localtime(j["lastReset"]/1000 ))
    
    await update.message.reply_text(json.dumps(j, indent=4, sort_keys=True) )

     
    

def telegrammmm_error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
async def price(update, context):
     
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
    await update.message.reply_html(html)
     



client = discord.Client()

def iscmdfulltext(txt,cmd):    
    return (len(txt.splitlines())==1) and "$"+cmd in [txt,txt.split()[0]]

def iscmd(txt,cmd):    
    return "$"+cmd == txt

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    try:
        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

        #Bring Commands implemented on telegram    
        txt=message.content
        if len(txt.splitlines())>1:        
            return
        cmd,*args=txt.split()

        update=TeleWrapper(message)
        context=TeleContext(args)

        if iscmd(cmd,"start"):
            await start(update,context)
        if iscmd(cmd,"help"):
            await help(update,context)
        if iscmd(cmd,"postidof"):
            await postidof(update,context)
        if iscmd(cmd,"votelink"):
            await votelink(update,context)
        if iscmd(cmd,"yup"):
            await yup(update,context)
        if iscmd(cmd,"votedump"):
            await votedump(update,context)
        if iscmd(cmd,"power"):
            await power(update,context)
        if iscmd(cmd,"price"):
            await price(update,context)
        if iscmd(cmd,"top_payment"):
            await top_payment(update,context)
        if iscmd(cmd,"tp"):
            await top_payment(update,context)
        if iscmd(cmd,"votesof"):
            await votesof(update,context)
        if iscmd(cmd,"votosde"):
            await votesof(update,context)
        if iscmd(cmd,"fee"):
            await fee(update,context)
    except:
        await message.channel.send('Sorry err... beep!')

              


client.run(os.getenv('YUPDISCORDTOKEN'))

