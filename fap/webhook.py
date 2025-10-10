#!/usr/bin/python3

import logging

# await webhook_send(ctx, channel, user, embed=embed)

logger = logging.getLogger("red")

_webhook_dict = {}

async def get_channel_webhook(channel):
    full_channel_id = f'{channel.guild.id}-{channel.id}'
    webhook = _webhook_dict.get(full_channel_id)

    if webhook is None:
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.name == 'framehook':
                break
        else:
            webhook = await channel.create_webhook(name='framehook', reason='hook for framing')

        _webhook_dict[full_channel_id] = webhook

    return webhook

async def webhook_send(ctc, channel, user, message=None, embed=None, file=None):
    webhook = await get_channel_webhook(channel)

    # in discord.py/redbot, default for missing argument is not None, but a custom variable 'MISSING'
    # so we have to pass args trough a dict
    arguments_dict = {}
    if message:
        arguments_dict['content'] = message
    if file:
        arguments_dict['file'] = file
    if embed:
        arguments_dict['embed'] = embed

    # removed (NotFound, AttributeError) exception handling from here - there was a bug where webhook could lose a token (?) and it needed to be recreated, idk if it's still relevant
    return await webhook.send(
        **arguments_dict,
        username=user.display_name,
        avatar_url=user.display_avatar.url,
        wait=True
    )
