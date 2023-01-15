import ssl

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from pymongo import MongoClient
from datetime import datetime

cluster = MongoClient("mongodb+srv://bd:bd@chatbottest.vlhgqzs.mongodb.net/?retryWrites=true&w=majority")
db = cluster["cafe"]
users = db["users"]
orders = db["orders"]

app = Flask(__name__)


@app.route("/", methods=["get", "post"])
def reply():
    text = request.form.get("Body")
    number = request.form.get("From")
    number = number.replace("whatsapp:", "")
    res = MessagingResponse()
    user = users.find_one({"number": number})
    if bool(user) == False:
        res.message("Hi und herzlich Willkommen im baaila Cafe. \nDu kannst aus den folgenden Optionen auswählen: \n\n *Optionen* \n\n 1️⃣ *Telefonnummer anzeigen* \n 2️⃣ *Tisch reservieren* \n 3️⃣ *Öffnungszeiten ansehen* \n 4️⃣ *Adresse anzeigen*" )
        users.insert_one({"number": number, "status": "main", "messages": []})
    elif user["status"] == "main":
        try:
            option = int(text)
        except:
            res.message("Bitte entscheide dich für eine mögliche Antwort.")
            return str(res)
        if option == 1:
            res.message("1153131551")
        elif option == 2:
            res.message("Für wann möchtest du einen Tisch reservieren?")
            users.update_one({"number": number}, {"$set": {"status": "ordering"}})
            res.message(datetime.today().strftime('%Y-%m-%d'))
        elif option == 3:
            res.message("Wir haben Donnerstag bis Sonntag von 9:00 bis 22:00 geöffnet. :) Freitag und Samstags auch mal 1-2 Stunden länger.")
        elif option == 4:
            res.message("Du findest uns direkt hier am Fuße der Burg:\nBurgstraße 12\n63755 Alzenau")
        else:
            res.message("Bitte entscheide dich für eine mögliche Antwort.")
            return str(res)
    elif user["status"] == "ordering":
        try:
            option = int(text)
        except:
            res.message("Bitte entscheide dich für eine mögliche Antwort.")
            return str(res)
        if option == 0:
            users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})
            res.message("Hi und herzlich Willkommen zurück im baaila Cafe. \nDu kannst aus den folgenden Optionen auswählen: \n\n *Optionen* \n\n 1️⃣ *Telefonnummer anzeigen* \n 2️⃣ *Tisch reservieren* \n 3️⃣ *Öffnungszeiten ansehen* \n 4️⃣ *Adresse anzeigen*")
        elif 1<= option <= 5:
            cakes = ["Kuchen 1", "kuchen 2", "cupacke", "zimtschnecke", "sonstiges"]
            selected = cakes[option-1]
            users.update_one({"number": number}, {"$set": {"status": "address"}})
            users.update_one({"number": number}, {"$set": {"item": selected}})
            res.message("Gute Wahl !")
            res.message("Please enter your address to confirm the order")
        else:
            res.message("bitte gib eine mögliche antwort ein")
    elif user["status"] == "address":
        selected = user["item"]
        res.message("Gute Wahl")
        res.message(f"Deine Bestellung für {selected} ist angekommen und wird in der nächsten Stunde ausgeliefert")
        orders.insert_one({"number": number, "item": selected, "address": text, "order_time": datetime.now()})
        users.update_one({"number": number}, {"$set": {"status": "ordered"}})
    elif user["status"] == "ordered":
        res_message("Hi und herzlich Willkommen zurück im baaila Cafe. \nDu kannst aus den folgenden Optionen auswählen: \n\n *Optionen* \n\n 1️⃣ *Telefonnummer anzeigen* \n 2️⃣ *Tisch reservieren* \n 3️⃣ *Öffnungszeiten ansehen* \n 4️⃣ *Adresse anzeigen*")
        users.update_one({"number": number}, {"$set": {"status": "main"}})
    users.update_one({"number": number}, {"$push": {"messages": {"text": text, "date": datetime.now()}}})

    return str(res)


if __name__ == "__main__":
    app.run()
