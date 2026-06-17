import discord


WEBHOOK_NAME = (
    "Word Replacer"
)


_cache = {}


class MissingWebhookPermissions(
    Exception
):
    pass


async def check_permissions(
    channel
):

    guild = (
        channel.guild
    )

    me = (
        guild.me
        or
        guild.get_member(
            guild._state.user.id
        )
    )

    perms = (
        channel.permissions_for(
            me
        )
    )

    required = [

        perms.manage_webhooks,
        perms.manage_messages,
        perms.send_messages,
        perms.read_message_history

    ]

    if (
        not all(
            required
        )
    ):

        raise (
            MissingWebhookPermissions(
                "Missing permissions"
            )
        )


async def resolve_channel(
    channel
):

    if isinstance(
        channel,
        discord.Thread
    ):

        if (
            channel.parent
        ):

            return (
                channel.parent,
                channel.id
            )

    return (
        channel,
        None
    )


async def get_or_create_webhook(
    channel
):

    channel, thread_id = (
        await resolve_channel(
            channel
        )
    )

    await check_permissions(
        channel
    )

    key = (
        str(
            channel.id
        )
    )

    if key in _cache:

        return (
            _cache[key],
            thread_id
        )

    hooks = (
        await channel.webhooks()
    )

    webhook = next(

        (

            w

            for w

            in hooks

            if (
                w.user
                and
                w.user.bot
            )

        ),

        None

    )

    if (
        webhook
        is None
    ):

        webhook = (
            await channel.create_webhook(
                name=WEBHOOK_NAME
            )
        )

    _cache[
        key
    ] = webhook

    return (
        webhook,
        thread_id
    )


def clear_webhook_cache(
    channel_id=None
):

    if (
        channel_id
        is None
    ):

        _cache.clear()

        return

    _cache.pop(
        str(
            channel_id
        ),
        None
    )


async def send_as_user(

    webhook,

    message,

    content,

    username,

    avatar

):

    kwargs = {

        "content":
        content,

        "username":
        username,

        "avatar_url":
        avatar,

        "allowed_mentions":
        discord.AllowedMentions.none()

    }

    if isinstance(
        message.channel,
        discord.Thread
    ):

        kwargs[
            "thread"
        ] = (
            message.channel
        )

    await webhook.send(
        **kwargs
    )
