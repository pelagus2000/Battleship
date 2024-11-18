import random

class Ship:
    def __init__(self, name, length):
        self.name = name
        self.length = length
        self.hits = 0
        self.positions = []

    def is_sunk(self):
        return self.hits >= self.length

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [['.' for _ in range(size)] for _ in range(size)]
        self.ships = []

    def add_ship(self, ship, start_row, start_col, orientation):
        if orientation == 'H':
            if start_col + ship.length > self.size:
                return False
            for i in range(ship.length):
                if self.grid[start_row][start_col + i] != '.':
                    return False
            for i in range(ship.length):
                ship.positions.append((start_row, start_col + i))
        elif orientation == 'V':
            if start_row + ship.length > self.size:
                return False
            for i in range(ship.length):
                if self.grid[start_row + i][start_col] != '.':
                    return False
            for i in range(ship.length):
                ship.positions.append((start_row + i, start_col))
        self.ships.append(ship)
        return True

    def place_ships_randomly(self, ships):
        for ship in ships:
            placed = False
            while not placed:
                start_row = random.randint(0, self.size - 1)
                start_col = random.randint(0, self.size - 1)
                orientation = random.choice(['H', 'V'])
                placed = self.add_ship(ship, start_row, start_col, orientation)

    def display(self):
        print("  " + " ".join(str(i) for i in range(self.size)))  # Print column headers
        for idx, row in enumerate(self.grid):
            print(f"{idx} " + " ".join(row))  # Print row index and row data
        print()

    def attack(self, row, col):
        if (row, col) in [pos for ship in self.ships for pos in ship.positions]:
            for ship in self.ships:
                if (row, col) in ship.positions:
                    ship.hits += 1
            self.grid[row][col] = 'H'  # Mark hit
            return True
        elif self.grid[row][col] == '.':
            self.grid[row][col] = 'M'  # Mark miss
            return False
        return None

class User:
    def __init__(self, name):
        self.name = name
        self.board = Board(6)

    def take_turn(self):
        while True:
            try:
                row = int(input(f"{self.name}, enter row (0-5): "))
                col = int(input(f"{self.name}, enter column (0-5): "))
                if 0 <= row < 6 and 0 <= col < 6:
                    return row, col
                else:
                    print("Invalid input. Please enter values between 0 and 5.")
            except ValueError:
                print("Invalid input. Please enter numbers only.")

class AI(User):
    def take_turn(self):
        return random.randint(0, 5), random.randint(0, 5)

def main():
    player = User("Player")
    ai = AI("AI")

    player_ships = [
        Ship("Battleship", 3),
        Ship("Cruiser1", 2),
        Ship("Cruiser2", 2),
        Ship("Destroyer1", 1),
        Ship("Destroyer2", 1),
        Ship("Destroyer3", 1)
    ]

    ai_ships = [
        Ship("Battleship", 3),
        Ship("Cruiser1", 2),
        Ship("Cruiser2", 2),
        Ship("Destroyer1", 1),
        Ship("Destroyer2", 1),
        Ship("Destroyer3", 1)
    ]

    player.board.place_ships_randomly(player_ships)
    ai.board.place_ships_randomly(ai_ships)

    while True:
        print("Player's Board:")
        player.board.display()
        print("AI's Board:")
        ai.board.display()

        # Player's turn
        while True:
            row, col = player.take_turn()
            result = ai.board.attack(row, col)
            if result is True:
                print("Hit!")
                if all(ship.is_sunk() for ship in ai.board.ships):
                    print("Player wins!")
                    return
            elif result is False:
                print("Miss!")
                break
            else:
                print("Already attacked this position!")

        # AI's turn
        while True:
            row, col = ai.take_turn()
            result = player.board.attack(row, col)
            if result is True:
                print("AI hit your ship!")
                if all(ship.is_sunk() for ship in player.board.ships):
                    print("AI wins!")
                    return
            elif result is False:
                print("AI missed!")
                break
            else:
                print("AI already attacked this position!")

if __name__ == "__main__":
    main()