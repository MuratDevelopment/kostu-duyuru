import time

def AnnouncementType(annoucement_id,title, content, contentdate):
    return {
        "announcement_id": annoucement_id,
        "title": title,
        "content": content,
        "contentdate": contentdate,
        "creation_date": time.time()
    }

def UserType(chat_id, name):
    return {
        "chat_id": chat_id,
        "name": name
    }

def oldAnnoucementType(announcement_id):
    return {
        "announcement_id": announcement_id
    }