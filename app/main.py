import requests
import json
import time
from datetime import datetime as dt

#Zammad
zammad_url = "http://WWW.ZAMMAD.EXAMPLE.COM/api/v1"
zammad_token = "ZAMMAD_TOKEN"

#Nextcloud Talk
nextcloud_talk_url = "https://NEXTCLOUD.EXAMPLE.COM/ocs/v2.php/apps/spreed/api/v1/chat"
nextcloud_talk_room_id = "ID_CHATROOM"
nextcloud_talk_username = "USERNAME"
nextcloud_talk_password = "PASSWORD"


def send_to_nextcloud_talk(ticket_id, ticket_subject, ticket_date):
    try:
        payload = {
            "message": f"`*****🛎️✨📬 Neues Ticket ******` \n\nTicket ID: {ticket_id}\nSubject: {ticket_subject}\n{ticket_date}\n\n\n"
        }

        headers = {
            "Content-Type": "application/json",
            "OCS-APIRequest": "true",
            "accept": "application/json, text/plain, /"
        }

        session = requests.Session()
        session.auth = (nextcloud_talk_username, nextcloud_talk_password)

        response = session.post(f"{nextcloud_talk_url}/{nextcloud_talk_room_id}", data=json.dumps(payload), headers=headers)
        print(f'Status Code: {response.status_code}, Content: {response.json()}')

        if response.status_code == 200:
            print("Message sent to Nextcloud Talk successfully.")
        else:
            print(f"Failed to send message to Nextcloud Talk. Status Code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_all_zammad_tickets():
    all_tickets = [] # leer list
    page = 1

    while True:
        response = requests.get(f"{zammad_url}/tickets?page={page}", headers={"Authorization": f"Token token={zammad_token}"})
        
        if response.status_code == 200:
            tickets = response.json()
            if not tickets:
                return all_tickets # return the list of all tickets
            all_tickets.extend(tickets) # add the tickets in list
            page += 1
        else:
            print(f"Failed to get tickets from Zammad. Status code: {response.status_code}")
            return None

def is_same_ticket(ticket1, ticket2):
    if ticket1 is None or ticket2 is None:
        return False
    return ticket1["number"] == ticket2["number"] and ticket1["title"] == ticket2["title"] and ticket1["created_at"] == ticket2["created_at"]

if __name__ == "__main__":
    last_sent_ticket = None
    while True:
        all_tickets = get_all_zammad_tickets()
        if all_tickets:
            latest_ticket = all_tickets[-1] # get last ticket in list
            if not is_same_ticket(latest_ticket, last_sent_ticket):
                ticket_id = latest_ticket["number"]
                ticket_subject = latest_ticket["title"]
                ticket_date = dt.strptime(latest_ticket["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
                send_to_nextcloud_talk(ticket_id, ticket_subject, ticket_date)
                last_sent_ticket = latest_ticket
            else:
                print("The latest ticket is already sent.")
        else:
            print("No new ticket to send.")
            break
            
        #Zeit/Time
        time.sleep(10)
