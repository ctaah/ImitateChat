import discord
import asyncio
import time

TOKEN = "" # Your discord bot token
SOURCE_CHANNEL_ID = 1305654769477746779  # Source channel ID  | Channel you want to move the conversation FROM
TARGET_CHANNEL_ID = 1308419156399620136  # Target Channel ID | Channel you want to move the conversation INTO
ACTION_DELAY = 4  # Delay for each action batch. Made to obey the API law, lol.

intents = discord.Intents.all()
intents.message_content = True
client = discord.Client(intents=intents)

async def fetch_and_replay_messages():
    await client.wait_until_ready()
    source_channel = client.get_channel(SOURCE_CHANNEL_ID)
    target_channel = client.get_channel(TARGET_CHANNEL_ID)

    if not source_channel or not target_channel:
        print("Source or target channel not found!")
        return
    messages = []
    async for message in source_channel.history(limit=None, oldest_first=True):
        messages.append(message)

    webhooks = {}
    for member in source_channel.members:
        if member.id not in webhooks:
            webhook = await target_channel.create_webhook(name=member.display_name)
            webhooks[member.id] = webhook
            print(f"Created webhook for {member.display_name}")

    total_actions = len(messages) * 3
    total_time = total_actions * ACTION_DELAY
    print(f"Total messages: {len(messages)}")
    print(f"Estimated completion time: {total_time // 60} minutes {total_time % 60} seconds")

    for message in messages:
        try:
            if not message.content and not message.attachments:
                continue

            if message.author.id not in webhooks:
                webhook = await target_channel.create_webhook(name=message.author.display_name)
                webhooks[message.author.id] = webhook
                print(f"Created webhook for {message.author.display_name}")
            else:
                webhook = webhooks[message.author.id]
            avatar_url = message.author.avatar.url if message.author.avatar else None

            if message.content:
                await webhook.send(
                    content=message.content,
                    username=message.author.display_name,
                    avatar_url=avatar_url,
                )

            for attachment in message.attachments:
                await webhook.send(
                    content=None,
                    file=await attachment.to_file(),
                    username=message.author.display_name,
                    avatar_url=avatar_url,
                )

            print(f"Sent message from {message.author.display_name}")
            await asyncio.sleep(ACTION_DELAY)

        except Exception as e:
            print(f"Error handling message {message.id}: {e}")

    print("Finished replaying messages.")
    await client.close()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await fetch_and_replay_messages()

client.run(TOKEN)
