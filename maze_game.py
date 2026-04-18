import random
import re
import unicodedata
from typing import List, Tuple, Set, Optional, Dict


# Synonyms for riddle answers
ANSWER_SYNONYMS = {
    'mountain': ['mountain', 'peak', 'summit', 'highland', 'mount', 'hill', 'range', 'ridge', 'crag', 'tor', 'massif', 'alp', 'elevation', 'height', 'eminence', 'prominence', 'knoll', 'peak', 'pinnacle', 'summit', 'apex'],
    'castle': ['castle', 'fortress', 'stronghold', 'keep', 'citadel', 'bastion', 'redoubt', 'tower', 'palace', 'mansion', 'fortification', 'rampart', 'bulwark', 'garrison', 'hold', 'fort', 'keep', 'donjon', 'fastness', 'strongpoint'],
    'dungeon': ['dungeon', 'prison', 'cell', 'vault', 'chamber', 'cavern', 'crypt', 'pit', 'hole', 'hold', 'oubliette', 'keep', 'tower', 'lock-up', 'lockup', 'jail', 'confinement', 'enclosure', 'underground', 'catacombs'],
    'forest': ['forest', 'wood', 'woods', 'woodland', 'grove', 'thicket', 'jungle', 'wilderness', 'wildwood', 'copse', 'stand', 'timber', 'timberland', 'greenwood', 'bush', 'brush', 'undergrowth', 'shrubbery', 'tree', 'arboretum'],
    'tree': ['tree', 'oak', 'elm', 'ash', 'pine', 'fir', 'spruce', 'cedar', 'birch', 'maple', 'beech', 'willow', 'timber', 'wood', 'plant', 'flora', 'sapling', 'trunk', 'growth', 'vegetation'],
    'wheat': ['wheat', 'grain', 'crop', 'cereal', 'barley', 'rye', 'oat', 'harvest', 'stalks', 'ears', 'kernels', 'corn', 'seed', 'produce', 'yield', 'bounty', 'golden', 'grain', 'bushel', 'sheaf'],
    'egg': ['egg', 'ovum', 'embryo', 'shell', 'clutch', 'oval', 'sphere', 'pod', 'capsule', 'treasure', 'golden', 'orb', 'nugget', 'jewel', 'gem', 'prize', 'find', 'fortune', 'bounty', 'riches'],
    'peanut': ['peanut', 'groundnut', 'arachis', 'nut', 'seed', 'walnut', 'hazelnut', 'almond', 'cashew', 'pistachio', 'pecan', 'brazil nut', 'macadamia', ],
    'ocean': ['ocean', 'sea', 'water', 'brine', 'tide', 'wave', 'deep', 'abyss', 'blue', 'waters', 'expanse', 'main', 'briny', 'saltwater', 'maritime', 'pelagic', 'vast', 'immense', 'boundless', 'infinite'],
    'wave': ['wave', 'ripple', 'undulation', 'surge', 'swell', 'breaker', 'whitecap', 'foam', 'tide', 'crest', 'billow', 'roll', 'sea', 'water', 'motion', 'movement', 'undulation', 'oscillation', 'fluctuation', 'rise'],
    'coast': ['coast', 'shore', 'beach', 'shoreline', 'strand', 'seashore', 'seaside', 'littoral', 'bank', 'margin', 'edge', 'boundary', 'border', 'waterfront', 'inlet', 'bay', 'cove', 'harbor', 'headland', 'breakwater'],
    'ice': ['ice', 'frost', 'freeze', 'crystalline', 'frozen', 'glacier', 'iceberg', 'icicle', 'crystal', 'sheet', 'block', 'floe', 'solid', 'cold', 'rigid', 'white', 'hard', 'brittle', 'slick', 'rime'],
    'snow': ['snow', 'flakes', 'powder', 'white', 'drift', 'blanket', 'sleet', 'frost', 'frozen', 'crystalline', 'precipitation', 'covering', 'mantle', 'shroud', 'layer', 'carpet', 'heap', 'mound', 'accumulation', 'fall'],
    'arctic': ['arctic', 'tundra', 'polar', 'frozen', 'wasteland', 'desolate', 'ice', 'north', 'frozen', 'barren', 'wilderness', 'waste', 'expanse', 'realm', 'region', 'zone', 'terrain', 'landscape', 'climate', 'terrain'],
}


