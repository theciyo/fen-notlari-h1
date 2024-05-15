from highrise import *
from highrise.models import *
from asyncio import run as arun
from flask import Flask
from threading import Thread
from highrise.__main__ import *
import random
import asyncio
import time

class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.target_room_id = "6510519bef2d56a7ddd1391d"
        self.is_teleporting_dict = {}
        self.following_user = None
        self.following_user_id = None
        self.kus = {}
        self.user_positions = {} 
        self.position_tasks = {} 

    haricler = ["karainek"]


    async def on_start(self, session_metadata: SessionMetadata) -> None:
        print("hi im alive?")
        self.highrise.tg.create_task(self.highrise.teleport(
            session_metadata.user_id, Position(17.00, 0.00,13.5, "FrontRight")))

    async def on_user_move(self, user: User, pos: Position) -> None:
        """On a user moving in the room."""
        print(f"{user.username} moved to {pos}")

    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        await self.highrise.chat(f"Hoşgeldin @{user.username}!")

    async def on_user_leave(self, user: User):    
        user_id = user.id
        farewell_message = f"Görüşürüz @{user.username}!"
        if user_id in self.kus:
            self.kus[user_id] = False      
        if self.following_user and self.following_user.id == user_id:
            self.following_user = None
        await self.highrise.chat(farewell_message)
    async def reset_target_position(self, target_user_obj: User, initial_position: Position) -> None:
        try:
            while True:
                room_users = await self.highrise.get_room_users()
                current_position = next((position for user, position in room_users.content if user.id == target_user_obj.id), None)

                if current_position and current_position != initial_position:
                    await self.teleport(target_user_obj, initial_position)

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"An error occurred during position monitoring: {e}")

    async def on_chat(self, user: User, message: str) -> None:

        if message.lower().startswith("cak") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip()
            room_users = await self.highrise.get_room_users()
            user_info = next((info for info in room_users.content if info[0].username.lower() == target_username.lower()), None)

            if user_info:
                target_user_obj, initial_position = user_info
                task = asyncio.create_task(self.reset_target_position(target_user_obj, initial_position))

                if target_user_obj.id not in self.position_tasks:
                    self.position_tasks[target_user_obj.id] = []
                self.position_tasks[target_user_obj.id].append(task)

        elif message.lower().startswith("cek") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip()
            room_users = await self.highrise.get_room_users()
            target_user_obj = next((user_obj for user_obj, _ in room_users.content if user_obj.username.lower() == target_username.lower()), None)

            if target_user_obj:
                tasks = self.position_tasks.pop(target_user_obj.id, [])
                for task in tasks:
                    task.cancel()
                print(f"Breaking position monitoring loop for {target_username}")
            else:
                print(f"User {target_username} not found in the room.")


        if message.lower().startswith("herkes kick") and await self.is_user_allowed(user):
            room_users = (await self.highrise.get_room_users()).content
            for room_user, pos in room_users:
                if room_user.username not in self.haricler:
                    try:
                        await self.highrise.moderate_room(room_user.id, "kick")
                    except Exception:
                        pass

        if message.lower().startswith("herkes yanima") and await self.is_user_allowed(user):
            room_users = (await self.highrise.get_room_users()).content

            for room_user, _ in room_users:
                if room_user.id != user.id and room_user.username not in self.haricler:
                    await self.teleport_user_next_to(room_user.username, user)

        if message.lower().startswith("herkes havaya") and await self.is_user_allowed(user):
            room_users = (await self.highrise.get_room_users()).content
            for room_user, _ in room_users:
                if room_user.username not in self.haricler:
                    try:
                        kl = Position(random.randint(1, 25), random.randint(1, 25), random.randint(1, 25))
                        await self.teleport(room_user, kl)
                    except Exception as e:
                        print(f"An error occurred while teleporting: {e}")




        if message.lower().startswith("info"):
            target_username = message.split("@")[-1].strip()
            await self.userinfo(user, target_username)


        if message.startswith("+x") or message.startswith("-x"):
            await self.adjust_position(user, message, 'x')
        elif message.startswith("+y") or message.startswith("-y"):
            await self.adjust_position(user, message, 'y')
        elif message.startswith("+z") or message.startswith("-z"):
            await self.adjust_position(user, message, 'z')


        allowed_commands = ["switch", "degis", "değiş"] 
        if any(message.lower().startswith(command) for command in allowed_commands) and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip()


            if target_username not in self.haricler:
                await self.switch_users(user, target_username)
            else:
                print(f"{target_username} is in the exclusion list and won't be affected by the switch.")

        message_lower = message.lower()

        reactions_mapping = {
            "herkese el": "wave",
            "herkese parmak": "thumbs",
            "herkese kalp": "heart",
            "herkese alkis": "clap",
            "herkese alkış": "clap",
            "herkese goz": "wink",
            "herkese göz": "wink"
        }

        for reaction_name, reaction in reactions_mapping.items():
            if reaction_name in message_lower and await self.is_user_allowed(user):
                room_users = (await self.highrise.get_room_users()).content
                try:
                    for room_user, _ in room_users:
                        if room_user.id not in ["659873d169db490d461690c0", "6607332b6b826c09f89ce332"]:
                            await self.highrise.react(reaction, room_user.id)
                except Exception as e:
                    print(f"An error occurred while sending all reactions: {e}")


        reactions_mapping = {
            "👋": "wave",
            "👍": "thumbs",
            "❤️": "heart",
            "👏": "clap",
            "😉": "wink",
        }

        unique_emojis = set(reactions_mapping.keys())

        for emoji in unique_emojis:
            count = message.count(emoji)
            if count > 0:
                await self.highrise.react(reactions_mapping[emoji], user.id)     

