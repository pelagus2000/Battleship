import os
from random import randrange

class FieldPart(object):
    main = 'map'
    radar = 'radar'

class Cell(object):
    empty_cell = ' '
    ship_cell = '\u25a0'
    destroyed_ship = 'X'
    damaged_ship = '\u25a1'
    miss_cell = '\u2022'

class Field(object):
    def __init__(self, size):
        self.size = size
        self.map = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]
        self.radar = [[Cell.empty_cell for _ in range(size)] for _ in range(size)]

    def get_field_part(self, element):
        if element == FieldPart.main:
            return self.map
        if element == FieldPart.radar:
            return self.radar

    def draw_field(self, element, label):
        field = self.get_field_part(element)
        print(f"{label}:")
        print("  " + " ".join(str(i) for i in range(self.size)))
        for x in range(self.size):
            line = str(x) + ' ' + ' '.join(str(field[x][y]) for y in range(self.size))
            print(line.strip())
        print()

    def check_ship_fits(self, ship):
        if ship.x + ship.height > self.size or ship.x < 0 or \
                ship.y + ship.width > self.size or ship.y < 0:
            return False

        # Check for touching ships, including an empty cell around
        for p_x in range(ship.x - 1, ship.x + ship.height + 1):
            for p_y in range(ship.y - 1, ship.y + ship.width + 1):
                if (0 <= p_x < self.size) and (0 <= p_y < self.size):
                    if str(self.map[p_x][p_y]) != Cell.empty_cell:
                        return False
        return True

    def add_ship_to_field(self, ship):
        for p_x in range(ship.x, ship.x + ship.height):
            for p_y in range(ship.y, ship.y + ship.width):
                self.map[p_x][p_y] = ship

    def count_destroyed_ships(self):
        return sum(row.count(Cell.destroyed_ship) for row in self.map)

class Game(object):
    letters = ("A", "B", "C", "D", "E", "F")
    ships_rules = [3, 2, 2, 1, 1, 1, 1]  # Ship sizes from largest to smallest
    field_size = len(letters)

    def __init__(self):
        self.players = []
        self.current_player = None
        self.next_player = None
        self.status = 'prepare'

    def start_game(self):
        if len(self.players) < 2:
            raise ValueError("Not enough players to start the game.")
        self.current_player = self.players[0]
        self.next_player = self.players[1]

    def add_player(self, player):
        player.field = Field(Game.field_size)
        self.ships_setup(player)
        self.players.append(player)

    def ships_setup(self, player):
        for ship_size in Game.ships_rules:
            ship = Ship(ship_size, 0, 0, 0)

            placed = False
            attempts = 0
            while not placed and attempts < 70:
                # Randomly set position and rotation
                ship.set_rotation(randrange(2))  # Random rotation (0 or 1)
                ship.set_position(randrange(0, Game.field_size), randrange(0, Game.field_size), ship.rotation)
                placed = player.field.check_ship_fits(ship)
                attempts += 1

            if not placed:
                print(f"Failed to place ship of size {ship_size} after 70 attempts.")
                print("Instructions: Restart the game.")
                input("Press Enter to restart...")
                return

            player.field.add_ship_to_field(ship)
            player.ships.append(ship)  # Ensure the ship is added to the player's ship list

        # Verify if all ships are placed after attempting to place each ship
        if len(player.ships) != len(Game.ships_rules):
            print("Not all ships were placed.")
            print("Instructions: Restart the game.")
            input("Press Enter to restart...")

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

class Player(object):
    def __init__(self, name):
        self.name = name
        self.ships = []
        self.field = None
        self.shots_taken = set()  # To track shots made by the player

    def make_shot(self, target_player):
        while True:
            if self.name == 'Player1':
                x, y = self.get_input_move()  # Get input move from Player1
            else:
                x, y = self.get_random_shot()  # Random shot for AI

            if (x, y) in self.shots_taken:
                print("You've hit this cell previously. Please choose another coordinates.")
                continue  # Prompt for new coordinates

            self.shots_taken.add((x, y))  # Mark the shot as taken
            return target_player.receive_shot((x, y))

    def get_input_move(self):
        while True:
            user_input = input(f"{self.name}, enter your move (e.g., 0 0): ").strip()
            coords = user_input.split()
            if len(coords) != 2 or not all(c.isdigit() for c in coords):
                print("Invalid input. Please enter valid coordinates (e.g., 0 0).")
                continue

            x, y = int(coords[0]), int(coords[1])  # Convert to integers

            if x < 0 or x >= Game.field_size or y < 0 or y >= Game.field_size:
                print("Invalid input. Coordinates must be between 0 and 5.")
                continue

            return x, y

    def get_random_shot(self):
        x = randrange(0, Game.field_size)
        y = randrange(0, Game.field_size)
        return x, y

    def receive_shot(self, shot):
        sx, sy = shot
        if isinstance(self.field.map[sx][sy], Ship):
            ship = self.field.map[sx][sy]
            ship.hp -= 1
            if ship.hp <= 0:
                # Mark ship as destroyed and replace all damaged ships with destroyed ships
                for x in range(Game.field_size):
                    for y in range(Game.field_size):
                        if isinstance(self.field.map[x][y], Ship) and self.field.map[x][y] == ship:
                            self.field.map[x][y] = Cell.destroyed_ship
                self.ships.remove(ship)  # Remove the ship from the list
                return 'kill'
            self.field.map[sx][sy] = Cell.damaged_ship
            return 'hit'
        else:
            self.field.map[sx][sy] = Cell.miss_cell
            return 'miss'

