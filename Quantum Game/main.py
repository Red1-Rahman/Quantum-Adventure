import pygame
import random
from qiskit import QuantumCircuit
from qiskit_aer import Aer, AerSimulator
from qiskit.result import Result

# Quantum utility functions

# Cache the backend for efficiency
_q_backend = AerSimulator()

def quantum_random_int(max_value):
    """Generate a quantum random integer in [0, max_value)."""
    n_qubits = max_value.bit_length()
    while True:
        qc = QuantumCircuit(n_qubits)
        qc.h(range(n_qubits))
        qc.measure_all()
        job = _q_backend.run(qc, shots=1)
        result = job.result()
        counts = result.get_counts()
        value = int(list(counts.keys())[0], 2)
        if value < max_value:
            return value

def quantum_random_int_batch(max_value, batch_size):
    """Generate a batch of quantum random integers in [0, max_value)."""
    n_qubits = max_value.bit_length()
    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    qc.measure_all()
    job = _q_backend.run(qc, shots=batch_size)
    result = job.result()
    counts = result.get_counts()
    values = []
    for key in counts:
        value = int(key, 2)
        if value < max_value:
            values.extend([value] * counts[key])
    return values[:batch_size]

def quantum_maze_visibility(size, start=(0,0), goal=None):
    """Return a 2D grid of booleans for path visibility using quantum superposition. Ensures start and goal are open."""
    if goal is None:
        goal = (size//2, size//2)
    grid = []
    for y in range(size):
        row = []
        qc = QuantumCircuit(size)
        qc.h(range(size))
        qc.measure_all()
        job = _q_backend.run(qc, shots=1)
        result = job.result()
        bits = list(result.get_counts().keys())[0]
        for x, bit in enumerate(bits[::-1]):
            row.append(bit == '1')
        grid.append(row)
    # Ensure start and goal are open
    sx, sy = start
    gx, gy = goal
    grid[sy][sx] = True
    grid[gy][gx] = True
    return grid

def entangled_move(pos1, pos2, move, grid_size):
    """Return new positions for two entangled characters given a move (dx, dy)."""
    x1, y1 = pos1
    x2, y2 = pos2
    dx, dy = move
    # Mirror move for entanglement
    new_pos1 = (max(0, min(grid_size-1, x1 + dx)), max(0, min(grid_size-1, y1 + dy)))
    new_pos2 = (max(0, min(grid_size-1, x2 - dx)), max(0, min(grid_size-1, y2 - dy)))
    return new_pos1, new_pos2

# Main game class
class QuantumAdventureGame:
    def __init__(self, grid_size=10):
        pygame.init()
        self.grid_size = grid_size
        self.cell_size = min(60, max(20, 600 // grid_size))  # Dynamically size cells for a 600x600 window
        self.window_size = (self.grid_size * self.cell_size, self.grid_size * self.cell_size)
        self.screen = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption('Quantum Adventure Game')
        self.clock = pygame.time.Clock()
        self.enemy_move_delay = 5  # Delay in frames for enemy movement
        self.enemy_move_counter = 0
        self.reset_game()

    def reset_game(self):
        self.goal = (self.grid_size//2, self.grid_size//2)
        self.maze = quantum_maze_visibility(self.grid_size, start=(0,0), goal=self.goal)
        self.player1_pos = (0, 0)
        self.player2_pos = (self.grid_size-1, self.grid_size-1)
        self.enemies = [self.random_empty_cell() for _ in range(3)]
        self.running = True

    def random_empty_cell(self):
        while True:
            x = quantum_random_int(self.grid_size)
            y = quantum_random_int(self.grid_size)
            if self.maze[y][x] and (x, y) not in [self.player1_pos, self.player2_pos, self.goal]:
                return (x, y)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                    return
                move = None
                if event.key == pygame.K_UP:
                    move = (0, -1)
                elif event.key == pygame.K_DOWN:
                    move = (0, 1)
                elif event.key == pygame.K_LEFT:
                    move = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    move = (1, 0)
                if move:
                    self.move_players(move)

    def move_players(self, move):
        new_pos1, new_pos2 = entangled_move(self.player1_pos, self.player2_pos, move, self.grid_size)
        if self.is_valid(new_pos1):
            self.player1_pos = new_pos1
        if self.is_valid(new_pos2):
            self.player2_pos = new_pos2

    def is_valid(self, pos):
        x, y = pos
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size and self.maze[y][x]

    def update(self):
        # Increment the enemy move counter
        self.enemy_move_counter += 1
        if self.enemy_move_counter >= self.enemy_move_delay:
            self.enemy_move_counter = 0  # Reset counter
            # Perform enemy movement
            new_enemies = []
            for ex, ey in self.enemies:
                move = random.choice([(0,1),(0,-1),(1,0),(-1,0),(0,0)])
                nx, ny = ex + move[0], ey + move[1]
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.maze[ny][nx]:
                    new_enemies.append((nx, ny))
                else:
                    new_enemies.append((ex, ey))
            self.enemies = new_enemies

    def draw(self):
        self.screen.fill((0,0,0))
        offset_x = (self.screen.get_width() - self.grid_size * self.cell_size) // 2
        offset_y = (self.screen.get_height() - self.grid_size * self.cell_size) // 2
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rect = pygame.Rect(offset_x + x*self.cell_size, offset_y + y*self.cell_size, self.cell_size, self.cell_size)
                color = (50,50,50) if not self.maze[y][x] else (200,200,200)
                pygame.draw.rect(self.screen, color, rect)
        # Draw goal
        gx, gy = self.goal
        pygame.draw.rect(self.screen, (0,255,0), pygame.Rect(offset_x + gx*self.cell_size, offset_y + gy*self.cell_size, self.cell_size, self.cell_size))
        # Draw players
        px1, py1 = self.player1_pos
        px2, py2 = self.player2_pos
        pygame.draw.rect(self.screen, (0,0,255), pygame.Rect(offset_x + px1*self.cell_size, offset_y + py1*self.cell_size, self.cell_size, self.cell_size))
        pygame.draw.rect(self.screen, (255,0,255), pygame.Rect(offset_x + px2*self.cell_size, offset_y + py2*self.cell_size, self.cell_size, self.cell_size))
        # Draw enemies
        for ex, ey in self.enemies:
            pygame.draw.rect(self.screen, (255,0,0), pygame.Rect(offset_x + ex*self.cell_size, offset_y + ey*self.cell_size, self.cell_size, self.cell_size))
        pygame.display.flip()

    def check_game_over(self):
        if self.player1_pos == self.goal or self.player2_pos == self.goal:
            self.show_end_screen("You win! Press R to restart or Q to quit.")
            self.running = False
        if self.player1_pos in self.enemies or self.player2_pos in self.enemies:
            self.show_end_screen("Game Over! Press R to restart or Q to quit.")
            self.running = False

    def show_end_screen(self, message):
        font = pygame.font.SysFont(None, 36)
        text = font.render(message, True, (255,255,255))
        rect = text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(text, rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()  # Restart the game
                        waiting = False
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        exit()

    def show_instructions(self):
        instructions = [
            "Quantum Adventure Game",
            "",
            "Use the arrow keys to move the blue player",
            "The pink player is quantum entangled and moves in mirrored directions",
            "Avoid the red enemies",
            "Try to reach the green goal with either player",
            "The maze paths (white squares) are generated using quantum superposition",
            "The enemy movements are random walks",
            "The game ends when either:",
            "- One of the players reaches the goal (you win!)",
            "- One of the players collides with an enemy (game over)",
            "",
            "Press any key to start..."
        ]
        self.screen.fill((0,0,0))
        font = pygame.font.SysFont(None, 32)
        for i, line in enumerate(instructions):
            text = font.render(line, True, (255,255,255))
            rect = text.get_rect(center=(self.screen.get_width()//2, 40 + i*36))
            self.screen.blit(text, rect)
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    waiting = False

    def run(self):
        self.show_instructions()
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.check_game_over()
            self.clock.tick(10)

if __name__ == "__main__":
    game = QuantumAdventureGame()
    game.run()