# TELPORTLAR TELEPORTLAR TELEPORT


        message = message.lower()

        teleport_locations = {
            "havuz": Position(12.5, 0.0, 20.5),
            "kalp": Position(7.0, 11.0, 11.0),
            "kapi": Position(17.5, 0.35, 14.5),
            "kapı": Position(17.5, 0.35, 14.5),
            "kuş": Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40)),
            "kus": Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))
        }

        for location_name, position in teleport_locations.items():
            if message ==(location_name):
                try:
                    await self.teleport(user, position)
                except:
                    print("Teleportasyon sırasında hata oluştu")



        message = message.lower()

        teleport_locations = {
            "!havuz": Position(12.5, 0.0, 20.5),
            "!kalp": Position(7.0, 11.0, 11.0),
            "!kapi": Position(17.5, 0.35, 14.5),
            "!kapı": Position(17.5, 0.35, 14.5),
            "!kuş": Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40)),
            "!kus": Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))
        }

        for location_name, position in teleport_locations.items():
            if message.startswith(location_name):
                target_username = message.split("@")[-1].strip().lower()

                try:
                    room_users = (await self.highrise.get_room_users()).content
                    target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

                    if target_user and target_user.username.lower() not in self.haricler:
                        try:
                            await self.teleport(target_user, position)
                        except Exception as e:
                            print(f"An error occurred during teleportation: {e}")
                except Exception as e:
                    print(f"An error occurred while getting room users: {e}")

        if                          message.lower().startswith("gotur") or message.lower().startswith("götür"):
          target_username =         message.split("@")[-1].strip()
          await                     self.teleport_to_user(user, target_username)
        if await self.is_user_allowed(user) and message.lower().startswith("getir"):
            target_username = message.split("@")[-1].strip()
            if target_username not in self.haricler:
                await self.teleport_user_next_to(target_username, user)
        if message.lower().startswith("git") and await self.is_user_allowed(user):
            parts = message.split()
            if len(parts) == 2 and parts[1].startswith("@"):
                target_username = parts[1][1:]
                target_user = None

                room_users = (await self.highrise.get_room_users()).content
                for room_user, _ in room_users:
                    if room_user.username.lower() == target_username and room_user.username.lower() not in self.haricler:
                        target_user = room_user
                        break

                if target_user:
                    try:
                        kl = Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))
                        await self.teleport(target_user, kl)
                    except Exception as e:
                        print(f"An error occurred while teleporting: {e}")
                else:
                    print(f"Kullanıcı adı '{target_username}' odada bulunamadı.")

        if message.lower() == "full kus" or message.lower() == "full kuş":
            if user.id not in self.kus:
                self.kus[user.id] = False

            if not self.kus[user.id]:
                self.kus[user.id] = True

                try:
                    while self.kus.get(user.id, False):
                        kl = Position(random.randint(0, 40), random.randint(0, 40), random.randint(0, 40))
                        await self.teleport(user, kl)

                        await asyncio.sleep(0.7)
                except Exception as e:
                    print(f"Teleport sırasında bir hata oluştu: {e}")

        if message.lower() == "dur" or message.lower() == "stop":
            if user.id in self.kus: 
                self.kus[user.id] = False

