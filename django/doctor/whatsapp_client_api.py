import json
import requests
from django.conf import settings


class WABot:
    def __init__(self):

        self.APIUrl = settings.API_URL
        self.token = settings.TOKEN
        self.accountStatusActive = False

        client_status_response = self.get_status_of_client(True, True)
        if client_status_response['accountStatus'] == 'authenticated':
            self.accountStatusActive = True

    # To make a POST request
    def send_requests(self, method, data):
        url = f"{self.APIUrl}{method}?token={self.token}"
        print("url = ", url)
        headers = {'Content-type': 'application/json'}
        answer = requests.post(url, data=json.dumps(data), headers=headers)
        print("answer = ", answer)
        return answer.json()

    # To make a GET request
    def get_requests(self, method, data):
        url = f"{self.APIUrl}{method}?token={self.token}"
        print("url = ", url)
        headers = {'Content-type': 'application/json'}
        answer = requests.get(url, data=json.dumps(data), headers=headers)
        print("answer = ", answer)
        return answer.json()

    # Get the account status and QR code for authorization ## GET
    def get_status_of_client(self, full=False, no_wakeup=False):
        data = {
            "full": full,
            "no_wakeup": no_wakeup
        }
        answer = self.get_requests('status', data)
        return answer

    # send messages by phone number, eg : phone = "+919895691004" ## POST
    def send_message_by_phone(self, phone, text):
        response = False
        if self.accountStatusActive:
            data = {
                "phone": phone,
                "body": text
            }

            answer = self.send_requests('sendMessage', data)
            if answer:
                if answer['sent']:
                    response = True
            return response
        else:
            return "client is not authenticated"

    # send messages by phone number, eg : chat_id = "919895691004@c.us" ## POST
    def send_message_by_chat_id(self, chatId, text):
        if self.accountStatusActive:
            response = False
            data = {
                "chatId": chatId,
                "body": text
            }

            answer = self.send_requests('sendMessage', data)
            if answer:
                if answer['sent']:
                    response = True
            return response
        else:
            return "client is not authenticated"

    # Direct link to QR-code in the form of an image, not base64 ## GET
    def get_qr_code(self):
        if not self.accountStatusActive:
            method = "qr_code"
            url = f"{self.APIUrl}{method}?token={self.token}"
            answer = requests.get(url)
            response_body = answer.content
            qr_path = settings.MEDIA_ROOT + '/' + 'qr_code_{}.png'.format(self.token)
            fd = open('{}'.format(qr_path), 'wb')
            fd.write(response_body)
            fd.close()
            file_path = 'media/qr_code_{}.png'.format(self.token)
            return file_path
        else:
            return "Client already registered! please logout first to display QR code."

    # Logout from WhatsApp Web to get new QR code ## POST
    def logout(self):
        if self.accountStatusActive:
            answer = self.send_requests('logout', data={})
            if answer:
                return answer['result']
            else:
                return "client is not authenticated"
        else:
            return "client is not authenticated"

    # Updates the QR code after its expired ## POST
    def expire_qr_code(self):
        answer = self.send_requests('expiry', data={})
        return answer

    # Repeat the manual synchronization attempt with the device ## POST
    def repeat_sync(self):
        if self.accountStatusActive:
            answer = self.send_requests('retry', data={})
            return answer
        else:
            return "client is not authenticated"

    # Reboot WhatsApp Instance ## POST
    def reboot(self):
        if self.accountStatusActive:
            answer = self.send_requests('reboot', data={})
            if answer:
                return answer['success']
            else:
                return "client is not authenticated"
        else:
            return "client is not authenticated"

    # Returns the active session if the device has connected another instance of Web WhatsApp ## POST
    def take_over(self):
        if self.accountStatusActive:
            answer = self.send_requests('takeover', data={})
            return answer
        else:
            return "client is not authenticated"

    # Get the chat list ## GET
    def get_all_chats(self):
        if self.accountStatusActive:
            answer = self.get_requests('dialogs', data={})
            return answer
        else:
            return "client is not authenticated"

    # Get info about group/dialog. ## GET
    def get_a_chat(self, chatId=None):
        if self.accountStatusActive:
            data = {
                'chatId': chatId,
            }
            answer = self.get_requests('dialog', data=data)
            return answer
        else:
            return "client is not authenticated"

    # Get a list of messages. ## GET
    def get_all_messages(self, lastMessageNumber=0, last=False, chatId=None, limit=100, min_time=0, max_time=0):
        if self.accountStatusActive:
            return_array = []
            # url = "https://api.chat-api.com/instance195978/messages" # Princeton Data Center
            url = "https://api.chat-api.com/instance202617/messages"  # WizWatch Test
            headers = {'Content-type': 'application/json'}
            params = {
                'token': self.token,
                'lastMessageNumber': lastMessageNumber,
                'last': last,
                'chatId': chatId,
                'limit': limit,
                'min_time': min_time,
                'max_time': max_time,
            }
            answer = requests.get(url, params=params, headers=headers)
            if answer:
                json_response = answer.json()
                if json_response:
                    arr_msgs = json_response['messages'] or None
                    if arr_msgs:
                        for i in arr_msgs:
                            if 'body' and 'fromMe' and 'type' in i:
                                if i['type'] == 'chat' and not i['fromMe']:
                                    return_array.append(i['body'].upper())
                return return_array
        else:
            return "client is not authenticated"

    # Get a list of messages sorted by time descending ## GET
    def get_message_history(self, page=0, count=100, chatId=None):
        if self.accountStatusActive:
            return_array = []
            # url = "https://api.chat-api.com/instance195978/messagesHistory" # ehzaaan@gmail.com
            url = "https://api.chat-api.com/instance202617/messagesHistory"
            headers = {'Content-type': 'application/json'}
            params = {
                'page': page,
                'count': count,
                'chatId': chatId,
                'token': self.token,
            }
            answer = requests.get(url, params=params, headers=headers)
            if answer:
                json_response = answer.json()
                if json_response:
                    arr_msgs = json_response['messages'] or None
                    if arr_msgs:
                        for i in arr_msgs:
                            if 'body' and 'fromMe' and 'type' in i:
                                if i['type'] == 'chat' and not i['fromMe']:
                                    return_array.append(i['body'].upper())
                return return_array
        else:
            return "client is not authenticated"