import asyncio
import logging
import json
import random
import os
import httpx

from PIL import Image, ImageColor
from io import BytesIO
from typing import Optional

import discord
from redbot.core import Config, checks, commands
from redbot.core.bot import Red
from redbot.core.commands import Cog
from redbot.core.utils.chat_formatting import pagify

from .buffer import dprint, buffempty, dsend
from .rembed import create_reply_embed_from_ref, \
                    create_reply_embed, \
                    fetch_message_from_link, \
                    fetch_message_from_reference

from .webhook import webhook_send
from .letters import mapfont
from .render_gallery import render_gallery

logger = logging.getLogger("red")


def find_matches(pattern, filelist):
    plength = len(pattern)
    return [ match for match in filelist if pattern == match[:plength] ]


def file_extension(filename):
    if '.' not in filename:
        return None

    split = filename.split('.')
    if len(split) == 1:
        return None

    ext = split[-1]
    if not 3 <= len(ext) <= 4:
        return None

    return ext


# @todo: get rid of this function
async def _check_channel_permissions(ctx, channel: discord.TextChannel):
    if not channel.permissions_for(ctx.author).send_messages:
        await ctx.send('You don\'t have permissions to send messages in that channel ')
        return False

    if not channel.permissions_for(ctx.me).send_messages:
        await ctx.send('I don\'t have permissions to send messages in that channel.')
        return False

    return True


# @todo: this will have to be linked to guild somehow..
DISGUST = '<:kurumDisgust:973260944593530991>'
STARE = '<:kurumStare:973260945260433408>'
WOW = '<:kurumWow:973260945667268700>'
KAZ_SALUT = '<:kazSalut:936613010062049360>'