def _normalize_answer_text(value: str) -> str:
    """Normalize free-form answer text for robust comparison."""
    text = unicodedata.normalize("NFKC", value)

    # Remove control characters that can break rendering/comparison.
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C")

    # Strip accents and normalize case.
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if unicodedata.category(ch) != "Mn"
    )
    text = text.casefold()

    # Keep only letters, numbers, and spaces.
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse repeated whitespace.
    text = " ".join(text.split())
    return text


def check_answer(user_input, correct_answer):
    """Durable answer matcher with normalization and input guards."""
    # Guard: handle missing values and wrong input types.
    if user_input is None or correct_answer is None:
        return False
    if not isinstance(user_input, str):
        return False

    # Guard: reject empty and excessively long payloads.
    if not user_input.strip() or len(user_input) > 100:
        return False

    normalized_user = _normalize_answer_text(user_input)
    if not normalized_user:
        return False

    # Accept either a single answer string or a collection of valid answers.
    if isinstance(correct_answer, str):
        candidates = [correct_answer]
    elif isinstance(correct_answer, (set, list, tuple)):
        candidates = [item for item in correct_answer if isinstance(item, str)]
    else:
        return False

    for candidate in candidates:
        normalized_candidate = _normalize_answer_text(candidate)
        if normalized_candidate and normalized_user == normalized_candidate:
            return True
    return False


class Tile:
    """Represents a single tile in the maze with a description and riddle."""
    
    def __init__(self, x: int, y: int, theme: str, description: str, riddle: str, answer: str):
        self.x = x
        self.y = y
        self.theme = theme
        self.description = description
        self.riddle = riddle
        self.answer = answer.lower()
        base_synonyms = ANSWER_SYNONYMS.get(answer.lower(), [answer.lower()])
        self.synonyms = [syn.lower() for syn in base_synonyms]
        self.visited = False
    
    def __repr__(self):
        return f"Tile({self.x}, {self.y}, {self.theme})"