# MODERATOR KICK BAN VESAIRE 

        if message.lower().startswith("yallah") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip().lower()

            try:
                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

                if target_user and target_user.username.lower() != "karainek":
                    await self.move_user_to_target_room(target_user.id)
            except Exception as e:
                print(f"An error occurred while moving the user: {e}")

        if message == "-inek":
            await self.move_user_to_target_room(user.id)
        if message.lower() == "herkes inek" and await self.is_user_allowed(user):
            await self.move_users_to_target_room()


        if message.lower().startswith("ceza") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip().lower()

            if target_username not in self.haricler:
                room_users = (await self.highrise.get_room_users()).content
                target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

                if target_user:
                    if target_user.id not in self.is_teleporting_dict:
                        self.is_teleporting_dict[target_user.id] = True

                        try:
                            while self.is_teleporting_dict.get(target_user.id, False):
                                kl = Position(random.randint(0, 30), random.randint(0, 0), random.randint(0, 30))
                                await self.teleport(target_user, kl)
                                await asyncio.sleep(1)
                        except Exception as e:
                            print(f"An error occurred while teleporting: {e}")

                        self.is_teleporting_dict.pop(target_user.id, None)
                        final_position = Position(17.0, 0.0, 13.5, "FrontRight")
                        await self.teleport(target_user, final_position)


        if message.lower().startswith("dur") and await self.is_user_allowed(user):
            target_username = message.split("@")[-1].strip().lower()

            room_users = (await self.highrise.get_room_users()).content
            target_user = next((u for u, _ in room_users if u.username.lower() == target_username), None)

            if target_user:
                self.is_teleporting_dict.pop(target_user.id, None)


        if message.lower() == "takip" and await self.is_user_allowed(user):
            if self.following_user is not None:
                await self.highrise.chat("Şu anda başka birini takip ediyorum, sıranızı bekleyin.")
            else:
                await self.follow(user)

        if message.lower() == "stay" and await self.is_user_allowed(user):
            if self.following_user is not None:
                await self.highrise.chat("Takip etmeyi bıraktım.")
                self.following_user = None
            else:
                await self.highrise.chat("Şu anda kimseyi takip etmiyorum.")

        if message.lower().startswith("kick") and await self.is_user_allowed(user):
            parts = message.split()
            if len(parts) != 2:
                return
            if "@" not in parts[1]:
                username = parts[1]
            else:
                username = parts[1][1:]

            room_users = (await self.highrise.get_room_users()).content
            for room_user, pos in room_users:
                if room_user.username.lower() == username.lower():
                    user_id = room_user.id
                    break

            if "user_id" not in locals():
                return

            try:
                await self.highrise.moderate_room(user_id, "kick")
            except Exception as e:
                return


