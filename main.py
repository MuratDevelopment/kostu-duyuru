import os, requests, time
import pymongo
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import mongotypes

token = os.getenv('TELEGRAMTOKEN')
mongo = os.getenv('MONGODB')

print(f'Telegram token: {token}')
print(f'Mongo URI: {mongo}')

dbclient = pymongo.MongoClient(mongo)
print(f'Database: {dbclient.collection_name}')
db = dbclient["kostu"]
annnouncementdb = db["announcements"]
usersdb = db["users"]
olddb = db['oldanc']

async def subscribe(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    usercheck = usersdb.find_one({"name": update.message.from_user.username})
    print(usercheck)
    if len(usercheck) > 0:
        await update.message.reply_text(f'Zaten abonesiniz.\nYou are already subscribed')
    else:
        usersdb.insert_one(mongotypes.UserType(update.message.chat_id, update.message.from_user.username))
        await update.message.reply_text(f'KOSTÜ Duyurularına abone olundu.\nSubscribed to the KOSTÜ announcements')

async def unsubscribe(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    user = usersdb.find_one({"chat_id":update.message.chat_id})
    if user:
        usersdb.delete_one(user)
        await update.message.reply_text('KOSTÜ Duyuru kanalından aboneliğinizi kaldırdınız.\n\nUnsubscibed from the KOSTÜ Announcements channel.')
    else:
        await update.message.reply_text('Aboneliğiniz bulunmadı, bir değişiklik yapılmadı.\n\nYour subscription was not found, no changes were made.')

async def start(update: Update, context:ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.chat.send_message('KOSTÜ Duyuru Kanalına hoşgeldiniz.\nKanala abone olmak için /subscribe komutunu kullanın.\n\nWelcome to the KOSTÜ Announcements channel\nTo subscribe to the channel use the command /subscribe')

def checkNewAnnouncements():
    newanc=[]
    anc = annnouncementdb.find()
    for a in anc:
        if olddb.find_one({"announcement_id": a}):
            pass
        else:
            newanc.insert(annnouncementdb.find_one({"announcement_id": a}))
        
def sendAnnouncementsToSubs(anc):
    users = usersdb.find()
    for user in users:
        for a in anc:
            send_message(user.chat_id, a.content)


def announcementPolling():
    newanc = checkNewAnnouncements()
    if len(newanc) > 0:
        sendAnnouncementsToSubs(newanc)

    

def send_message(chat_id: str, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    requests.get(url)

app = ApplicationBuilder().token(token).build()
app.add_handler(CommandHandler('subscribe', subscribe))
app.add_handler(CommandHandler('unsubscribe', unsubscribe))
app.add_handler(CommandHandler('start', start))
while True:
    try:
        app.run_polling()
        announcementPolling()
    except Exception as e:
        print(f"Error while getting updates: {e}")
        time.sleep(5)  # Sleep for 5 seconds before retrying