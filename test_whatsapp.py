from database.models import send_whatsapp_reminders

phone_numbers = [
    "212720735797",
    "212634430010",
    "212714799726",
    "212678167558",
    "212607256677"
]

send_whatsapp_reminders(phone_numbers)
