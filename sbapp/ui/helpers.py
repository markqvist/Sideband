from kivy.utils import get_color_from_hex
from kivymd.color_definitions import colors
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import OneLineIconListItem, MDList, IconLeftWidget, IconRightWidget
from kivy.properties import StringProperty

ts_format = "%Y-%m-%d %H:%M:%S"
file_ts_format = "%Y_%m_%d_%H_%M_%S"

def mdc(color, hue=None):
    if hue == None:
        hue = "400"
    return get_color_from_hex(colors[color][hue])

color_playing = "Amber"
color_received = "LightGreen"
color_delivered = "Blue"
color_paper = "Indigo"
color_propagated = "Indigo"
color_failed = "Red"
color_unknown = "Gray"
intensity_msgs_dark = "800"
intensity_msgs_light = "500"
intensity_play_dark = "600"
intensity_play_light = "300"

class ContentNavigationDrawer(Screen):
    pass

class DrawerList(MDList):
    pass

class IconListItem(OneLineIconListItem):
    icon = StringProperty()

def is_emoji(unicode_character):
    return unicode_character in emoji_lookup

def strip_emojis(str_input):
    output = ""
    for cp in str_input:
        if not is_emoji(cp):
            output += cp
    return output

def multilingual_markup(data):
    # TODO: Remove
    # import time
    # ts = time.time()

    do = ""
    rfont = "default"
    ds = data.decode("utf-8")
    for cp in ds:
        match = False
        switch = False
        pfont = rfont

        if is_emoji(cp):
            match = True
            if rfont != "emoji":
                switch = True
                rfont = "emoji"

        if not match:
            for range_start in codepoint_map:
                range_end = codepoint_map[range_start][0]
                mapped_font = codepoint_map[range_start][1]

                if range_end >= ord(cp) >= range_start:
                    match = True
                    if rfont != mapped_font:
                        rfont = mapped_font
                        switch = True               
                    break

        if (not match) and rfont != "default":
            rfont = "default"
            switch = True

        if switch:
            if pfont != "default":
                do += "[/font]"
            if rfont != "default":
                do += "[font="+str(rfont)+"]"

        do += cp

    if rfont != "default":
        do += "[/font]"

    # TODO: Remove
    # print(do+"\n\n"+str(time.time()-ts))

    return do.encode("utf-8")

codepoint_map = {
    0x0590: [0x05ff, "hebrew"],
    0x2e3a: [0x2e3b, "chinese"],
    0x2e80: [0x2ef3, "chinese"],
    0x2f00: [0x2fdf, "chinese"],
    0x2ff0: [0x2fff, "chinese"],
    0x3000: [0x303f, "chinese"],
    0x3040: [0x309f, "japanese"],
    0x30a0: [0x30ff, "japanese"],
    0x3100: [0x312f, "japanese"],
    0x3130: [0x318f, "japanese"],
    0x3190: [0x319f, "japanese"],
    0x31a0: [0x31bf, "japanese"],
    0x31c0: [0x31ef, "japanese"],
    0x31f0: [0x31ff, "japanese"],
    0x3200: [0x32ff, "japanese"],
    0x3300: [0x33ff, "japanese"],
    0xf900: [0xfa6d, "japanese"],
    0xfb00: [0xfb04, "japanese"],
    0xfe10: [0xfe1f, "japanese"],
    0xfe30: [0xfe4f, "japanese"],
    0xfe50: [0xfe6f, "japanese"],
    0x3400: [0x4dbf, "chinese"],
    0x4e00: [0x9fff, "chinese"],
    0xff00: [0xffef, "japanese"],
    0x10000: [0x1fffd, "japanese"],
    0x1f100: [0x1f1ff, "japanese"],
    0x1f200: [0x1f2ff, "japanese"],
    0x20000: [0x3fffd, "japanese"],
    0xa960: [0xa97f, "korean"],
    0xac00: [0xd7af, "korean"],
    0xd7b0: [0xd7ff, "korean"],
    0x0900: [0x097f, "combined"], # Devanagari
}