# DIGER KOMUTLAR WIE ASYNICO UND DING


    async def on_reaction(self, user: User, reaction: str, receiver: User) -> None:

        if str(receiver.id) == "662e31cc27ad3ed321e4a396":
            try:
                await self.highrise.react(reaction, user.id)
            except Exception as e:
                print(f"An error occurred while reacting: {e}")

    async def move_users_to_target_room(self):
        room_users = (await self.highrise.get_room_users()).content

        for room_user, _ in room_users:
                await self.highrise.move_user_to_room(room_user.id, self.target_room_id)

    async def move_user_to_target_room(self, user_id: str):
        await self.highrise.move_user_to_room(user_id, self.target_room_id)

    async def is_user_allowed(self, user: User) -> bool:
        user_privileges = await self.highrise.get_room_privilege(user.id)
        return user_privileges.moderator or user.username in ["karainek", "The.Ciyo"]

    async def moderate_room(
        self,
        user_id: str,
        action: Literal["kick", "ban", "unban", "mute"],
        action_length: int | None = None,
    ) -> None:
        """Moderate a user in the room."""

    async def userinfo(self, user: User, target_username: str) -> None:
        user_info = await self.webapi.get_users(username=target_username, limit=1)

        if not user_info.users:
            await self.highrise.chat("Kullanıcı bulunamadı, lütfen geçerli bir kullanıcı belirtin")
            return

        user_id = user_info.users[0].user_id

        user_info = await self.webapi.get_user(user_id)

        number_of_followers = user_info.user.num_followers
        number_of_friends = user_info.user.num_friends
        country_code = user_info.user.country_code
        outfit = user_info.user.outfit
        bio = user_info.user.bio
        active_room = user_info.user.active_room
        crew = user_info.user.crew
        number_of_following = user_info.user.num_following
        joined_at = user_info.user.joined_at.strftime("%d/%m/%Y %H:%M:%S")

        joined_date = user_info.user.joined_at.date()
        today = datetime.now().date()
        days_played = (today - joined_date).days

        last_login = user_info.user.last_online_in.strftime("%d/%m/%Y %H:%M:%S") if user_info.user.last_online_in else "Son giriş bilgisi mevcut değil"

        await self.highrise.chat(f"""Kullanıcı adı: {target_username}\nTakipçi: {number_of_followers}\nArkadaş: {number_of_friends}\nOyuna Başlama: {joined_at}\nOyanma Süresi: {days_played}""")

    async def follow(self, user: User, message: str = ""):
        self.following_user = user  
        while self.following_user == user:
            room_users = (await self.highrise.get_room_users()).content
            for room_user, position in room_users:
                if room_user.id == user.id:
                    user_position = position
                    break
            if user_position is not None and isinstance(user_position, Position):
                nearby_position = Position(user_position.x + 1.0, user_position.y, user_position.z)
                await self.highrise.walk_to(nearby_position)

            await asyncio.sleep(0.5)


    async def on_message(self, user_id: str, conversation_id: str, is_new_conversation: bool) -> None:
        response = await self.highrise.get_messages(conversation_id)
        if isinstance(response, GetMessagesRequest.GetMessagesResponse):
            message = response.messages[0].content
            print(message)

        if message.lower() == "liste":
            await self.highrise.send_message(conversation_id, "1. Angry\n2. Bow\n3. Casual\n4. Celebrate\n5. Charging\n6. Confused\n7. Cursing\n8. Curtsy\n9. Cutey\n10. Dotheworm\n11. Cute\n12. Energyball\n13. Enthused\n14. Fashion\n15. Flex\n16. Float\n17. Frog\n18. Gagging\n19. Gravity\n20. Greedy\n21. Hello\n22. Hot\n23. Icecream\n24. Kiss\n25. Kpop\n26. Laugh\n27. Lust\n28. Macarena\n29. Maniac\n30. Model\n31. No\n32. Pose1\n33. Pose3\n34. Pose5\n35. Pose7\n36. Pose8\n37. Punk\n38. Russian\n39. Sad\n40. Sayso\n41. Shopping\n42. Shy\n43. Sit\n44. Snowangel\n45. Snowball\n46. Superpose\n47. Telekinesis\n48. Teleport\n49. Thumbs\n50. Tired\n51. Uwu\n52. Wave\n53. Weird\n54. Wrong\n55. Yes\n56. Zero\n57. Penny\n58. Zombie\n59. Fight\n60. Sing\n61. Savage\n62. Donot\n63. Shuffle\n64. Viral\n65. Penguin\n66. Rock\n67. Star\n68. Boxer\n69. Creepy\n70. Anime\n71. Ruh\n72. Kafasız\n73. Bashful\n74. Party\n75. Pose10\n76. Skate\n77. Wild\n78. Nervous\n79. Timejump\n80. Toilet\n81. Jingle\n82. Hyped\n83. Sleigh\n84. Pose6\n85. Kawai\n86. Touch\n87. Repose\n88. Step\n89. Push\n90. Launch\n91. Salute\n92. Attention\n93. Wop\n94. Gift\n95. Ditzy")

    async def on_tip(self, sender: User, receiver: User, tip: CurrencyItem | Item) -> None:
        message = f"{sender.username} tarafından {receiver.username} kişine {tip.amount} altın bağış yapıldı."
        await self.highrise.chat(message)




    async def on_whisper(self, user: User, message: str) -> None:
        """On a received room whisper."""
        if await self.is_user_allowed(user) and message.startswith(''):
            try:
                xxx = message[0:]
                await self.highrise.chat(xxx)
            except:
                print("error 3")


