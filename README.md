# [@kaznadc_bot](http://t.me/kaznadc_bot) kaznadc-telegram-bot
Telegram Bot, which will help Kazakhstan National Doping Committee to track their athletes.

Currently, KazNADC does not have any professional tools to gather this information and athletes do not have any tools to always provide it. Consequently, KazNADC ban those athletes, who stop providing any information and as a result, they cannot participate in Olympic Games. Moreover, not many athletes are acquainted with the list of forbidden substances, so they suffer from KazNADC’s punishment actions.

## How to use it?
Press ```/start``` to start using the bot
Press ```/cancel``` if bot is not responding

**Note!** If bot is not responding try to use ```/start``` as well

## Files and Code
There is one file which I didn't include in this repository, because it's a Certificate file written in .json. Also, in some lines of code there are no String values because they represent private TOKENs and Certificates.

## Code Snippets

### Getting User's phone number, name and id
```
def main():
        states = {
            REGISTER: [MessageHandler(Filters.contact, get_user_data, pass_user_data=True, pass_chat_data=True)], 
            ...
        },

        ...
    )
```

```
def get_user_data(bot, update, user_data, chat_data):
    phone_number = update.message.contact.phone_number
    first_name = update.message.contact.first_name
    user_id = str(update.message.contact.user_id)
    save_user_data(bot, update, phone_number, first_name, user_id)
    ...
```

### Getting User's location (latitude, longitude)
It works the same as with contact information
```
def main():
        states = {
            LOCATION: [MessageHandler(Filters.location, get_user_location, pass_user_data=True, pass_chat_data=True)], 
            ...
        },

        ...
    )
```

```
def get_user_location(bot, update, user_data, chat_data):
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    ...
```

### Using Firebase Realtime Database to save User's information
```
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("your certificate")

firebase_admin.initialize_app(cred, {
    'databaseURL': db_url
})
ref = db.reference('users')
```
This method will save previously got data into Firebase Realtime Database
```
def save_user_data(bot, update, phone_number, first_name, user_id):
    users_ref = ref.child(user_id)
    users_ref.update({
        'phone_number': phone_number,
        'first_name': first_name,
        'user_id': user_id
    })
```

## Hosting
Bot is being hosted on Heroku. It's 24/7 available