emoji_lookup = [
    "⌚","⌛","","⏪","⏫","⏬","⏰","⏳","◽","◾","☔","☕","♈","♉","♊","♋","♌","♍","♎","♏","♐","♑","♒","♓","♿","⚓",
    "⚡","⚪","⚫","⚽","⚾","⛄","⛅","⛎","⛔","⛪","⛲","⛳","⛵","⛺","⛽","✅","✊","✋","✨","❌","❎","❓","❔","❕","❗","➕",
    "➖","➗","➰","➿","⬛","⬜","⭐","⭕","🀄","🃏","🆎","🆑","🆒","🆓","🆔","🆕","🆖","🆗","🆘","🆙","🆚","🈁","🈚","🈯","🈲","🈳",
    "🈴","🈵","🈶","🈸","🈹","🈺","🉐","🉑","🌀","🌁","🌂","🌃","🌄","🌅","🌆","🌇","🌈","🌉","🌊","🌋","🌌","🌍","🌎","🌏","🌐","🌑",
    "🌒","🌓","🌔","🌕","🌖","🌗","🌘","🌙","🌚","🌛","🌜","🌝","🌞","🌟","🌠","🌭","🌮","🌯","🌰","🌱","🌲","🌳","🌴","🌵","🌷","🌸",
    "🌹","🌺","🌻","🌼","🌽","🌾","🌿","🍀","🍁","🍂","🍃","🍄","🍅","🍆","🍇","🍈","🍉","🍊","🍋","🍌","🍍","🍎","🍏","🍐","🍑","🍒",
    "🍓","🍔","🍕","🍖","🍗","🍘","🍙","🍚","🍛","🍜","🍝","🍞","🍟","🍠","🍡","🍢","🍣","🍤","🍥","🍦","🍧","🍨","🍩","🍪","🍫","🍬",
    "🍭","🍮","🍯","🍰","🍱","🍲","🍳","🍴","🍵","🍶","🍷","🍸","🍹","🍺","🍻","🍼","🍾","🍿","🎀","🎁","🎂","🎃","🎄","🎅","🎆","🎇",
    "🎈","🎉","🎊","🎋","🎌","🎍","🎎","🎏","🎐","🎑","🎒","🎓","🎠","🎡","🎢","🎣","🎤","🎥","🎦","🎧","🎨","🎩","🎪","🎫","🎬","🎭",
    "🎮","🎯","🎰","🎱","🎲","🎳","🎴","🎵","🎶","🎷","🎸","🎹","🎺","🎻","🎼","🎽","🎾","🎿","🏀","🏁","🏂","🏃","🏄","🏅","🏆","🏇",
    "🏈","🏉","🏊","🏏","🏐","🏑","🏒","🏓","🏠","🏡","🏢","🏣","🏤","🏥","🏦","🏧","🏨","🏩","🏪","🏫","🏬","🏭","🏮","🏯","🏰","🏴",
    "🏸","🏹","🏺","🏻","🏼","🏽","🏾","🏿","🐀","🐁","🐂","🐃","🐄","🐅","🐆","🐇","🐈","🐉","🐊","🐋","🐌","🐍","🐎","🐏","🐐","🐑",
    "🐒","🐓","🐔","🐕","🐖","🐗","🐘","🐙","🐚","🐛","🐜","🐝","🐞","🐟","🐠","🐡","🐢","🐣","🐤","🐥","🐦","🐧","🐨","🐩","🐪","🐫",
    "🐬","🐭","🐮","🐯","🐰","🐱","🐲","🐳","🐴","🐵","🐶","🐷","🐸","🐹","🐺","🐻","🐼","🐽","🐾","👀","👂","👃","👄","👅","👆","👇",
    "👈","👉","👊","👋","👌","👍","👎","👏","👐","👑","👒","👓","👔","👕","👖","👗","👘","👙","👚","👛","👜","👝","👞","👟","👠","👡",
    "👢","👣","👤","👥","👦","👧","👨","👩","👪","👫","👬","👭","👮","👯","👰","👱","👲","👳","👴","👵","👶","👷","👸","👹","👺","👻",
    "👼","👽","👾","👿","💀","💁","💂","💃","💄","💅","💆","💇","💈","💉","💊","💋","💌","💍","💎","💏","💐","💑","💒","💓","💔","💕",
    "💖","💗","💘","💙","💚","💛","💜","💝","💞","💟","💠","💡","💢","💣","💤","💥","💦","💧","💨","💩","💪","💫","💬","💭","💮","💯",
    "💰","💱","💲","💳","💴","💵","💶","💷","💸","💹","💺","💻","💼","💽","💾","💿","📀","📁","📂","📃","📄","📅","📆","📇","📈","📉",
    "📊","📋","📌","📍","📎","📏","📐","📑","📒","📓","📔","📕","📖","📗","📘","📙","📚","📛","📜","📝","📞","📟","📠","📡","📢","📣",
    "📤","📥","📦","📧","📨","📩","📪","📫","📬","📭","📮","📯","📰","📱","📲","📳","📴","📵","📶","📷","📸","📹","📺","📻","📼","📿",
    "🔀","🔁","🔂","🔃","🔄","🔅","🔆","🔇","🔈","🔉","🔊","🔋","🔌","🔍","🔎","🔏","🔐","🔑","🔒","🔓","🔔","🔕","🔖","🔗","🔘","🔙",
    "🔚","🔛","🔜","🔝","🔞","🔟","🔠","🔡","🔢","🔣","🔤","🔥","🔦","🔧","🔨","🔩","🔪","🔫","🔬","🔭","🔮","🔯","🔰","🔱","🔲","🔳",
    "🔴","🔵","🔶","🔷","🔸","🔹","🔺","🔻","🔼","🔽","🕋","🕌","🕍","🕎","🕐","🕑","🕒","🕓","🕔","🕕","🕖","🕗","🕘","🕙","🕚","🕛",
    "🕜","🕝","🕞","🕟","🕠","🕡","🕢","🕣","🕤","🕥","🕦","🕧","🖕","🖖","🗻","🗼","🗽","🗾","🗿","😀","😁","😂","😃","😄","😅","😆",
    "😇","😈","😉","😊","😋","😌","😍","😎","😏","😐","😑","😒","😓","😔","😕","😖","😗","😘","😙","😚","😛","😜","😝","😞","😟","😠",
    "😡","😢","😣","😤","😥","😦","😧","😨","😩","😪","😫","😬","😭","😮","😯","😰","😱","😲","😳","😴","😵","😶","😷","😸","😹","😺",
    "😻","😼","😽","😾","😿","🙀","🙁","🙂","🙃","🙄","🙅","🙆","🙇","🙈","🙉","🙊","🙋","🙌","🙍","🙎","🙏","🚀","🚁","🚂","🚃","🚄",
    "🚅","🚆","🚇","🚈","🚉","🚊","🚋","🚌","🚍","🚎","🚏","🚐","🚑","🚒","🚓","🚔","🚕","🚖","🚗","🚘","🚙","🚚","🚛","🚜","🚝","🚞",
    "🚟","🚠","🚡","🚢","🚣","🚤","🚥","🚦","🚧","🚨","🚩","🚪","🚫","🚬","🚭","🚮","🚯","🚰","🚱","🚲","🚳","🚴","🚵","🚶","🚷","🚸",
    "🚹","🚺","🚻","🚼","🚽","🚾","🚿","🛀","🛁","🛂","🛃","🛄","🛅","🛌","🛐","🛫","🛬","🤐","🤑","🤒","🤓","🤔","🤕","🤖","🤗","🤘",
    "🦀","🦁","🦂","🦃","🦄","🧀","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇦🇽","🇦🇿","🇧🇦","🇧🇧","🇧🇩",
    "🇧🇪","🇧🇫","🇧🇬","🇧🇭","🇧🇮","🇧🇯","🇧🇱","🇧🇲","🇧🇳","🇧🇴","🇧🇶","🇧🇷","🇧🇸","🇧🇹","🇧🇻","🇧🇼","🇧🇾","🇧🇿","🇨🇦","🇨🇨","🇨🇩","🇨🇫","🇨🇬","🇨🇭","🇨🇮","🇨🇰",
    "🇨🇱","🇨🇲","🇨🇳","🇨🇴","🇨🇵","🇨🇷","🇨🇺","🇨🇻","🇨🇼","🇨🇽","🇨🇾","🇨🇿","🇩🇪","🇩🇬","🇩🇯","🇩🇰","🇩🇲","🇩🇴","🇩🇿","🇪🇦","🇪🇨","🇪🇪","🇪🇬","🇪🇭","🇪🇷","🇪🇸",
    "🇪🇹","🇪🇺","🇫🇮","🇫🇯","🇫🇰","🇫🇲","🇫🇴","🇫🇷","🇬🇦","🇬🇧","🇬🇩","🇬🇪","🇬🇫","🇬🇬","🇬🇭","🇬🇮","🇬🇱","🇬🇲","🇬🇳","🇬🇵","🇬🇶","🇬🇷","🇬🇸","🇬🇹","🇬🇺","🇬🇼",
    "🇬🇾","🇭🇰","🇭🇲","🇭🇳","🇭🇷","🇭🇹","🇭🇺","🇮🇨","🇮🇩","🇮🇪","🇮🇱","🇮🇲","🇮🇳","🇮🇴","🇮🇶","🇮🇷","🇮🇸","🇮🇹","🇯🇪","🇯🇲","🇯🇴","🇯🇵","🇰🇪","🇰🇬","🇰🇭","🇰🇮",
    "🇰🇲","🇰🇳","🇰🇵","🇰🇷","🇰🇼","🇰🇾","🇰🇿","🇱🇦","🇱🇧","🇱🇨","🇱🇮","🇱🇰","🇱🇷","🇱🇸","🇱🇹","🇱🇺","🇱🇻","🇱🇾","🇲🇦","🇲🇨","🇲🇩","🇲🇪","🇲🇫","🇲🇬","🇲🇭","🇲🇰",
    "🇲🇱","🇲🇲","🇲🇳","🇲🇴","🇲🇵","🇲🇶","🇲🇷","🇲🇸","🇲🇹","🇲🇺","🇲🇻","🇲🇼","🇲🇽","🇲🇾","🇲🇿","🇳🇦","🇳🇨","🇳🇪","🇳🇫","🇳🇬","🇳🇮","🇳🇱","🇳🇴","🇳🇵","🇳🇷","🇳🇺",
    "🇳🇿","🇴🇲","🇵🇦","🇵🇪","🇵🇫","🇵🇬","🇵🇭","🇵🇰","🇵🇱","🇵🇲","🇵🇳","🇵🇷","🇵🇸","🇵🇹","🇵🇼","🇵🇾","🇶🇦","🇷🇪","🇷🇴","🇷🇸","🇷🇺","🇷🇼","🇸🇦","🇸🇧","🇸🇨","🇸🇩",
    "🇸🇪","🇸🇬","🇸🇭","🇸🇮","🇸🇯","🇸🇰","🇸🇱","🇸🇲","🇸🇳","🇸🇴","🇸🇷","🇸🇸","🇸🇹","🇸🇻","🇸🇽","🇸🇾","🇸🇿","🇹🇦","🇹🇨","🇹🇩","🇹🇫","🇹🇬","🇹🇭","🇹🇯","🇹🇰","🇹🇱",
    "🇹🇲","🇹🇳","🇹🇴","🇹🇷","🇹🇹","🇹🇻","🇹🇼","🇹🇿","🇺🇦","🇺🇬","🇺🇲","🇺🇸","🇺🇾","🇺🇿","🇻🇦","🇻🇨","🇻🇪","🇻🇬","🇻🇮","🇻🇳","🇻🇺","🇼🇫","🇼🇸","🇽🇰","🇾🇪","🇾🇹",
    "🇿🇦","🇿🇲","🇿🇼","🟢"];

