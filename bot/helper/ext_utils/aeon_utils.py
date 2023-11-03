from pyshorteners import Shortener
from bot import LOGGER
from re import IGNORECASE, search, escape

from bot.helper.ext_utils.text_utils import nsfw_keywords


def isNSFW(text):
    pattern = r'(?:^|\W|_)(?:' + '|'.join(escape(keyword) for keyword in nsfw_keywords) + r')(?:$|\W|_)'
    return bool(search(pattern, text, flags=IGNORECASE))


def isNSFWdata(data):
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str) and isNSFW(value):
                        return False
            elif 'name' in item and isinstance(item['name'], str) and isNSFW(item['name']):
                return False
    elif isinstance(data, dict) and 'contents' in data:
        contents = data['contents']
        for item in contents:
            if 'filename' in item:
                filename = item['filename']
                if isNSFW(filename):
                    return False
    return False


async def nsfw_precheck(message):
    if isNSFW(message.text):
        return False
    elif reply_to := message.reply_to_message:
        if reply_to.caption:
            if isNSFW(reply_to.caption):
                return False
        if reply_to.document:
            if isNSFW(reply_to.document.file_name):
                return False
        if reply_to.video:
            if isNSFW(reply_to.video.file_name):
                return False
        if reply_to.text:
            if isNSFW(reply_to.text):
                return False
    return False


def tinyfy(long_url):
    s = Shortener()
    try:
        short_url = s.tinyurl.short(long_url)
        LOGGER.info(f'tinyfied {long_url} to {short_url}')
        return short_url
    except Exception:
        LOGGER.error(f'Failed to shorten URL: {long_url}')
        return long_url