class Dungeon:
    """Manages the dungeon grid and game logic."""
    
    THEMES = {
        'mountain': {
            'descriptions': [
                "Before you rises a towering peak, wreathed in mist and ancient stone. The slopes are barren and windswept, holding the memory of ages past.",
                "A great mountain dominates the horizon, its summit shrouded in clouds. Snow clings to the upper reaches, and the rock beneath is grey and timeless.",
                "The mountain looms majestically, its face carved by millennia of wind and weather. You feel small beneath its eternal gaze.",
            ],
            'riddles': [
                ("I am tall, silent, and ancient. I watch the world change below me. What am I?", "mountain"),
                ("I am born from fire and shaped by ice. I touch the clouds yet am rooted to the earth. What am I?", "mountain"),
                ("Worn by wind for countless ages, I stand higher than the birds can fly. What am I?", "mountain"),
            ]
        },
        'castle': {
            'descriptions': [
                "A great fortress of pale stone stands before you, its towers piercing the sky like a crown. Banners flutter from the battlements, and the walls seem to hold centuries of stories.",
                "An imposing castle rises before you, its walls thick and formidable. The gates are massive iron, forged in ages past. You sense the power that dwells within.",
                "The castle looms ahead, a masterwork of ancient architecture. Its stonework is intricate and beautiful, yet speaks of strength and unyielding defense.",
            ],
            'riddles': [
                ("I am built to protect, yet stand empty at times. Kings dwell within me, yet I have no heart. What am I?", "castle"),
                ("Stone upon stone, I am raised by the hands of many. I shelter the noble and the brave. What am I?", "castle"),
                ("With towers of might and gates of steel, I guard the realm and keep watch. What am I?", "castle"),
            ]
        },
        'dungeon': {
            'descriptions': [
                "You descend into darkness below stone. The air is cold and damp, and the walls weep with ancient moisture. Torches flicker in iron sconces, casting dancing shadows.",
                "Deep beneath the earth lies this sunken hall. Chains hang from the walls, and the sound of dripping water echoes endlessly. The stone is worn smooth by countless feet.",
                "A vast underground chamber unfolds before you, carved from the living rock. Pillars support the ceiling high above. The gloom is absolute save for your torchlight.",
            ],
            'riddles': [
                ("I am deep and dark, built beneath stone and earth. I hold secrets that fear the light of day. What am I?", "dungeon"),
                ("Deep in the rock, far from the sun, I am a prison of shadow and despair. What am I?", "dungeon"),
                ("Below the world, carved in stone, I hold the forgotten and the feared. What am I?", "dungeon"),
            ]
        },
        'forest': {
            'descriptions': [
                "An ancient forest stretches before you, where the trees are older than memory. Their trunks are vast and gnarled, and the canopy blocks out the sky entirely.",
                "The primordial woodland welcomes you with towering oaks and elms. Mushrooms ring the clearings, and the air is thick with the smell of loam and growing things.",
                "A forest of timeless beauty surrounds you. The trees seem almost sentient, their branches intertwining to form natural cathedrals. Moss and fern carpet the ground.",
            ],
            'riddles': [
                ("I am ancient and alive, home to creatures great and small. I breathe the world's air and drink the sky's tears. What am I?", "forest"),
                ("I am rooted yet free, I reach toward the heavens yet feed from the earth below. What am I?", "tree"),
                ("Dense and dark, I am a kingdom unto myself. Beasts dwell within me, and my heart is eternal. What am I?", "forest"),
            ]
        },
        'farmland': {
            'descriptions': [
                "Rolling fields of golden grain stretch to the horizon, swaying gently in the breeze. The earth here is rich and deep, nourishing countless growing things.",
                "Farmsteads dot the landscape, their stone walls weathered by seasons uncounted. Neat rows of crops march across the fields in orderly fashion. The soil here has fed generations.",
                "Vast acres of cultivated land spread before you. The smell of earth and growing things fills the air. Stone walls divide the fields, built by hands long turned to dust.",
            ],
            'riddles': [
                ("I have a pale smooth heart covered in skin. I grow beneath the earth. I keep my heart locked away for even a child would be driven to devour it. What am I?", "peanut"),
                ("This is a box without hinges, key or a lid, yet golden treasure inside is hid. What am I?", "egg"),
                ("Born of earth and sweat and sun, I nourish those who tend my kind. What am I?", "wheat"),
            ]
        },
        'coast': {
            'descriptions': [
                "The mighty ocean crashes upon white sand beaches. Cliffs of dark stone rise above the foam, carved by the relentless waves over countless millennia.",
                "Where land meets sea, you stand upon the threshold between two worlds. The waves roll endlessly, carrying the scent of salt and distant shores.",
                "A rocky coastline stretches before you, where the sea has worn strange shapes in the ancient stone. Seabirds wheel overhead, crying their wild songs.",
            ],
            'riddles': [
                ("I am never still, yet I am counted in tides. I am salt and vast, holding mysteries in my depths. What am I?", "ocean"),
                ("I am touched by the moon and move by her command. I crash upon stone and wear the land away. What am I?", "wave"),
                ("I am the boundary between two worlds, where stone gives way to endless water. What am I?", "coast"),
            ]
        },
        'arctic': {
            'descriptions': [
                "A desolate wasteland of white and grey spreads before you. Snow lies thick upon the ground, and the wind cuts like a blade. The cold is absolute and merciless.",
                "The frozen realm greets you with its austere beauty. Ice formations rise like crystal towers, and the sky is pale and endless. Few things stir in this white silence.",
                "An arctic expanse of snow and ice surrounds you. The landscape is beautiful in its emptiness, harsh in its indifference. The wind howls with the voice of ancient ages.",
            ],
            'riddles': [
                ("I am water made solid by the kiss of winter. I build great halls of ice and hold secrets for ages. What am I?", "ice"),
                ("White and cold, I fall from the sky and blanket the earth. I am the garment of winter. What am I?", "snow"),
                ("I am frozen and vast, a prison of winter where life sleeps. What am I?", "arctic"),
            ]
        },
    }
    
    def __init__(self, width: int = 6, height: int = 4):
        """Initialize a dungeon with the given dimensions (24 tiles total)."""
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = []
        self.adjacency: Dict[Tuple[int, int], Set[str]] = {}
        self.start_pos: Tuple[int, int] = (0, 0)
        self.end_pos: Tuple[int, int] = (width - 1, height - 1)
        self._generate_tiles()
        self._build_adjacency()
    
    def _generate_tiles(self):
        """Generate all tiles with descriptions and riddles."""
        themes_list = list(self.THEMES.keys())
        random.shuffle(themes_list)
        
        theme_idx = 0
        for y in range(self.height):
            row = []
            for x in range(self.width):
                theme = themes_list[theme_idx % len(themes_list)]
                desc_idx = random.randint(0, len(self.THEMES[theme]['descriptions']) - 1)
                riddle_idx = random.randint(0, len(self.THEMES[theme]['riddles']) - 1)
                
                description = self.THEMES[theme]['descriptions'][desc_idx]
                riddle, answer = self.THEMES[theme]['riddles'][riddle_idx]
                
                tile = Tile(x, y, theme, description, riddle, answer)
                row.append(tile)
                theme_idx += 1
            self.tiles.append(row)

    def _build_adjacency(self) -> None:
        """Build a connected maze that satisfies gameplay path constraints."""
        moves = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }
        opposite = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
        }

        best_adjacency: Optional[Dict[Tuple[int, int], Set[str]]] = None

        # Retry generation until both game rules are satisfied.
        for _ in range(250):
            adjacency: Dict[Tuple[int, int], Set[str]] = {
                (x, y): set()
                for y in range(self.height)
                for x in range(self.width)
            }

            # Step 1: carve a spanning tree so all tiles are reachable.
            start = self.start_pos
            visited: Set[Tuple[int, int]] = {start}
            stack: List[Tuple[int, int]] = [start]

            while stack:
                x, y = stack[-1]
                unvisited_neighbors: List[Tuple[str, int, int]] = []

                for direction, (dx, dy) in moves.items():
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height and (nx, ny) not in visited:
                        unvisited_neighbors.append((direction, nx, ny))

                if not unvisited_neighbors:
                    stack.pop()
                    continue

                direction, nx, ny = random.choice(unvisited_neighbors)
                adjacency[(x, y)].add(direction)
                adjacency[(nx, ny)].add(opposite[direction])
                visited.add((nx, ny))
                stack.append((nx, ny))

            # Step 2: open extra passages to create alternate routes.
            possible_extra_edges: List[Tuple[int, int, str, int, int]] = []
            for y in range(self.height):
                for x in range(self.width):
                    if x + 1 < self.width and 'east' not in adjacency[(x, y)]:
                        possible_extra_edges.append((x, y, 'east', x + 1, y))
                    if y + 1 < self.height and 'south' not in adjacency[(x, y)]:
                        possible_extra_edges.append((x, y, 'south', x, y + 1))

            random.shuffle(possible_extra_edges)
            extra_to_open = min(len(possible_extra_edges), random.randint(2, 6))
            for x, y, direction, nx, ny in possible_extra_edges[:extra_to_open]:
                adjacency[(x, y)].add(direction)
                adjacency[(nx, ny)].add(opposite[direction])

            best_adjacency = adjacency
            has_multiple_exit_paths = self._count_paths_to_exit(adjacency, limit=2) >= 2
            no_tiles_gated_by_exit = self._all_non_exit_reachable_without_exit(adjacency)

            if has_multiple_exit_paths and no_tiles_gated_by_exit:
                self.adjacency = adjacency
                return

        # Fallback to the best attempt if constraints weren't met in retries.
        self.adjacency = best_adjacency or {
            (x, y): set()
            for y in range(self.height)
            for x in range(self.width)
        }

    def _count_paths_to_exit(
        self,
        adjacency: Dict[Tuple[int, int], Set[str]],
        limit: int = 2,
    ) -> int:
        """Count distinct simple paths from start to exit up to a limit."""
        moves = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }

        start = self.start_pos
        end = self.end_pos

        def dfs(pos: Tuple[int, int], visited: Set[Tuple[int, int]]) -> int:
            if pos == end:
                return 1

            total = 0
            x, y = pos
            for direction in adjacency.get(pos, set()):
                dx, dy = moves[direction]
                nxt = (x + dx, y + dy)
                if nxt in visited:
                    continue
                visited.add(nxt)
                total += dfs(nxt, visited)
                visited.remove(nxt)
                if total >= limit:
                    return total
            return total

        return dfs(start, {start})

    def _all_non_exit_reachable_without_exit(
        self,
        adjacency: Dict[Tuple[int, int], Set[str]],
    ) -> bool:
        """Return True when all non-exit tiles are reachable without crossing exit."""
        moves = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }

        start = self.start_pos
        end = self.end_pos
        seen: Set[Tuple[int, int]] = {start}
        queue: List[Tuple[int, int]] = [start]

        while queue:
            x, y = queue.pop(0)
            for direction in adjacency.get((x, y), set()):
                dx, dy = moves[direction]
                nxt = (x + dx, y + dy)
                if nxt == end or nxt in seen:
                    continue
                seen.add(nxt)
                queue.append(nxt)

        required = (self.width * self.height) - 1
        return len(seen) == required
    
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get a tile at the given coordinates, or None if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None
    
    def can_move(self, x: int, y: int, direction: str) -> bool:
        """Check if movement in a direction is valid."""
        return direction in self.adjacency.get((x, y), set())
    
    def move(self, x: int, y: int, direction: str) -> Tuple[int, int]:
        """Move in a direction and return the new coordinates."""
        moves = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }
        
        dx, dy = moves[direction]
        return x + dx, y + dy