class Ship:
    def __init__(self, size, x, y, rotation):
        self.size = size
        self.hp = size
        self.x = x
        self.y = y
        self.rotation = rotation
        self.set_rotation(rotation)

    def set_position(self, x, y, r):
        self.x = x
        self.y = y
        self.set_rotation(r)

    def set_rotation(self, r):
        self.rotation = r
        if self.rotation == 0:  # Horizontal
            self.width = self.size
            self.height = 1
        elif self.rotation == 1:  # Vertical
            self.width = 1
            self.height = self.size

    def __str__(self):
        return Cell.ship_cell  # Return the representation of the ship

def play_game():
    players = []
    players.append(Player(name='Player1'))
    players.append(Player(name='AI'))

    game = Game()

    # Add both players to the game before starting
    for player in players:
        game.add_player(player)

    # Ensure both players have all ships placed before starting the game
    for player in game.players:
        while len(player.ships) != len(Game.ships_rules):
            player.ships = []  # Clear previous ships
            player.field = Field(Game.field_size)  # Reset the field
            game.ships_setup(player)

    # Start the game
    game.start_game()

    print('\nWelcome to the Battleship game v.1.0.\n'
          'You need to enter 2 parameters:\n'
          '0-5 at y-axis space 0-5 at x-axis. \n'
          'You will see following designated signes:\n'
          'miss_cell = "\u2022"\n'
          'ship afloat = "\u25a0"\n'
          'damaged ship = "\u25a1"\n'
          'ship sunk last cell = "X"\n'
          'Your ships are at the top field\n'
          'Your enemy is in the bottom\n'
          'SINK ALL SHIPS! GOOD LUCK!\n')

    # Display the fields
    while True:
        game.current_player.field.draw_field(FieldPart.main, "My ships")

        # Prepare AI field for display
        ai_field_for_display = [[Cell.empty_cell for _ in range(Game.field_size)] for _ in range(Game.field_size)]
        for x in range(Game.field_size):
            for y in range(Game.field_size):
                if isinstance(game.next_player.field.map[x][y], Ship):
                    continue  # Do not show AI's ships
                ai_field_for_display[x][y] = game.next_player.field.map[x][y]

        # Manually draw the AI field
        print("AI field:")
        print("  " + " ".join(str(i) for i in range(Game.field_size)))
        for x in range(Game.field_size):
            line = str(x) + ' ' + ' '.join(str(ai_field_for_display[x][y]) for y in range(Game.field_size))
            print(line.strip())
        print()

        result = game.current_player.make_shot(game.next_player)

        # Check for win condition for both players using the radar field
        if game.current_player.field.count_destroyed_ships() >= len(game.ships_rules):
            print(f"All ships are sunk! {game.next_player.name} wins!")
            game.current_player.field.draw_field(FieldPart.main, "Winner - final position")
            game.next_player.field.draw_field(FieldPart.main, "Looser -final position")
            break
        if game.next_player.field.count_destroyed_ships() >= len(game.ships_rules):
            print(f"All ships are sunk! {game.current_player.name} wins!")
            game.next_player.field.draw_field(FieldPart.main, "Winner -final position")
            game.current_player.field.draw_field(FieldPart.main, "Loser - final position")
            break
        if result == 'miss':
            print("Missed!")
            # Switch players if it's a miss
            game.current_player, game.next_player = game.next_player, game.current_player
        elif result == 'hit':
            print("Hit! You get another turn.")
            # Player gets another turn
            continue
        elif result == 'kill':
            print("You sunk the enemy ship! You get another turn.")
            # Player gets another turn
            continue

def main():
    while True:
        play_game()
        restart = input("Do you want to play again? (y/n): ").strip().lower()
        if restart != 'y':
            print("Thanks for playing!")
            break

if __name__ == '__main__':
    main()