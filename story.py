"""Setting, regions, characters and dialogue for The Number Thief of Arithmos."""

TITLE = "The Number Thief of Arithmos"

PROLOGUE = (
    "The kingdom of Arithmos woke up to a terrible surprise: **the numbers were gone!** "
    "Price signs were blank. Clocks had no hours. The bakers could not count their buns "
    "and the builders could not measure their walls.\n\n"
    "High on a snowy peak, a trickster dragon named **Zerix** is sitting on a glittering "
    "pile of stolen numbers. Six Number Gems hold the kingdom's math together, and "
    "Zerix's creatures guard every one.\n\n"
    "The Queen needs a hero who is brave, clever, and good at math. That hero is **you**.\n\n"
    "*The old folk say that dragons once lived down in the valley, among the people. "
    "Nobody seems to remember why they left.*"
)

# The friend who runs the speed trials.
TRIAL_HOST = {
    "kind": "trial",
    "name": "Pip the Firefly",
    "emoji": "🧚",
    "intro": "Trial time! There is no clock, so take your time.",
    "win": "Well done!",
}

# Story pages. They appear after the 1st gem, after the 3rd gem, and when the
# last gem before Dragon's Peak is won, in whatever order the regions are played.
BEATS = [
    {
        "title": "A scorched note",
        "art": "note",
        "text": "Tucked under the gem you find a scrap of paper, burnt at one corner.\n\n"
                "> *Sorry about the mess. I am still looking. — Z*\n\n"
                "Looking? Looking for **what**? A thief who says sorry is a very "
                "strange sort of thief.",
    },
    {
        "title": "A small shadow",
        "art": "nilla",
        "text": "Something has been following you. It sneezes, and a tiny puff of smoke "
                "gives it away. Out tumbles a small orange dragon.\n\n"
                "\"I'm Nilla,\" she says. \"Zerix is my big brother, and he is NOT a bad "
                "dragon! He didn't take the numbers to keep them. He is **checking** "
                "them. Every single one. He says that somewhere there is a number "
                "that is wrong, and it is the reason dragons have to live on the cold "
                "mountain. His creatures only guard the gems so that nobody takes the "
                "numbers away before he has finished.\"\n\n"
                "She looks down at her claws. \"I can only count to twelve, so I can't "
                "help him. Can you?\"",
    },
    {
        "title": "The Great Ledger",
        "art": "ledger",
        "text": "Sage Owlivia lands beside you. She looks ashamed.\n\n"
                "\"It is time you knew,\" she says. \"A hundred years ago, dragons were "
                "the counters of this kingdom. They kept the **Great Ledger**, the book "
                "of all our sums. Then one day the royal gold came out ten coins short. "
                "The people blamed the dragons and sent them away to the mountain.\"\n\n"
                "\"But I have always wondered. Dragons do not make mistakes in sums. "
                "What if the mistake was someone else's?\"\n\n"
                "Nilla tugs your sleeve. \"That's what Zerix is looking for! The wrong "
                "number!\"\n\n"
                "**The path to Dragon's Peak is open.**",
    },
]

HEALER = {
    "kind": "healer",
    "name": "Pip the Firefly Healer",
    "emoji": "🧚",
    "intro": "You look tired, hero! Answer my little riddle and I will share my glow-potion.",
    "win": "Drink up! You sparkle with new energy.",
}

SAGE_NAME = "Sage Owlivia"

