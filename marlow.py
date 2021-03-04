import datetime
from sys import maxsize
import time
import groupy
import requests
import bs4

import groupy
from creds import ACCESS_TOKEN, BOT_ID, GROUP_ID

MARLOW_WHITE_MALE_URL = 'https://www.marlowwhite.com/male-officer-agsu-package'
MARLOW_WHITE_FEMALE_URL = 'https://www.marlowwhite.com/female-officer-agsu-package'

def grab_page(url):
    """
        Grabs HTML page from given URL and returns a BS4 object.
    """
    res = requests.get(MARLOW_WHITE_MALE_URL)
    soup = bs4.BeautifulSoup(res.content, 'html.parser')

    return soup

def is_agsu_available(soup):
    """
        Given a HTML page for a Marlow White uniform, returns True if uniform available, else False.
    """
    avail_block = soup.find("div",class_="product-info-stock-sku")

    avail_span = avail_block.find("span").text

    return avail_span != 'Out of stock'

def format_message():
    """
        Returns a formatted string with the information the bot should send.
    """

    male_string = 'OUT OF ORDER' if not is_agsu_available(grab_page(MARLOW_WHITE_MALE_URL)) else f'May be in stock - page has changed. Check {MARLOW_WHITE_MALE_URL}'
    female_string = 'OUT OF ORDER' if not is_agsu_available(grab_page(MARLOW_WHITE_FEMALE_URL)) else f'May be in stock - page has changed. Check {MARLOW_WHITE_FEMALE_URL}'

    return f'Status:\nMale AGSU: {male_string}\nFemale AGSU: {female_string}'

# BOT STUFF


if __name__ == '__main__':
    client = groupy.Client.from_token(ACCESS_TOKEN)

    group = client.groups.get(GROUP_ID)

    # initialize
    last_message = group.messages.list()[0] # most recent message
    last_updated = datetime.date.today() - datetime.timedelta(days=1) # yesterday

    while True:

        # definitely post status every day
        can_update_today = datetime.date.today() > last_updated
        after_nine = datetime.datetime.now().time().hour >= 9
        
        if (can_update_today and after_nine):
            msg = format_message()
            client.bots.post(BOT_ID, msg)
            last_message = group.messages.list()[0]
            last_updated = datetime.date.today()

        # scan recent messages for mentions
        recent_messages = group.messages.list_after(last_message.id)


        # cannot mention bots so pause on this for now:
        # for message in recent_messages:
        #     for attachment in message.attachments:
        #         if type(attachment) == groupy.api.attachments.Mentions:
        #             for user_id in attachment.user_ids:
        #                 pass

        for message in recent_messages:
            if '!marlow' in message.text:
                msg = format_message()
                client.bots.post(BOT_ID, msg)
                last_message = group.messages.list()[0]
                last_updated = datetime.date.today()

        time.sleep(1) # second-long loop