#TELEPORT
    async def adjust_position(self, user: User, message: str, axis: str) -> None:
        try:
            adjustment = int(message[2:])
            if message.startswith("-"):
                adjustment *= -1

            room_users = await self.highrise.get_room_users()
            user_position = None

            for user_obj, user_position in room_users.content:
                if user_obj.id == user.id:
                    break

            if user_position:
                new_position = None

                if axis == 'x':
                    new_position = Position(user_position.x + adjustment, user_position.y, user_position.z, user_position.facing)
                elif axis == 'y':
                    new_position = Position(user_position.x, user_position.y + adjustment, user_position.z, user_position.facing)
                elif axis == 'z':
                    new_position = Position(user_position.x, user_position.y, user_position.z + adjustment, user_position.facing)
                else:
                    print(f"Unsupported axis: {axis}")
                    return

                await self.teleport(user, new_position)

        except ValueError:
            print("Invalid adjustment value. Please use +x/-x, +y/-y, or +z/-z followed by an integer.")
        except Exception as e:
            print(f"An error occurred during position adjustment: {e}")

    async def switch_users(self, user: User, target_username: str) -> None:
        try:
            room_users = await self.highrise.get_room_users()

            maker_position = None
            for maker_user, maker_position in room_users.content:
                if maker_user.id == user.id:
                    break

            target_position = None
            for target_user, position in room_users.content:
                if target_user.username.lower() == target_username.lower():
                    target_position = position
                    break

            if maker_position and target_position:
                await self.teleport(user, Position(target_position.x + 0.0001, target_position.y, target_position.z, target_position.facing))

                await self.teleport(target_user, Position(maker_position.x + 0.0001, maker_position.y, maker_position.z, maker_position.facing))

        except Exception as e:
            print(f"An error occurred during user switch: {e}")

    async def teleport(self, user: User, position: Position):
        try:
            await self.highrise.teleport(user.id, position)
        except Exception as e:
            print(f"Caught Teleport Error: {e}")

    async def teleport_to_user(self, user: User, target_username: str) -> None:
        try:
            room_users = await self.highrise.get_room_users()
            for target, position in room_users.content:
                if target.username.lower() == target_username.lower():
                    z = position.z
                    new_z = z - 1
                    await self.teleport(user, Position(position.x, position.y, new_z, position.facing))
                    break
        except Exception as e:
            print(f"An error occurred while teleporting to {target_username}: {e}")

    async def teleport_user_next_to(self, target_username: str, requester_user: User) -> None:
        try:

            room_users = await self.highrise.get_room_users()
            requester_position = None
            for user, position in room_users.content:
                if user.id == requester_user.id:
                    requester_position = position
                    break



            for user, position in room_users.content:
                if user.username.lower() == target_username.lower():
                    z = requester_position.z
                    new_z = z + 1  
                    await self.teleport(user, Position(requester_position.x, requester_position.y, new_z, requester_position.facing))
                    break
        except Exception as e:
            print(f"An error occurred while teleporting {target_username} next to {requester_user.username}: {e}")





    async def run(self, room_id, token) -> None:
        await __main__.main(self, room_id, token)
class WebServer():

  def __init__(self):
    self.app = Flask(__name__)

    @self.app.route('/')
    def index() -> str:
      return "Alive"

  def run(self) -> None:
    self.app.run(host='0.0.0.0', port=8080)

  def keep_alive(self):
    t = Thread(target=self.run)
    t.start()

class RunBot():
  room_id = "6636bdd57bea260ddd72f7f6"
  bot_token = "b8fcd3b7e5dac42b093fd830362c4597d295f3839b1603f1bd7c771ec8be8903"
  bot_file = "main"
  bot_class = "Bot"

  def __init__(self) -> None:
    self.definitions = [
        BotDefinition(
            getattr(import_module(self.bot_file), self.bot_class)(),
            self.room_id, self.bot_token)
    ] 

  def run_loop(self) -> None:
    while True:
      try:
        arun(main(self.definitions)) 
      except Exception as e:
        import traceback
        print("Caught an exception:")
        traceback.print_exc()
        time.sleep(1)
        continue


if __name__ == "__main__":
  WebServer().keep_alive()

  RunBot().run_loop()