REGIONS = [
    {
        "key": "village",
        "name": "Market Village",
        "emoji": "🏘️",
        "gem": "Gem of Sums",
        "topics": ["addition", "subtraction"],
        "intro": "The market is a mess. Nobody knows what anything costs, and sneaky "
                 "creatures are mixing up everyone's coins. Help the villagers add and "
                 "subtract their way back to order.",
        "outro": "The Tally Troll drops the Gem of Sums. Price signs all over the "
                 "market flicker back to life!",
        "memory": "Baker Bramble wipes her hands. 'My granny told me a dragon once "
                  "ran the big scales at this market. Ember, her name was. Granny "
                  "said she was very fair. I wonder where the dragons all went.'",
        "encounters": [
            {"kind": "riddle", "name": "Baker Bramble", "emoji": "🥖",
             "intro": "My price signs are blank! Help me count and my numbers will come back.",
             "win": "That's it! Have a warm bun for the road."},
            {"kind": "riddle", "name": "Tilly the Coin Counter", "emoji": "🪙",
             "intro": "I keep losing track of my coins. Can you work this out for me?",
             "win": "Every coin counted. Thank you, hero!"},
            {"kind": "fight", "name": "Sum Goblin", "emoji": "👺",
             "intro": "Hee hee! I scrambled all the sums. Bet you can't fix them!",
             "win": "The Sum Goblin yelps and runs off, dropping a bag of numbers."},
            {"kind": "task", "task": "coins", "name": "Peddler Pim", "emoji": "💰",
             "intro": "I can't make change without numbers! Pay me the exact price, please.",
             "win": "Clink, clink! Exactly right. Pleasure doing business."},
            {"kind": "riddle", "name": "Old Fisher Finn", "emoji": "🎣",
             "intro": "I've sold fish here for fifty years, and today I can't count one catch.",
             "win": "Ha! Sharp as a fish hook, you are."},
            {"kind": "fight", "name": "Minus Magpie", "emoji": "🐦",
             "intro": "Caw! I take things away. Shiny things. Number things!",
             "win": "The Minus Magpie flaps away, leaving its stolen shinies behind."},
            {"kind": "boss", "name": "The Tally Troll", "emoji": "👹",
             "intro": "NOBODY crosses my bridge without paying the toll... in ANSWERS!",
             "win": "The Tally Troll sits down with a thump. 'Fine. You count better than "
                    "me. Trolls always did get sleepy over their sums.'"},
        ],
    },
    {
        "key": "mines",
        "name": "Multiplication Mines",
        "emoji": "⛏️",
        "gem": "Gem of Times",
        "topics": ["multiplication"],
        "intro": "Deep under the hills, the miners can no longer count their carts of "
                 "crystals. Rows and rows of them! Only multiplication is fast enough.",
        "outro": "The Crystal Golem crumbles into sparkling dust, and the Gem of Times "
                 "lights up every tunnel.",
        "memory": "Digger Dot points down a tunnel far too wide for any miner. "
                  "'Dragons dug that one, long ago. They counted every crystal by "
                  "firelight. We still hang our lamps on their old hooks.'",
        "encounters": [
            {"kind": "riddle", "name": "Digger Dot", "emoji": "👷",
             "intro": "So many carts, so many crystals. Counting one by one takes forever!",
             "win": "Quick as a pickaxe! The carts are rolling again."},
            {"kind": "riddle", "name": "Lampkeeper Lux", "emoji": "🏮",
             "intro": "I need to know how many lamps to light. Help me work it out.",
             "win": "The tunnel glows. Onward, hero!"},
            {"kind": "fight", "name": "Times Bat", "emoji": "🦇",
             "intro": "Screeee! I swoop down and mix up your numbers. You'll never catch me!",
             "win": "The Times Bat zigzags away into the dark."},
            {"kind": "task", "task": "multiples", "name": "The Echo Cave", "emoji": "🕳️",
             "intro": "Hundreds of bats hang here, and each one carries a number. Catch the right ones!",
             "win": "The bats swirl away and drop a shower of crystals."},
            {"kind": "riddle", "name": "Cart-master Gus", "emoji": "🛒",
             "intro": "One more load to count before the deep tunnel. Ready?",
             "win": "Right on track! Mind the gap."},
            {"kind": "fight", "name": "Rock Grumbler", "emoji": "🪨",
             "intro": "GRRRUMBLE. Too many rocks for a little hero.",
             "win": "The Rock Grumbler rolls over and falls asleep."},
            {"kind": "boss", "name": "The Crystal Golem", "emoji": "🗿",
             "intro": "I AM BUILT FROM A THOUSAND CRYSTALS. CAN YOU COUNT THEM ALL?",
             "win": "Cracks race across the Golem. It bows, and breaks apart."},
        ],
    },
    {
        "key": "docks",
        "name": "Division Docks",
        "emoji": "⚓",
        "gem": "Gem of Shares",
        "topics": ["division"],
        "intro": "At the harbor, the sailors are arguing. Nobody can share the cargo "
                 "fairly without numbers. Divide it up before a fight breaks out!",
        "outro": "The Kraken sinks beneath the waves and the Gem of Shares bobs to "
                 "the surface. Fair shares for everyone!",
        "memory": "Captain Quotia taps the huge harbor scale. 'See those claw marks? "
                  "Dragons weighed the cargo here once. My grandfather said nobody "
                  "ever got cheated, back then.'",
        "encounters": [
            {"kind": "riddle", "name": "Captain Quotia", "emoji": "🧑‍✈️",
             "intro": "My crew is arguing over the cargo, and I've lost my numbers. Help me, sailor!",
             "win": "Fair and square! You'd make a fine first mate."},
            {"kind": "riddle", "name": "Net-mender Ned", "emoji": "🪢",
             "intro": "I've got fish for the boats and no numbers to count them. Can you help?",
             "win": "Every boat is happy. Thank you kindly!"},
            {"kind": "fight", "name": "Splitter Crab", "emoji": "🦀",
             "intro": "Snip snap! I snip the numbers off the crates. Stop me if you can!",
             "win": "The Splitter Crab scuttles sideways into the sea."},
            {"kind": "task", "task": "share", "name": "Dockmaster Della", "emoji": "🚢",
             "intro": "Crates everywhere! Load my boats fairly before the tide goes out.",
             "win": "Every boat sits level in the water. Cast off!"},
            {"kind": "riddle", "name": "Cook Remy", "emoji": "🍲",
             "intro": "A good cook wastes nothing. Help me with this kitchen sum.",
             "win": "Perfect portions! Have some stew."},
            {"kind": "fight", "name": "Remainder Eel", "emoji": "🐍",
             "intro": "Ssso many numbers! I gobble them all up. Even socks.",
             "win": "The Remainder Eel slips back under the dock."},
            {"kind": "boss", "name": "The Kraken of Shares", "emoji": "🐙",
             "intro": "EIGHT ARMS. ALL THE CARGO IS MINE!",
             "win": "The Kraken lets go of the ships, one arm at a time."},
        ],
    },
    {
        "key": "forest",
        "name": "Fraction Forest",
        "emoji": "🌲",
        "gem": "Gem of Parts",
        "topics": ["fractions"],
        "intro": "In this forest everything comes in pieces: half-moons, quarter-pies, "
                 "and paths that split into thirds. Only someone who understands "
                 "fractions can find the way through.",
        "outro": "The Piecemeal Wolf howls once and trots away. The Gem of Parts makes "
                 "the broken paths whole again.",
        "memory": "The Half-Moon Owl blinks slowly. 'I am old enough to remember the "
                  "Counting Fair. A dragon cut every pie, so that each child got an "
                  "equal piece. Those were good days, little hero.'",
        "encounters": [
            {"kind": "riddle", "name": "Pie-maker Penny", "emoji": "🥧",
             "intro": "I can't bake a thing without numbers! Help me with this one.",
             "win": "A perfect slice! Take one with you."},
            {"kind": "riddle", "name": "The Half-Moon Owl", "emoji": "🦉",
             "intro": "Whooo knows the answer? Show me, little hero.",
             "win": "Wise indeed. The path ahead is clear."},
            {"kind": "fight", "name": "Sliver Spider", "emoji": "🕷️",
             "intro": "I spin my web across the path. You'll get tangled in it!",
             "win": "The Sliver Spider scurries up its thread."},
            {"kind": "task", "task": "shade", "name": "Hazel the Squirrel Chef", "emoji": "🐿️",
             "intro": "My recipe needs just the right part of the nut loaf. Help me cut it!",
             "win": "Perfect! Not a crumb too many."},
            {"kind": "riddle", "name": "The Fawn of Fourths", "emoji": "🦌",
             "intro": "The stream splits into parts here. Which way? Answer and I'll show you.",
             "win": "This way! Follow me."},
            {"kind": "fight", "name": "Thorn Sprite", "emoji": "🌿",
             "intro": "Prickle, prickle! My thorns hide every answer. You can't have ANY of them!",
             "win": "The Thorn Sprite vanishes in a puff of leaves."},
            {"kind": "boss", "name": "The Piecemeal Wolf", "emoji": "🐺",
             "intro": "I creep through the trees and steal the numbers, one... by one... by one.",
             "win": "The Wolf tilts its head. 'You are sharper than you look. Go on.'"},
        ],
    },
    {
        "key": "castle",
        "name": "Castle Builders",
        "emoji": "🏰",
        "gem": "Gem of Measures",
        "topics": ["area_perimeter"],
        "intro": "The royal builders have stopped work. Without numbers they cannot "
                 "measure a wall or plan a room. Help them get building again.",
        "outro": "The empty armor of the Blueprint Knight clatters to the floor. The "
                 "Gem of Measures glows, and the castle walls stand straight again.",
        "memory": "Mason Marta looks up at the tower door. 'Far too tall for people, "
                  "isn't it? My great-grandmother said dragons helped to build this "
                  "castle. They carried the biggest stones.'",
        "encounters": [
            {"kind": "riddle", "name": "Mason Marta", "emoji": "🧱",
             "intro": "I need to measure before I build, and my ruler has gone blank. Help me work it out!",
             "win": "Measured twice, built once. Well done!"},
            {"kind": "riddle", "name": "Gardener Gwen", "emoji": "🌷",
             "intro": "The Queen's garden needs planting. Help me figure out the size.",
             "win": "The tulips will fit perfectly!"},
            {"kind": "fight", "name": "Fence Gremlin", "emoji": "😈",
             "intro": "I moved all the fences! Now nobody knows where anything goes!",
             "win": "The Fence Gremlin trips over its own fence and tumbles away."},
            {"kind": "task", "task": "garden", "name": "The Queen's New Garden", "emoji": "📐",
             "intro": "The Queen has ordered a new garden, and the plan is blank. Help Gwen lay it out!",
             "win": "The ropes are pegged out. It fits the plan exactly."},
            {"kind": "riddle", "name": "Royal Carpenter Cole", "emoji": "🪚",
             "intro": "One last room to floor before the tower. Give me a hand?",
             "win": "A perfect fit. The tower door is open."},
            {"kind": "fight", "name": "Moat Serpent", "emoji": "🐊",
             "intro": "Round and round the castle I swim. You'll never get past me!",
             "win": "The Moat Serpent dives deep and stays there."},
            {"kind": "boss", "name": "The Blueprint Knight", "emoji": "🛡️",
             "intro": "I GUARD EVERY PLAN OF THIS CASTLE. ONE WRONG ANSWER AND IT ALL FALLS.",
             "win": "The Knight's helmet nods. The armor was empty all along."},
        ],
    },
    {
        "key": "peak",
        "name": "Dragon's Peak",
        "emoji": "🏔️",
        "gem": "Gem of Wisdom",
        "topics": ["two_step"],
        "mix": True,
        "final": True,
        "intro": "The path climbs into the clouds. Up here the problems take more than "
                 "one step, and Zerix will test everything you have learned.",
        "outro": "One wrong sum. A sleepy troll, the Tally Troll's great-grandfather, "
                 "wrote it down a hundred years ago. The royal gold came out ten coins "
                 "short, and the dragons took the blame.\n\n"
                 "You carry the page down the mountain. The Queen reads it twice. Then "
                 "she does something no ruler of Arithmos has done in a hundred years: "
                 "she says **sorry** to a dragon.\n\n"
                 "Zerix's eyes go wide. With one great flap of his wings, every stolen "
                 "number flies home. Price signs light up. Clocks start to tick.\n\n"
                 "The dragons come back to the valley. Zerix is the new Royal "
                 "Riddle-Master, the Counting Fair is held again, and the Tally Troll "
                 "has promised to check his sums twice. As for Nilla, she starts "
                 "school on Monday. She can already count to thirteen.",
        "encounters": [
            {"kind": "riddle", "name": "Hermit Hale", "emoji": "🧙",
             "intro": "Up here the air is thin. Think slowly, hero, and you will get there.",
             "win": "Step by step. That is how mountains are climbed."},
            {"kind": "riddle", "name": "Gruff the Goat Guide", "emoji": "🐐",
             "intro": "Baaa! I'll lead you up the cliff if you can solve this.",
             "win": "Sure-footed AND sure-minded. Follow me!"},
            {"kind": "fight", "name": "Cloud Wisp", "emoji": "🌫️",
             "intro": "Whoooo... I fog up every thought. Can you still think clearly?",
             "win": "The Cloud Wisp thins out and drifts away."},
            {"kind": "riddle", "name": "Echo, the Last Gatekeeper", "emoji": "🚪",
             "intro": "One more riddle... riddle... riddle... before the dragon's door.",
             "win": "The gate swings open... open... open."},
            {"kind": "fight", "name": "The Dragon's Shadow", "emoji": "🌑",
             "intro": "I am only his shadow, and even I am tricky!",
             "win": "The Shadow shrinks to nothing in the morning light."},
            {"kind": "boss", "name": "Zerix the Number Thief", "emoji": "🐉",
             "hp": "final",
             "intro": "So! A hero at last. Let's see if you can out-riddle a DRAGON.",
             "win": "Zerix laughs, a real, happy laugh. 'Again! No... wait. You win. "
                    "Nobody ever stays to play riddles with me. Come, I must show you something.'"},
            {"kind": "task", "task": "ledger", "name": "Zerix and the Great Ledger", "emoji": "📖",
             "intro": "This is the page from the year we were sent away. I have checked ten "
                      "thousand numbers and my eyes are tired. Hero... will you look?",
             "win": "THERE! Zerix roars with joy. 'That line! Look at the big, smudgy "
                    "troll writing. It was never the dragons. It was one wrong sum, "
                    "all along!'"},
        ],
    },
]