emoji_extra_1 = [
   "©","®","‼","⁉","™","ℹ","↔","↕","↖","↗","↘","↙","↩","↪","⌚","⌛","⌨","⏏","⏩","⏪","⏫","⏬","⏭","⏮","⏯",
   "⏰","⏱","⏲","⏳","⏸","⏹","⏺","Ⓜ","▪","▫","▶","◀","◻","◼","◽","◾","☀","☁","☂","☃","☄","☎","☑","☔",
   "☕","☘","☝","☠","☢","☣","☦","☪","☮","☯","☸","☹","☺","♀","♂","♈","♉","♊","♋","♌","♍","♎","♏","♐",
   "♑","♒","♓","♟","♠","♣","♥","♦","♨","♻","♾","♿","⚒","⚓","⚔","⚕","⚖","⚗","⚙","⚛","⚜","⚠","⚡","⚧","⚪",
   "⚫","⚰","⚱","⚽","⚾","⛄","⛅","⛈","⛎","⛏","⛑","⛓","⛔","⛩","⛪","⛰","⛱","⛲","⛳","⛴","⛵","⛷","⛸",
   "⛹","⬆","⬇","⬛","⬜","⭐","⭕","〰","⛺","⛽","✂","✅","✈","✉","✊","✋","✌","✍","✏","✒","✔","✖","✝","✡",
   "✨","✳","✴","❄","❇","❌","❎","❓","❔","❕","❗","❣","❤","➕","➖","➗","➡","➰","➿","⤴","⤵","⬅","〽","㊗",
   "㊙","🀄","🃏","🅰","🅱","🅾","🅿","🆎","🆑","🆒","🆓","🆔","🆕","🆖","🆗","🆘","🆙","🆚","🈁","🈂","🈚","🈯","🈲",
   "🈳","🈴","🈵","🈶","🈷","🈸","🈹","🈺","🉐","🉑","🌀","🌁","🌂","🌃","🌄","🌅","🌆","🌇","🌈","🌉","🌊","🌋",
   "🌌","🌍","🌎","🌏","🌐","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘","🌙","🌚","🌛","🌜","🌝","🌞","🌟","🌠","🌡",
   "🌤","🌥","🌦","🌧","🌨","🌩","🌪","🌫","🌬","🌭","🌮","🌯","🌰","🌱","🌲","🌳","🌴","🌵","🌶","🌷","🌸","🌹",
   "🌺","🌻","🌼","🌽","🌾","🌿","🍀","🍁","🍂","🍃","🍄","🍅","🍆","🍇","🍈","🍉","🍊","🍋","🍌","🍍","🍎","🍏",
   "🍐","🍑","🍒","🍓","🍔","🍕","🍖","🍗","🍘","🍙","🍚","🍛","🍜","🍝","🍞","🍟","🍠","🍡","🍢","🍣","🍤","🍥",
   "🍦","🍧","🍨","🍩","🍪","🍫","🍬","🍭","🍮","🍯","🍰","🍱","🍲","🍳","🍴","🍵","🍶","🍷","🍸","🍹","🍺","🍻",
   "🍼","🍽","🍾","🍿","🎀","🎁","🎂","🎃","🎄","🎅","🎆","🎇","🎈","🎉","🎊","🎋","🎌","🎍","🎎","🎏","🎐","🎑",
   "🎒","🎓","🎖","🎗","🎙","🎚","🎛","🎞","🎟","🎠","🎡","🎢","🎣","🎤","🎥","🎦","🎧","🎨","🎩","🎪","🎫","🎬","🎭",
   "🎮","🎯","🎰","🎱","🎲","🎳","🎴","🎵","🎶","🎷","🎸","🎹","🎺","🎻","🎼","🎽","🎾","🎿","🏀","🏁","🏂","🏃",
   "🏄","🏅","🏆","🏇","🏈","🏉","🏊","🏋","🏌","🏍","🏎","🏏","🏐","🏑","🏒","🏓","🏔","🏕","🏖","🏗","🏘","🏙",
   "🏚","🏛","🏜","🏝","🏞","🏟","🏠","🏡","🏢","🏣","🏤","🏥","🏦","🏧","🏨","🏩","🏪","🏫","🏬","🏭","🏮","🏯",
   "🏰","🏳","🏴","🏵","🏷","🏸","🏹","🏺","🏻","🏼","🏽","🏾","🏿","🐀","🐁","🐂","🐃","🐄","🐅","🐆","🐇","🐈",
   "🐉","🐊","🐋","🐌","🐍","🐎","🐏","🐐","🐑","🐒","🐓","🐔","🐕","🐖","🐗","🐘","🐙","🐚","🐛","🐜","🐝","🐞",
   "🐟","🐠","🐡","🐢","🐣","🐤","🐥","🐦","🐧","🐨","🐩","🐪","🐫","🐬","🐭","🐮","🐯","🐰","🐱","🐲","🐳","🐴",
   "🐵","🐶","🐷","🐸","🐹","🐺","🐻","🐼","🐽","🐾","🐿","👀","👁","👂","👃","👄","👅","👆","👇","👈","👉","👊",
   "👋","👌","👍","👎","👏","👐","👑","👒","👓","👔","👕","👖","👗","👘","👙","👚","👛","👜","👝","👞","👟","👠",
   "👡","👢","👣","👤","👥","👦","👧","👨","👩","👪","👫","👬","👭","👮","👯","👰","👱","👲","👳","👴","👵","👶",
   "👷","👸","👹","👺","👻","👼","👽","👾","👿","💀","💁","💂","💃","💄","💅","💆","💇","💈","💉","💊","💋","💌",
   "💍","💎","💏","💐","💑","💒","💓","💔","💕","💖","💗","💘","💙","💚","💛","💜","💝","💞","💟","💠","💡","💢",
   "💣","💤","💥","💦","💧","💨","💩","💪","💫","💬","💭","💮","💯","💰","💱","💲","💳","💴","💵","💶","💷","💸",
   "💹","💺","💻","💼","💽","💾","💿","📀","📁","📂","📃","📄","📅","📆","📇","📈","📉","📊","📋","📌","📍","📎",
   "📏","📐","📑","📒","📓","📔","📕","📖","📗","📘","📙","📚","📛","📜","📝","📞","📟","📠","📡","📢","📣","📤",
   "📥","📦","📧","📨","📩","📪","📫","📬","📭","📮","📯","📰","📱","📲","📳","📴","📵","📶","📷","📸","📹","📺",
   "📻","📼","📽","📿","🔀","🔁","🔂","🔃","🔄","🔅","🔆","🔇","🔈","🔉","🔊","🔋","🔌","🔍","🔎","🔏","🔐","🔑",
   "🔒","🔓","🔔","🔕","🔖","🔗","🔘","🔙","🔚","🔛","🔜","🔝","🔞","🔟","🔠","🔡","🔢","🔣","🔤","🔥","🔦","🔧",
   "🔨","🔩","🔪","🔫","🔬","🔭","🔮","🔯","🔰","🔱","🔲","🔳","🔴","🔵","🔶","🔷","🔸","🔹","🔺","🔻","🔼","🔽",
   "🕉","🕊","🕋","🕌","🕍","🕎","🕐","🕑","🕒","🕓","🕔","🕕","🕖","🕗","🕘","🕙","🕚","🕛","🕜","🕝","🕞","🕟",
   "🕠","🕡","🕢","🕣","🕤","🕥","🕦","🕧","🕯","🕰","🕳","🕴","🕵","🕶","🕷","🕸","🕹","🕺","🖇","🖊","🖋","🖌","🖍",
   "🖐","🖕","🖖","🖤","🖥","🖨","🖱","🖲","🖼","🗂","🗃","🗄","🗑","🗒","🗓","🗜","🗝","🗞","🗡","🗣","🗨","🗯","🗳","🗺",
   "🗻","🗼","🗽","🗾","🗿","😀","😁","😂","😃","😄","😅","😆","😇","😈","😉","😊","😋","😌","😍","😎","😏","😐",
   "😑","😒","😓","😔","😕","😖","😗","😘","😙","😚","😛","😜","😝","😞","😟","😠","😡","😢","😣","😤","😥","😦",
   "😧","😨","😩","😪","😫","😬","😭","😮","😯","😰","😱","😲","😳","😴","😵","😶","😷","😸","😹","😺","😻","😼",
   "😽","😾","😿","🙀","🙁","🙂","🙃","🙄","🙅","🙆","🙇","🙈","🙉","🙊","🙋","🙌","🙍","🙎","🙏","🚀","🚁","🚂",
   "🚃","🚄","🚅","🚆","🚇","🚈","🚉","🚊","🚋","🚌","🚍","🚎","🚏","🚐","🚑","🚒","🚓","🚔","🚕","🚖","🚗","🚘",
   "🚙","🚚","🚛","🚜","🚝","🚞","🚟","🚠","🚡","🚢","🚣","🚤","🚥","🚦","🚧","🚨","🚩","🚪","🚫","🚬","🚭","🚮",
   "🚯","🚰","🚱","🚲","🚳","🚴","🚵","🚶","🚷","🚸","🚹","🚺","🚻","🚼","🚽","🚾","🚿","🛀","🛁","🛂","🛃","🛄",
   "🛅","🛋","🛌","🛍","🛎","🛏","🛐","🛑","🛒","🛕","🛖","🛗","🛠","🛡","🛢","🛣","🛤","🛥","🛩","🛫","🛬","🛰","🛳",
   "🛴","🛵","🛶","🛷","🛸","🛹","🛺","🛻","🛼","🟠","🟡","🟢","🟣","🟤","🟥","🟦","🟧","🟨","🟩","🟪","🟫","🤌",
   "🤍","🤎","🤏","🤐","🤑","🤒","🤓","🤔","🤕","🤖","🤗","🤘","🤙","🤚","🤛","🤜","🤝","🤞","🤟","🤠","🤡","🤢",
   "🤣","🤤","🤥","🤦","🤧","🤨","🤩","🤪","🤫","🤬","🤭","🤮","🤯","🤰","🤱","🤲","🤳","🤴","🤵","🤶","🤷","🤸",
   "🤹","🤺","🤼","🤽","🤾","🤿","🥀","🥁","🥂","🥃","🥄","🥅","🥇","🥈","🥉","🥊","🥋","🥌","🥍","🥎","🥏","🥐",
   "🥑","🥒","🥓","🥔","🥕","🥖","🥗","🥘","🥙","🥚","🥛","🥜","🥝","🥞","🥟","🥠","🥡","🥢","🥣","🥤","🥥","🥦",
   "🥧","🥨","🥩","🥪","🥫","🥬","🥭","🥮","🥯","🥰","🥱","🥲","🥳","🥴","🥵","🥶","🥷","🥸","🥺","🥻","🥼","🥽",
   "🥾","🥿","🦀","🦁","🦂","🦃","🦄","🦅","🦆","🦇","🦈","🦉","🦊","🦋","🦌","🦍","🦎","🦏","🦐","🦑","🦒","🦓",
   "🦔","🦕","🦖","🦗","🦘","🦙","🦚","🦛","🦜","🦝","🦞","🦟","🦠","🦡","🦢","🦣","🦤","🦥","🦦","🦧","🦨","🦩",
   "🦪","🦫","🦬","🦭","🦮","🦯","🦰","🦱","🦲","🦳","🦴","🦵","🦶","🦷","🦸","🦹","🦺","🦻","🦼","🦽","🦾","🦿",
   "🧀","🧁","🧂","🧃","🧄","🧅","🧆","🧇","🧈","🧉","🧊","🧋","🧍","🧎","🧏","🧐","🧑","🧒","🧓","🧔","🧕","🧖",
   "🧗","🧘","🧙","🧚","🧛","🧜","🧝","🧞","🧟","🧠","🧡","🧢","🧣","🧤","🧥","🧦","🧧","🧨","🧩","🧪","🧫","🧬",
   "🧭","🧮","🧯","🧰","🧱","🧲","🧳","🧴","🧵","🧶","🧷","🧸","🧹","🧺","🧻","🧼","🧽","🧾","🧿","🩰","🩱","🩲",
   "🩳","🩴","🩸","🩹","🩺","🪀","🪁","🪂","🪃","🪄","🪅","🪆","🪐","🪑","🪒","🪓","🪔","🪕","🪖","🪗","🪘","🪙",
   "🪚","🪛","🪜","🪝","🪞","🪟","🪠","🪡","🪢","🪣","🪤","🪥","🪦","🪧","🪨","🪰","🪱","🪲","🪳","🪴","🪵","🪶",
   "🫀","🫁","🫂","🫐","🫑","🫒","🫓","🫔","🫕","🫖"]

for e in emoji_extra_1:
    if not e in emoji_lookup:
        emoji_lookup.append(e)