class fap(Cog):
    """
    F4P utils
    """

    def __init__(self, red: Red):
        super().__init__()
        self.bot = red

        # TODO:
        # loading setting - probably do it at start,
        # load reddata name from there
        # if there is no reddata dirname in settings, ask user for that

        home = self.home = os.environ['HOME']

        # cat files directory
        # XXX: store it in fap dir?? probably shitty idea but idk
        self.fap_files = home + '/.fap-files'
        self.reddata = self.fap_files + '/reddata'
        self.todos = self.fap_files + '/todos'

        for path in [ self.fap_files, self.reddata, self.todos ]:
            if not os.path.isdir(path):
                os.mkdir(path)

        self.fap_location = os.path.dirname(os.path.realpath(__file__))

        self.cat_cache = {}
        self.loadable_extensions = set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4'])


    # XXX: some checks here?
    async def _fetch_message(self, guildid, channelid, messageid):
        guild = self.bot.get_guild(int(guildid))
        channel = guild.get_channel(int(channelid))
        return await channel.fetch_message(int(messageid))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if message.author.bot:  # @todo: change to check if self ?
                return

            # insult a user; @todo: later do it only if some setting is up
            mentions = message.mentions
            if len(mentions) == 1 and mentions[0].id == self.bot.user.id:
                await self.insult_user(message.channel)
        except Exception as e:
            await message.channel.send(f'FUCKING SHIT REEEE: {e}')

    async def insult_user(self, channel, user=None):
        async with httpx.AsyncClient() as client:
            response = await client.get('https://evilinsult.com/generate_insult.php')

        if user != None:
            await channel.send(f'{user.mention} {response.text}')
        else:
            await channel.send(response.text)
        await channel.send(DISGUST)

    @commands.admin()
    @commands.group(name='d')
    async def dev(self, ctx):
        """Misc commands useful for development"""
        pass

    @dev.command(name='buffempty')
    async def fap_buffempty(self, ctx):
        await dsend(ctx.channel)

    @dev.command(name='ping')
    async def fap_ping(self, ctx):
        """fap ping to verify if fap loaded and working"""
        await ctx.channel.send('pong')

    @dev.command(name='clearhooks')
    async def fap_clearhooks(self, ctx):
        for channel in ctx.guild.text_channels:
            if not channel.permissions_for(ctx.me).manage_webhooks:
                continue

            webhooks = await channel.webhooks()
            if not webhooks:
                continue

            dprint('deleted webhooks:')
            for webhook in webhooks:
                dprint(webhook.name)
                asyncio.create_task(webhook.delete())

            await dsend(ctx.channel)


    @dev.command(name='listhooks')
    async def fap_listhooks(self, ctx):
        webhooks = await ctx.channel.webhooks()
        if not webhooks:
            await ctx.channel.send('no webhooks here')
            return

        dprint('webhooks in current channel:')
        for webhook in webhooks:
            dprint('> webhook: `', webhook, '` name: `', webhook.name, '`', sep='')

        await dsend(ctx.channel)


    @dev.command(name='thing')
    async def fap_thing(self, ctx):
        """
        does the thing
        I always used it as a testing command..
        """
        pass


    ## low effort useless commands
    #
    @commands.guild_only()
    @commands.command(name='whoami')
    async def fap_who(self, ctx):
        """Sends your username"""
        user = ctx.message.author
        await ctx.send(user)


    @commands.guild_only()
    @commands.command(name='addfav')
    async def fap_addfav(self, ctx):
        """Add to favorite"""
        user = ctx.message.author
        await ctx.send(f'{user.mention} added it to his favorites!')


    @commands.command(name='crazy')
    async def fap_crazy(self, ctx, how_much_crazy: Optional[int] = 10):
        """I was crazy once"""
        
        crazy = """𝘪 𝘸𝘢𝘴 𝘤𝘳𝘢𝘻𝘺 𝘰𝘯𝘤𝘦
        𝘵𝘩𝘦𝘺 𝘭𝘰𝘤𝘬𝘦𝘥 𝘮𝘦 𝘪𝘯 𝘢 𝘳𝘰𝘰𝘮
        𝘢 𝘳𝘶𝘣𝘣𝘦𝘳 𝘳𝘰𝘰𝘮
        𝘢 𝘳𝘶𝘣𝘣𝘦𝘳 𝘳𝘰𝘰𝘮 𝘸𝘪𝘵𝘩 𝘳𝘢𝘵𝘴
        𝘢𝘯𝘥 𝘵𝘩𝘦𝘺 𝘮𝘢𝘥𝘦 𝘮𝘦 𝘤𝘳𝘢𝘻𝘺
        𝘤𝘳𝘢𝘻𝘺 ?""".splitlines()
      
        await ctx.send('𝘤𝘳𝘢𝘻𝘺 ?')
        for _ in range(how_much_crazy):
            for line in crazy:
                await asyncio.sleep(1)
                await ctx.send(line)


    @commands.command(name='insult')
    async def fap_insult(self, ctx, user: discord.Member):
        """Insult a user <:kekwPatkekw:1107697748964298872>"""
        await self.insult_user(ctx.channel, user)


    ## somewhat useful commands
    #
    @commands.command(name='colorcode')
    async def fap_colorcode(self, ctx, *, color: str):
        """usage: &colorcode #696969"""
        if color[:3] != 'rgb' and color[0] != '#' and color not in ImageColor.colormap:
            color = '#' + color
        try:
            img = Image.new("RGB", (50,50), color)
        except ValueError:
            await ctx.send("Incorrect value")
            return
        imgbytes = BytesIO()
        img.save(imgbytes, format="PNG")
        imgbytes.seek(0)
        await ctx.send(file = discord.File(imgbytes, filename='image.png'))


    # @todo: maybe move it to a separate cog
    def _todo_usage_message(self, message):
        return message + '\nusage: &todo, &todo add your_todo..., &todo del <number>'

    async def _list_todos(self, todo_lines, channel, filter=None):
        if len(todo_lines) == 0:
            await channel.send('empty ' + WOW)
            return
        found_length = 0
        dprint('TODO:')
        for i, line in enumerate(todo_lines, 1):
            if filter is not None and filter.lower() not in line.lower() and str(i) != filter:
                continue
            found_length += 1
            index = f' {i}' if i <= 9 else i
            dprint(index, line)
            continue
        await dsend(channel, code=True)    #
        if found_length == 0:              # another reason why buffer should have code in print
            await channel.send('empty ' + WOW) #


    # @todo: maybe embed output of this
    # @todo: maybe remove add argument, automatically add all arguments when no known argument 
    @commands.command(name='todo')
    async def fap_todo(self, ctx, *, args = None):
        '''
        todo <:peepoWeird:932638116865511464>

        &todo
        &todo add your_todo...
        &todo del <number> [number2, ...]
        &todo filter <some_words>
        '''

        todo_file = f'{self.todos}/{ctx.author.id}'
        if not os.path.isfile(todo_file):
            with open(todo_file, 'w') as f:
                pass  # create if doesnt exist
        with open(todo_file, 'r') as f:
            todo_file_content = f.read().split('\n')[:-1]

        if args == None:
            return await self._list_todos(todo_file_content, ctx.channel)
        args = args.split()

        if args[0] == 'list':
            return await self._list_todos(todo_file_content, ctx.channel)

        if args[0] == 'filter':
            filter = ' '.join(args[1:]) if len(args) >= 2 else None
            return await self._list_todos(todo_file_content, ctx.channel, filter)

        if args[0] == 'add':
            with open(todo_file, 'a') as f:
                f.write(' '.join(args[1:]) + '\n')
                return await ctx.send('appended')

        if args[0] == 'del' or args[0] == 'done':
            arguments, indexes = args[1:], []
            for number in arguments:
                if not number.isnumeric():
                    return await ctx.send(self._todo_usage_message(
                        f'number has to be a number! and *{number}* is not {DISGUST}'))
                index = int(number) - 1
                if index < 0:
                    return await ctx.send(self._todo_usage_message('number is less than one ' + STARE))
                if index > len(todo_file_content) - 1:
                    await ctx.send(f"there's no todo with {index} number")
                    if len(todo_file_content) == 1:
                        return
                    return await self._list_todos(todo_file_content, ctx.channel)
                indexes.append(index)
            
            removed_todos = [ todo_file_content.pop(i) for i in sorted(indexes, reverse=True) ]

            with open(todo_file, 'w') as f:
                if len(todo_file_content) != 0:
                    f.write('\n'.join(todo_file_content)+'\n')

            if removed_todos == [''] or len(removed_todos) == 0:  # not really sure if this still can happen
                return await ctx.send('list was empty')
            for x in removed_todos:
                await ctx.send(f'`{x}` done!')
            return

        await ctx.send(self._todo_usage_message(f'there is no *{args[0]}* option'))


    # TODO: reply to multiple commands
    # &reply [link] [+5]/[-5] 
    # &reply [link] [link] - range?
    @commands.command(name='reply')
    async def fap_reply(self, ctx, author_in_title: Optional[bool] = True, link=None):
        """reply to a message

        author_in_title: yes, y, 1, enabled / no, n, 0, disabled"""

        ref = ctx.message.reference
        if ref != None:
            asyncio.create_task(ctx.message.delete())
            embed = await create_reply_embed_from_ref(ctx.channel, ref, author_in_title)
            await ctx.channel.send(embed=embed)
            return

        if link == None:
            await ctx.channel.send('Provide link or reply to something')
            return

        msg = await fetch_message_from_link(ctx, link)
        if msg == None:
            return

        asyncio.create_task(ctx.message.delete())
        embed = create_reply_embed(msg, link, author_in_title)
        await ctx.channel.send(embed=embed)
        return

    @commands.command(name='show_reply')
    async def fap_show_reply(self, ctx, link=None):
        """show reply message is replying to"""

        ref = ctx.message.reference
        if ref != None:
            msg = await fetch_message_from_reference(ref, ctx)
            original_reply_ref = msg.reference
            if original_reply_ref == None:
                await ctx.channel.send("Message you've replied to doesn't reply to anything")
                return
            # asyncio.create_task(ctx.message.delete())
            embed = await create_reply_embed_from_ref(ctx.channel, original_reply_ref)
            await ctx.channel.send(embed=embed)
            return

        if link == None:
            await ctx.channel.send('Provide link or reply to something')
            return

        msg = await fetch_message_from_link(ctx, link)
        if msg == None:
            return

        original_reply_ref = msg.reference
        if original_reply_ref == None:
            await ctx.channel.send("Message you've linked to doesn't reply to anything")
            return

        # asyncio.create_task(ctx.message.delete())
        embed = await create_reply_embed_from_ref(ctx.channel, original_reply_ref)
        await ctx.channel.send(embed=embed)
        return


    # @todo: message attachments
    @commands.command(name='say')
    async def fap_say(self, ctx, channel: Optional[discord.TextChannel] = None, *, text):
        """Say something in channel"""

        # @todo:
        # * don't show this in logs
        # * this doens't work if in dm's..
        asyncio.create_task(ctx.message.delete())  

        channel = channel or ctx.channel
        channel_permission_check = await _check_channel_permissions(ctx, channel)
        if not channel_permission_check:
            return

        ref = ctx.message.reference

        if ref != None:
            # @todo: this doesnt work and fuck it
            await self._user_reply_to(ctx, channel, user, ref)

        await channel.send(text)


    async def _download_file_from_link(self, link, channel):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(link)
        except Exception as e:
            logger.info(f'user provided wrong link probably: {e}')
            return await channel.send(f"Couldn't download file from url: '{link}'")

        if r.status_code != 200:
            return await channel.send(f"Couldn't download file from url: '{link}' - Error {r.status_code}")

        # @todo: make usage of Content-Disposition filename
        logger.info(f'requested file has Content-Disposition: {r.headers.get("Content-Disposition")}')

        content_type = r.headers.get("content-type")
        if content_type is None:
            # @todo: maybe under such circumstances what should really happen is save and then run file command and maybe save
            return await channel.send(f"Are you trying to fuck with me? this file has no content type..")

        if content_type.startswith('image'):
            if '?' in link:
                link = link.split('?', 1)[0]

            filename = link.rsplit('/', 1)[1]

            if filename in os.listdir(self.reddata):
                return await channel.send(f'file "{filename}" already in reddata')

            await channel.send(f'saving `{filename}`..')

            try:
                with open(f'{self.reddata}/{filename}', 'wb') as f:
                    f.write(r.content)
            except Exception as e:
                logger.error(f'exception when saving in _download_file_from_link(): {e}')
                return await channel.send('Error happened when saving file from this link')
        else:
            return await channel.send(f"Unsupported content-type: {content_type}; we don't know how to behave here yet")


    def _rerender_gallery(self):
        render_gallery(self.reddata, f'{self.fap_files}/reddata_gallery.png', fontpath=self.fap_location + '/Iosevka-Medium.ttc')


    @commands.guild_only()
    @commands.command(name='rerender')
    async def fap_rerender(self, ctx):
        self._rerender_gallery()
        await ctx.send(file=discord.File(self.fap_files + '/reddata_gallery.png'))


    @commands.guild_only()
    @commands.command(name='cat_upload')
    async def fap_cat_upload(self, ctx, *, filelink=None):
        '''
        Upload a file for &cat command usage
        '''

        if len(ctx.message.attachments) == 0 and filelink is None:
            return await ctx.send("You're supposed to upload a file or provide an URL")

        if filelink is not None:
            try:
                await self._download_file_from_link(filelink, ctx.channel)
            except:
                logger.error(f'exception happened when running download_file_from_link(): {e}')
                await ctx.send('Error happened during file saving try')

        for file in ctx.message.attachments:
            filename = file.filename
            
            if '/' in filename:
                await ctx.send(
                    "I don't know how you did this but you're not allowed to do this ('/' in the filename)"
                )
                continue

            if filename in os.listdir(self.reddata):
                await ctx.send(f'file "{filename}" already in reddata, skipping')
                continue

            # @todo: convert to task
            await ctx.send(f'saving {filename}..')
            await file.save(f'{self.reddata}/{filename}')

        await ctx.send('done uploading!')
        self._rerender_gallery()
        

    # XXX: there is only one cache now, and it works bc in discord you can
    # actually leak your attachments,
    # but we might want to make  'server: channel: url'  cache
    def cat_cache_get(self, filename):
        return self.cat_cache.get(filename)


    # TODO: better reddata directory handling
    # TODO: add rm and add file commands (and change name probably)
    @commands.guild_only()
    @commands.command(name='cat')
    async def fap_cat(self, ctx, *, filename=None):
        """
        Concatenate file

        Use without filename to list all the files
        """

        if filename is None:
            files = os.listdir(self.reddata)
            if len(files) == 0:
                dprint('there are no files in reddata directory')
                dprint('use &reddata to to upload some')
                return await dsend(ctx.channel)

            return await ctx.send(file=discord.File(self.fap_files + '/reddata_gallery.png'))

        # make sure some HAXXOR won't succeed with his silly tricks
        if '..' in filename or '/' in filename:
            user = ctx.message.author
            file = discord.File(self.fap_location + '/400-pound-hacker.jpg',
                                filename='400-pound-hacker.jpg')
            return await ctx.send(f'found your picture {user.mention}', file=file)
            

        fullpath = self.reddata + '/' + filename

        if not os.path.isfile(fullpath):
            files = find_matches(filename, os.listdir(self.reddata))

            if len(files) == 0:
                await ctx.send('no such file in reddata directory')
                return

            if len(files) > 1:
                dprint('possible completions:')
                dprint('\n'.join(files))
                await dsend(ctx.channel)
                return

            filename = files[0]
            fullpath = self.reddata + '/' + filename

        user = ctx.message.author
        ref = ctx.message.reference

        asyncio.create_task(ctx.message.delete())

        if ref != None:
            await self._user_reply_to(ctx, ctx.channel, user, ref)

        url = self.cat_cache_get(filename)
        if url != None:
            await webhook_send(ctx, ctx.channel, user, message=url)
            return

        file = discord.File(fullpath, filename=filename)
        message = await webhook_send(ctx, ctx.channel, user, file=file)

        if file_extension(filename) in self.loadable_extensions:
            # added logging for debugging purposes - there's a bug where cached file may vanish
            # maybe it's related to removal of original message
            logger.info(f'&cat: caching file "{filename}" on "{message.guild.id}-{message.channel.id}-{message.id}"')
            self.cat_cache[filename] = message.attachments[0].url


    # TODO: prevent removed messages from appearing in logs
    @commands.guild_only()
    @commands.command(name='frame')
    async def fap_frame(self, ctx, member: discord.Member,
                        channel: Optional[discord.TextChannel] = None,
                        *, message=None):
        """My most useful tool"""

        if message == None:
            await channel.said('You forgot message content')
            return

        if channel != None:
            channel_permission_check = await _check_channel_permissions(ctx, channel)
            if not channel_permission_check:
                return
        else:
            channel = ctx.channel

        ref = ctx.message.reference
        asyncio.create_task(ctx.message.delete())

        # I won't accept people trying to frame me
        my_account = None
        if await self.bot.is_owner(member):
            my_account = member
            member = ctx.author

        if ref != None:
            await self._user_reply_to(ctx, channel, member, ref)

        await webhook_send(ctx, channel, member, message=message)

        if my_account != None:
            message = f'nice try {member.mention}'
            await webhook_send(ctx, channel, my_account, message=message)


    ## weeb commands
    @commands.command(name='waifu')
    async def fap_waifu(self, ctx, how_many_waifus: Optional[int] = 1,
                        category: Optional[str] = 'waifu'):
        '''
        random waifu for you <:kurumBlush:973260944270577674>

        use &waifu list to list categories
        '''

        categories = [ 'waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle',
                       'cry', 'hug', 'awoo', 'kiss', 'lick', 'pat', 'smug',
                       'bonk', 'yeet', 'blush', 'smile', 'wave', 'highfive',
                       'handhold', 'nom', 'bite', 'glomp', 'slap', 'kill',
                       'kick', 'happy', 'wink', 'poke', 'dance', 'cringe' ]

        category = category.lower()
        if category == 'list':
            for category in categories:
                dprint(category)
            await dsend(ctx.channel)
            return

        if category not in categories:
            await ctx.send('unknown category, please use &waifu list')
            return

        if how_many_waifus == 0:
            await ctx.send('sent 0 waifus!')
            return

        if how_many_waifus < 0:
            await ctx.send(f'deleting {-1*how_many_waifus} random waifus...')
            await asyncio.sleep(1)
            await ctx.send(f'done!')
            return

        if how_many_waifus > 50:
            await ctx.send("<:monkaMEGA:1026971851118878811>")
            await asyncio.sleep(1)
            await ctx.send("are you sick or something?")
            await asyncio.sleep(2)
            await ctx.send("I'm afraid discord servers won't endure "\
                           "this enormous horde of waifus")
            await asyncio.sleep(4)
            await ctx.send('...')
            await asyncio.sleep(1)
            await ctx.send('welp')
            await asyncio.sleep(1)
            await ctx.send('whatever')
            await asyncio.sleep(1)
            await ctx.send('gotta do your job')
            await asyncio.sleep(1)
            await ctx.send(f'sending {how_many_waifus} waifus to abyss...')

            wait_time = 3443 if how_many_waifus > 3442 else how_many_waifus
            await asyncio.sleep(wait_time)
            await ctx.send('done!')
            return

        if how_many_waifus > 5:
            await ctx.send("I'm really sorry but we can send only five waifus at once")
            how_many_waifus = 5


        for waifu in range(how_many_waifus):
            try:
                async with httpx.AsyncClient() as client:
                    waifu_json_object = await client.get('https://api.waifu.pics/sfw/' + category)

                waifu_url = json.loads(waifu_json_object.content.decode())['url']
            except Exception as e:
                dprint('error while trying to load waifu:')
                dprint(f'`{e}`')
                await dsend(ctx.channel)
                return

            # won't ever happen but that's probably what we should do since
            # sending empty str causes error, right?
            if waifu_url == '':
                await ctx.send('waifu turned out to be empty <:kurumWow:973260945667268700>')
                return

            await ctx.send(waifu_url)


    @commands.command(name='letters')
    async def fap_letters(self, ctx, *, text: str):
        """return text in different fonts"""

        for font in mapfont(text):
            dprint(font)

        await dsend(ctx.channel)


    async def _user_reply_to(self, ctx, channel, user, ref, author_in_title=True):
        embed = await create_reply_embed_from_ref(ctx.channel, ref, author_in_title)
        await webhook_send(ctx, channel, user, embed=embed)

    # def cog_unload(self):
    #     self.bot.loop.create_task(self.session.close())