REGION_BY_KEY = {r["key"]: r for r in REGIONS}

# The lines above fit any grade's topics. A grade file can add lines that name
# its topics (times, shares, fractions, perimeter) with [[region.encounter]]
# overrides. Only grade_4.toml restores the original topic lines; other grades
# use these neutral ones except where their file overrides a slot.
ENCOUNTER_FIELDS = ("name", "emoji", "intro", "win")


def shorten(encounters: list, limit: int | None) -> list:
    """Keep at most `limit` encounters, in story order. The boss and the
    hands-on task always stay; then the first friend, the first monster, and
    the rest from the start of the story."""
    if not limit or len(encounters) <= limit:
        return encounters
    must = [i for i, e in enumerate(encounters) if e["kind"] in ("boss", "task")]
    rest = [i for i in range(len(encounters)) if i not in must]
    firsts = []
    for kind in ("riddle", "fight"):
        firsts += [i for i in rest if encounters[i]["kind"] == kind][:1]
    order = must + firsts + [i for i in rest if i not in firsts]
    keep = sorted(order[:max(limit, len(must))])
    return [encounters[i] for i in keep]


def build_region(spec: dict, limit: int | None = None) -> dict:
    """Merge a grade file's [[region]] with the shared story for its map spot.

    The grade file gives the name, gem, topics and task, and may override the
    intro/outro/memory text and single encounters (by slot). Encounter
    characters and lines come from REGIONS above. A region without a task has
    no task encounter. `limit` shortens the story (see shorten).
    """
    base = REGION_BY_KEY[spec["key"]]
    region = dict(base)
    region.update({k: v for k, v in spec.items() if k != "encounter" and v is not None})
    encounters = [dict(e) for e in base["encounters"]]
    for ov in spec.get("encounter", []):
        slot = ov.get("slot", -1)
        if 0 <= slot < len(encounters):
            encounters[slot].update({k: ov[k] for k in ENCOUNTER_FIELDS if ov.get(k)})
    kept = []
    for e in encounters:
        if e["kind"] == "task":
            if not spec.get("task"):
                continue
            e["task"] = spec["task"]
        kept.append(e)
    region["encounters"] = shorten(kept, limit)
    return region
