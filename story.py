"""Setting, regions, characters and dialogue for The Number Thief of Arithmos."""

TITLE = "The Number Thief of Arithmos"

PROLOGUE = (
    "The kingdom of Arithmos woke up to a terrible surprise: **the numbers were gone!** "
    "Price signs were blank. Clocks had no hours. The bakers could not count their buns "
    "and the builders could not measure their walls.\n\n"
    "High on a snowy peak, a trickster dragon named **Zerix** is sitting on a glittering "
    "pile of stolen numbers. Six Number Gems hold the kingdom's math together, and "
    "Zerix's creatures guard every one.\n\n"
    "The Queen needs a hero who is brave, clever, and good at math. That hero is **you**."
)

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
        "name": "Market Village",
        "emoji": "🏘️",
        "gem": "Gem of Sums",
        "topics": ["addition", "subtraction"],
        "intro": "The market is a mess. Nobody knows what anything costs, and sneaky "
                 "creatures are mixing up everyone's coins. Help the villagers add and "
                 "subtract their way back to order.",
        "outro": "The Tally Troll drops the Gem of Sums. Price signs all over the "
                 "market flicker back to life!",
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
            {"kind": "riddle", "name": "Old Fisher Finn", "emoji": "🎣",
             "intro": "I've sold fish here for fifty years, and today I can't count one catch.",
             "win": "Ha! Sharp as a fish hook, you are."},
            {"kind": "fight", "name": "Minus Magpie", "emoji": "🐦",
             "intro": "Caw! I take things away. Shiny things. Number things!",
             "win": "The Minus Magpie flaps away, leaving its stolen shinies behind."},
            {"kind": "boss", "name": "The Tally Troll", "emoji": "👹",
             "intro": "NOBODY crosses my bridge without paying the toll... in ANSWERS!",
             "win": "The Tally Troll sits down with a thump. 'Fine. You count better than me.'"},
        ],
    },
    {
        "name": "Multiplication Mines",
        "emoji": "⛏️",
        "gem": "Gem of Times",
        "topics": ["multiplication"],
        "intro": "Deep under the hills, the miners can no longer count their carts of "
                 "crystals. Rows and rows of them! Only multiplication is fast enough.",
        "outro": "The Crystal Golem crumbles into sparkling dust, and the Gem of Times "
                 "lights up every tunnel.",
        "encounters": [
            {"kind": "riddle", "name": "Digger Dot", "emoji": "👷",
             "intro": "So many carts, so many crystals. Counting one by one takes forever!",
             "win": "Quick as a pickaxe! The carts are rolling again."},
            {"kind": "riddle", "name": "Lampkeeper Lux", "emoji": "🏮",
             "intro": "I need to know how many lamps to light. Help me multiply.",
             "win": "The tunnel glows. Onward, hero!"},
            {"kind": "fight", "name": "Times Bat", "emoji": "🦇",
             "intro": "Screeee! I flap in groups. How many of us are there? You'll never know!",
             "win": "The Times Bat zigzags away into the dark."},
            {"kind": "riddle", "name": "Cart-master Gus", "emoji": "🛒",
             "intro": "One more load to count before the deep tunnel. Ready?",
             "win": "Right on track! Mind the gap."},
            {"kind": "fight", "name": "Rock Grumbler", "emoji": "🪨",
             "intro": "GRRRUMBLE. Rocks times rocks. Too many for a little hero.",
             "win": "The Rock Grumbler rolls over and falls asleep."},
            {"kind": "boss", "name": "The Crystal Golem", "emoji": "🗿",
             "intro": "I AM BUILT FROM A THOUSAND CRYSTALS. CAN YOU COUNT THEM ALL?",
             "win": "Cracks race across the Golem. It bows, and breaks apart."},
        ],
    },
    {
        "name": "Division Docks",
        "emoji": "⚓",
        "gem": "Gem of Shares",
        "topics": ["division"],
        "intro": "At the harbor, the sailors are arguing. Nobody can share the cargo "
                 "fairly without numbers. Divide it up before a fight breaks out!",
        "outro": "The Kraken sinks beneath the waves and the Gem of Shares bobs to "
                 "the surface. Fair shares for everyone!",
        "encounters": [
            {"kind": "riddle", "name": "Captain Quotia", "emoji": "🧑‍✈️",
             "intro": "My crew wants equal shares, and I've lost my numbers. Help me, sailor!",
             "win": "Fair and square! You'd make a fine first mate."},
            {"kind": "riddle", "name": "Net-mender Ned", "emoji": "🪢",
             "intro": "I've got fish to split between the boats. How many each?",
             "win": "Every boat is happy. Thank you kindly!"},
            {"kind": "fight", "name": "Splitter Crab", "emoji": "🦀",
             "intro": "Snip snap! I split things UNFAIRLY. Stop me if you can!",
             "win": "The Splitter Crab scuttles sideways into the sea."},
            {"kind": "riddle", "name": "Cook Remy", "emoji": "🍲",
             "intro": "A good cook wastes nothing. Tell me about the shares and the leftovers.",
             "win": "Perfect portions! Have some stew."},
            {"kind": "fight", "name": "Remainder Eel", "emoji": "🐍",
             "intro": "Sssso many leftoversss. I eat them all. And sssometimes sssocks.",
             "win": "The Remainder Eel slips back under the dock."},
            {"kind": "boss", "name": "The Kraken of Shares", "emoji": "🐙",
             "intro": "EIGHT ARMS. EIGHT SHARES. ALL OF THEM MINE!",
             "win": "The Kraken lets go of the ships, one arm at a time."},
        ],
    },
    {
        "name": "Fraction Forest",
        "emoji": "🌲",
        "gem": "Gem of Parts",
        "topics": ["fractions"],
        "intro": "In this forest everything comes in pieces: half-moons, quarter-pies, "
                 "and paths that split into thirds. Only someone who understands "
                 "fractions can find the way through.",
        "outro": "The Piecemeal Wolf howls once and trots away. The Gem of Parts makes "
                 "the broken paths whole again.",
        "encounters": [
            {"kind": "riddle", "name": "Pie-maker Penny", "emoji": "🥧",
             "intro": "I can't slice my pies fairly anymore! Help me with the pieces.",
             "win": "A perfect slice! Take one with you."},
            {"kind": "riddle", "name": "The Half-Moon Owl", "emoji": "🦉",
             "intro": "Whooo knows their fractions? Show me, little hero.",
             "win": "Wise indeed. The path ahead is clear."},
            {"kind": "fight", "name": "Sliver Spider", "emoji": "🕷️",
             "intro": "I cut my web into tiny, tiny parts. You'll get tangled in them!",
             "win": "The Sliver Spider scurries up its thread."},
            {"kind": "riddle", "name": "The Fawn of Fourths", "emoji": "🦌",
             "intro": "The stream splits into parts here. Which way? Answer and I'll show you.",
             "win": "This way! Follow me."},
            {"kind": "fight", "name": "Thorn Sprite", "emoji": "🌿",
             "intro": "A piece of this, a piece of that. You can't have ANY of it!",
             "win": "The Thorn Sprite vanishes in a puff of leaves."},
            {"kind": "boss", "name": "The Piecemeal Wolf", "emoji": "🐺",
             "intro": "I never take the whole. I take it bit... by bit... by bit.",
             "win": "The Wolf tilts its head. 'You see the whole AND the parts. Go on.'"},
        ],
    },
    {
        "name": "Castle Builders",
        "emoji": "🏰",
        "gem": "Gem of Measures",
        "topics": ["area_perimeter"],
        "intro": "The royal builders have stopped work. Without numbers they cannot "
                 "measure a wall or fence a garden. Help them with area and perimeter.",
        "outro": "The empty armor of the Blueprint Knight clatters to the floor. The "
                 "Gem of Measures glows, and the castle walls stand straight again.",
        "encounters": [
            {"kind": "riddle", "name": "Mason Marta", "emoji": "🧱",
             "intro": "I need to measure before I build, and my ruler has gone blank. Help me work it out!",
             "win": "Measured twice, built once. Well done!"},
            {"kind": "riddle", "name": "Gardener Gwen", "emoji": "🌷",
             "intro": "The Queen's garden needs planting. Help me figure out the size.",
             "win": "The tulips will fit perfectly!"},
            {"kind": "fight", "name": "Fence Gremlin", "emoji": "😈",
             "intro": "I moved all the fences! Now nobody knows how far around anything is!",
             "win": "The Fence Gremlin trips over its own fence and tumbles away."},
            {"kind": "riddle", "name": "Royal Carpenter Cole", "emoji": "🪚",
             "intro": "One last room to floor before the tower. Give me a hand?",
             "win": "A perfect fit. The tower door is open."},
            {"kind": "fight", "name": "Moat Serpent", "emoji": "🐊",
             "intro": "Round and round the castle I swim. How far is it? I'll never tell!",
             "win": "The Moat Serpent dives deep and stays there."},
            {"kind": "boss", "name": "The Blueprint Knight", "emoji": "🛡️",
             "intro": "I GUARD EVERY PLAN OF THIS CASTLE. MEASURE WRONG AND IT ALL FALLS.",
             "win": "The Knight's helmet nods. The armor was empty all along."},
        ],
    },
    {
        "name": "Dragon's Peak",
        "emoji": "🏔️",
        "gem": "Gem of Wisdom",
        "topics": ["two_step"],
        "mix": True,
        "intro": "The path climbs into the clouds. Up here the problems take more than "
                 "one step, and Zerix will test everything you have learned.",
        "outro": "Zerix lowers his huge head. 'You answered every riddle,' he says "
                 "quietly. 'Nobody ever stays to play with me. I only took the numbers "
                 "so that someone would come looking.'\n\n"
                 "You smile. 'Then come down to the kingdom. Arithmos needs a Royal "
                 "Riddle-Master.'\n\n"
                 "Zerix's eyes go wide. With one great flap of his wings, every stolen "
                 "number flies home.",
        "encounters": [
            {"kind": "riddle", "name": "Hermit Hale", "emoji": "🧙",
             "intro": "Up here, one step is never enough. Take two. Think slowly.",
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
             "win": "Zerix laughs, a real, happy laugh. 'Again! No... wait. You win.'"},
        ],
    },
]
