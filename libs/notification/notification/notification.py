from .config import API_KEY, SUPPORT_EMAIL
import requests
import json


import aiohttp
import asyncio


async def send_email(to_email, subject, text):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "from": {
            "email": SUPPORT_EMAIL
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "subject": subject,
        "text": text
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            return response.status

async def send_template_email(to_email, template_id, template_data):
    url = "https://api.mailersend.com/v1/email"

    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Authorization": f"Bearer {API_KEY}"
    }

    data = {
        "from": {
            "email": SUPPORT_EMAIL
        },
        "to": [
            {
                "email": to_email
            }
        ],
        "template_id": template_id,
        "variables": template_data
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(data)) as response:
            return response.status