class Game:
    """Main game loop and player interaction."""

    ANSI_RESET = "\033[0m"
    ANSI_GRAY = "\033[90m"
    ANSI_DARK_GRAY = "\033[38;5;240m"
    ANSI_DARK_GREEN = "\033[32m"
    ANSI_LIGHT_GREEN = "\033[92m"
    ANSI_YELLOW = "\033[33m"
    ANSI_BRIGHT_YELLOW = "\033[93m"
    ANSI_BLUE = "\033[34m"
    ANSI_LIGHT_BLUE = "\033[94m"
    ANSI_CYAN = "\033[96m"
    ANSI_WHITE = "\033[97m"
    ANSI_BLACK = "\033[30m"
    ANSI_PURPLE = "\033[35m"
    ANSI_BG_GRAY = "\033[100m"
    ANSI_BG_DARK_GRAY = "\033[48;5;238m"
    ANSI_BG_LIGHT_GREEN = "\033[102m"
    ANSI_BG_LIGHT_BROWN = "\033[48;5;180m"
    ANSI_BG_LIGHT_BLUE = "\033[104m"
    ANSI_BG_WHITE = "\033[107m"
    ANSI_BG_WALL = "\033[48;5;240m"
    
    def __init__(self):
        self.dungeon = Dungeon()
        self.player_x = self.dungeon.start_pos[0]
        self.player_y = self.dungeon.start_pos[1]
        self.visited_tiles: Set[Tuple[int, int]] = set()
        self.tiles_visited_count = 0
        self.game_won = False
        self.correct_answers = 0
        self.total_questions = 0
    
    def format_exits(self, exits: List[str]) -> str:
        """Format a list of exits into natural language."""
        if not exits:
            return "No exits available."
        elif len(exits) == 1:
            return f"Exits lie to the {exits[0]}."
        elif len(exits) == 2:
            return f"Exits lie to the {exits[0]} and {exits[1]}."
        else:
            # Join all but the last with commas, then add "and" before the last
            return f"Exits lie to the {', '.join(exits[:-1])} and {exits[-1]}."
    
    def display_tile(self):
        """Display the current tile's description and riddle."""
        tile = self.dungeon.get_tile(self.player_x, self.player_y)
        if tile is None:
            print("\nThis room could not be loaded. Try another move.")
            return

        pos = (self.player_x, self.player_y)
        
        if pos not in self.visited_tiles:
            self.visited_tiles.add(pos)
            self.tiles_visited_count += 1
        
        print("\n" + "="*70)
        print(f"Location: [{self.player_x}, {self.player_y}] - {tile.theme.upper()}")
        print("="*70)
        print(f"\n{tile.description}\n")
        
        # Display available exits
        available_exits = self.get_available_moves()
        print(self.format_exits(available_exits) + "\n")

        # Show the explored dungeon layout every turn.
        self.show_map()
        
        print(f"Tiles visited: {self.tiles_visited_count}/24")
        print("-"*70)
    
    def ask_riddle(self) -> bool:
        """Ask the player a riddle and check their answer."""
        tile = self.dungeon.get_tile(self.player_x, self.player_y)
        if tile is None:
            print("This room cannot be read right now. Try moving again.")
            return False

        self.total_questions += 1
        
        print(f"\nRIDDLE: {tile.riddle}")
        player_answer = input("Your answer: ")
        
        # Create a set of acceptable answers including plurals
        acceptable_answers = {syn for syn in tile.synonyms}
        # Add plural forms of all synonyms (case-insensitive)
        for synonym in tile.synonyms:
            acceptable_answers.add(synonym + 's')
        
        # Check if answer matches any acceptable form
        if check_answer(player_answer, acceptable_answers):
            print("✓ Correct! You may proceed.")
            self.correct_answers += 1
            return True
        else:
            print(f"✗ Incorrect. The answer was: {tile.answer}")
            print("You must answer correctly to move on.")
            return False

    def _terrain_symbol(self, x: int, y: int) -> str:
        """Return the symbol used for a discovered tile's terrain."""
        tile = self.dungeon.get_tile(x, y)
        if tile is None:
            return "#"

        if tile.theme == 'mountain':
            return "▲"
        if tile.theme == 'forest':
            return "▼"
        if tile.theme == 'farmland':
            return ";"
        if tile.theme == 'coast':
            return "{" if x == 0 else "}"
        if tile.theme == 'arctic':
            return "-"
        if tile.theme == 'castle':
            return '"'
        if tile.theme == 'dungeon':
            return "●"
        return "?"

    def _color_symbol(self, symbol: str) -> str:
        """Return ANSI-colored symbol text for the map legend and grid."""
        if symbol == "#":
            return f"{self.ANSI_DARK_GRAY}#{self.ANSI_RESET}"
        if symbol == "*":
            return f"{self.ANSI_PURPLE}*{self.ANSI_RESET}"
        if symbol == "E":
            return "E"
        if symbol == "▲":
            return f"{self.ANSI_WHITE}{self.ANSI_BG_DARK_GRAY}▲{self.ANSI_RESET}"
        if symbol == "▼":
            return f"{self.ANSI_LIGHT_GREEN}{self.ANSI_BG_LIGHT_GREEN}▼{self.ANSI_RESET}"
        if symbol == ";":
            return f"\033[93;48;5;180m;{self.ANSI_RESET}"
        if symbol in ("{", "}"):
            return f"\033[96;104m{symbol}{self.ANSI_RESET}"
        if symbol == "-":
            return f"\033[96;107m-{self.ANSI_RESET}"
        if symbol == '"':
            return f"{self.ANSI_YELLOW}{self.ANSI_BG_GRAY}\"{self.ANSI_RESET}"
        if symbol == "●":
            return f"{self.ANSI_BLACK}{self.ANSI_BG_GRAY}●{self.ANSI_RESET}"
        return symbol

    def _wall_symbol(self) -> str:
        """Return a dull, uniform wall square."""
        return f"{self.ANSI_BG_WALL}■{self.ANSI_RESET}"

    def _tile_display_symbol(self, x: int, y: int) -> str:
        """Return the display symbol for a tile position."""
        pos = (x, y)
        if pos == (self.player_x, self.player_y):
            return self._color_symbol("*")
        if pos == self.dungeon.end_pos:
            return self._color_symbol("E")
        if pos in self.visited_tiles:
            return self._color_symbol(self._terrain_symbol(x, y))
        return self._color_symbol("#")
    
    def show_map(self):
        """Show an expanded dungeon map with visible walls."""
        print(f"\nDungeon Layout ({self.dungeon.width}x{self.dungeon.height}):")
        print(
            f"{self._color_symbol('#')} = Unexplored, "
            f"{self._color_symbol('*')} = You, "
            f"{self._color_symbol('E')} = Exit"
        )
        print(f"{self._wall_symbol()} = Wall")
        print(
            f"{self._color_symbol('▲')} = Mountain (white on dark gray), "
            f"{self._color_symbol('▼')} = Forest (light green on light green), "
            f"{self._color_symbol(';')} = Farmland (yellow on light brown)"
        )
        print(
            f"{self._color_symbol('{')} = West Coast (cyan on light blue), "
            f"{self._color_symbol('}')} = East Coast (cyan on light blue), "
            f"{self._color_symbol('-')} = Arctic (cyan on white)"
        )
        print(
            f"{self._color_symbol('\"')} = Castle (yellow text on gray), "
            f"{self._color_symbol('●')} = Dungeon (black on gray)\n"
        )

        # Expanded map dimensions include wall cells between tiles and border walls.
        render_height = self.dungeon.height * 2 + 1
        render_width = self.dungeon.width * 2 + 1

        for ry in range(render_height):
            for rx in range(render_width):
                if ry % 2 == 1 and rx % 2 == 1:
                    x = rx // 2
                    y = ry // 2
                    print(self._tile_display_symbol(x, y), end=" ")
                elif ry % 2 == 0 and rx % 2 == 0:
                    print(self._wall_symbol(), end=" ")
                elif ry % 2 == 0:
                    x = rx // 2
                    if ry == 0 or ry == render_height - 1:
                        print(self._wall_symbol(), end=" ")
                    else:
                        upper_y = (ry // 2) - 1
                        if 'south' in self.dungeon.adjacency.get((x, upper_y), set()):
                            print(" ", end=" ")
                        else:
                            print(self._wall_symbol(), end=" ")
                else:
                    y = ry // 2
                    if rx == 0 or rx == render_width - 1:
                        print(self._wall_symbol(), end=" ")
                    else:
                        left_x = (rx // 2) - 1
                        if 'east' in self.dungeon.adjacency.get((left_x, y), set()):
                            print(" ", end=" ")
                        else:
                            print(self._wall_symbol(), end=" ")
            print()
        print()
    
    def get_available_moves(self) -> List[str]:
        """Get list of valid moves from current position."""
        exits = self.dungeon.adjacency.get((self.player_x, self.player_y), set())
        return sorted(exits)
    
    def handle_movement(self, direction_input: Optional[str] = None) -> bool:
        """Handle player movement. Returns True if successful."""
        valid_moves = self.get_available_moves()

        # Use provided direction (from main loop) or prompt if not provided
        if direction_input is None:
            direction_input = input("Move (north/south/east/west or 'map'): ").strip().lower()
        else:
            direction_input = direction_input.strip().lower()

        alias = {'n': 'north', 's': 'south', 'e': 'east', 'w': 'west'}
        direction = alias.get(direction_input, direction_input)

        if direction == 'map':
            self.show_map()
            return self.handle_movement()

        if direction not in valid_moves:
            print("You cannot move in that direction.")
            return False

        # Ask riddle before moving
        if not self.ask_riddle():
            return False

        self.player_x, self.player_y = self.dungeon.move(self.player_x, self.player_y, direction)
        return True
    
    def check_win_condition(self) -> bool:
        """Check if player has reached the end and visited enough tiles."""
        at_end = (self.player_x, self.player_y) == self.dungeon.end_pos
        enough_tiles = self.tiles_visited_count >= 10
        
        return at_end and enough_tiles
    
    def play(self):
        """Main game loop."""
        print("\n" + "="*70)
        print("WELCOME TO THE MAZE OF RIDDLES")
        print("="*70)
        print("\nYou find yourself at the entrance of a mystical dungeon.")
        print("To escape, you must reach the far end of the dungeon and answer")
        print("the riddles posed by each chamber. You must visit at least 10 tiles")
        print("to complete your journey.")
        print("\nCommands: north, south, east, west, map, quit")
        print("="*70)
        
        self.display_tile()
        
        while not self.game_won:
            try:
                command = input("\nWhat do you do? > ").strip().lower()
                
                if command == 'quit':
                    print("\nYou abandon your quest. Farewell, traveler.")
                    break
                elif command == 'map':
                    self.show_map()
                elif command in ['north', 'south', 'east', 'west', 'n', 's', 'e', 'w']:
                    if self.handle_movement(command):
                        self.display_tile()
                        
                        if self.check_win_condition():
                            self.game_won = True
                            self.show_victory()
                else:
                    print("I do not understand that command.")
            
            except KeyboardInterrupt:
                print("\n\nYou slip away into the shadows. Farewell.")
                break
    
    def show_victory(self):
        """Display victory message."""
        print("\n" + "="*70)
        print("VICTORY!")
        print("="*70)
        print(f"\nYou have escaped the dungeon and found your way to freedom!")
        print(f"\nJourney Statistics:")
        print(f"  Tiles Visited: {self.tiles_visited_count}/24")
        print(f"  Riddles Answered Correctly: {self.correct_answers}/{self.total_questions}")
        accuracy = (self.correct_answers / self.total_questions * 100) if self.total_questions > 0 else 0
        print(f"  Accuracy: {accuracy:.1f}%")
        print("\n" + "="*70)


if __name__ == "__main__":
    game = Game()
    game.play()
