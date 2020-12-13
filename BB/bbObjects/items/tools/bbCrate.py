import random
from . import bbToolItem
from .... import lib, bbGlobals
from discord import Message
import asyncio
from ....bbConfig import bbConfig
from .. import bbItem
from ....logging import bbLogger


@bbItem.spawnableItem
class bbCrate(bbToolItem.bbToolItem):
    def __init__(self, itemPool, name : str = "", value : int = 0, wiki : str = "",
            manufacturer : str = "", icon : str = "", emoji : lib.emojis.dumbEmoji = lib.emojis.dumbEmoji.EMPTY,
            techLevel : int = -1, builtIn : bool = False):

        super().__init__(name, [], value=value, wiki=wiki,
            manufacturer=manufacturer, icon=icon, emoji=emoji,
            techLevel=techLevel, builtIn=builtIn)
        
        for item in itemPool:
            if not isinstance(item, bbItem.bbItem):
                raise RuntimeError("Attempted to create a bbCrate with something other than a spawnableItem in its itemPool.")
        self.itemPool = itemPool


    async def use(self, *args, **kwargs):
        """This item's behaviour function. Intended to be very generic at this level of implementation.
        """
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        callingBBUser = kwargs["callingBBUser"]
        callingBBUser.inactiveTools.addItem(random.choice(self.itemPool))
        callingBBUser.inactiveTools.removeItem(self)


    async def userFriendlyUse(self, message : Message, *args, **kwargs) -> str:
        """A version of self.use intended to be called by users, where exceptions are never thrown in the case of
        user error, and results strings are always returned.

        :param Message message: The discord message that triggered this tool use
        :return: A user-friendly messge summarising the result of the tool use.
        :rtype: str
        """
        if "callingBBUser" not in kwargs:
            raise NameError("Required kwarg not given: callingBBUser")
        if kwargs["callingBBUser"] is not None and kwargs["callingBBUser"].__class__.__name__ != "bbUser":
            raise TypeError("Required kwarg is of the wrong type. Expected bbUser or None, received " + kwargs["callingBBUser"].__class__.__name__)
        
        callingBBUser = kwargs["callingBBUser"]

        confirmMsg = await message.channel.send("Are you sure you want to open this crate? Please react to this message to confirm:\n" + bbConfig.defaultAcceptEmoji.sendable + " : Yes\n" + bbConfig.defaultRejectEmoji.sendable + " : Cancel\n\n*This menu will expire in " + str(bbConfig.skinApplyConfirmTimeoutSeconds) + "seconds.*") 
        
        def useConfirmCheck(reactPL):
            return reactPL.message_id == confirmMsg.id and reactPL.user_id == message.author.id and lib.emojis.dumbEmojiFromPartial(reactPL.emoji) in [bbConfig.defaultAcceptEmoji, bbConfig.defaultRejectEmoji]

        try:
            reactPL = await bbGlobals.client.wait_for("raw_reaction_add", check=useConfirmCheck, timeout=bbConfig.skinApplyConfirmTimeoutSeconds)
        except asyncio.TimeoutError:
            await confirmMsg.edit(content="This menu has now expired. Please use `" + bbConfig.commandPrefix + "use` again.")
        else:
            if lib.emojis.dumbEmojiFromPartial(reactPL.emoji) == bbConfig.defaultAcceptEmoji:
                newItem = random.choice(self.itemPool)
                callingBBUser.inactiveTools.addItem(random.choice(self.itemPool))
                callingBBUser.inactiveTools.removeItem(self)
                
                return "🎉 Success! You got a " + newItem.name + "!"
            else:
                return "🛑 Crate open cancelled."

    
    def statsStringShort(self) -> str:
        """Summarise all the statistics and functionality of this item as a string.

        :return: A string summarising the statistics and functionality of this item
        :rtype: str
        """
        return "*" + str(len(self.itemPool)) + " possible items*"


    def getType(self) -> type:
        """⚠ DEPRACATED
        Get the type of this object.

        :return: The bbItem class
        :rtype: type
        """
        return bbCrate

    
    def toDict(self, **kwargs) -> dict:
        """Serialize this tool into dictionary format.
        This step of implementation adds a 'type' string indicating the name of this tool's subclass.

        :return: The default bbItem toDict implementation, with an added 'type' field
        :rtype: dict
        """
        data = super().toDict(**kwargs)
        data["itemPool"] = []
        for item in self.itemPool:
            data["itemPool"].append(item.toDict())
        return data


    @classmethod
    def fromDict(cls, crateDict, **kwargs):
        itemPool = []
        if "itemPool" in crateDict:
            for itemDict in crateDict["itemPool"]:
                itemPool.append(bbItem.spawnItem(itemDict))
        else:
            bbLogger.log("bbCrate", "fromDict", "fromDict-ing a bbCrate with no itemPool.")
        
        return bbCrate(itemPool, name=crateDict["name"] if "name" in crateDict else "",
            value=crateDict["value"] if "value" in crateDict else 0,
            wiki=crateDict["wiki"] if "wiki" in crateDict else "",
            manufacturer=crateDict["manufacturer"] if "manufacturer" in crateDict else "",
            icon=crateDict["icon"] if "icon" in crateDict else "",
            emoji=lib.emojis.dumbEmojiFromDict(crateDict["emoji"]) if "emoji" in crateDict else lib.emojis.dumbEmoji.EMPTY,
            techLevel=crateDict["techLevel"] if "techLevel" in crateDict else -1,
            builtIn=crateDict["builtIn"] if "builtIn" in crateDict else False)
