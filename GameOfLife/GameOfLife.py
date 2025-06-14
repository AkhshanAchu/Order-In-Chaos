import pygame
import numpy as np
import random
import sys
import json


pygame.init()

BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GRAY = (60, 60, 60)
LIGHT_GRAY = (100, 100, 100)
GREEN = (76, 175, 80)
RED = (244, 67, 54)
BLUE = (33, 150, 243)
ORANGE = (255, 152, 0)
PURPLE = (156, 39, 176)

class GameOfLife:
    def __init__(self):
        self.width = 1200
        self.height = 800
        self.control_height = 120
        self.grid_width = 50
        self.grid_height = 40
        self.cell_size = 15
        self.running = False
        self.speed = 100  # milliseconds between generations
        self.generation = 0
        self.population = 0
        
        # Initialize display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game of Life")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.score = pygame.font.Font(None, 22)
        
        # Grid setup
        self.grid = np.zeros((self.grid_height, self.grid_width), dtype=int)
        self.next_grid = np.zeros((self.grid_height, self.grid_width), dtype=int)
        
        # UI elements
        self.buttons = self.create_buttons()
        self.input_boxes = self.create_input_boxes()
        self.selected_pattern = "Random"
        
        self.calculate_grid_size()
        
    def create_buttons(self):
        buttons = []
        y_start = 10
        button_width = 80
        button_height = 30
        spacing = 10
        
        button_data = [
            ("Start", GREEN, 10),
            ("Stop", RED, 100),
            ("Step", ORANGE, 190),
            ("Clear", GRAY, 280),
            ("Random", BLUE, 370),
            ("Apply Grid", PURPLE, 460)
        ]
        
        for text, color, x in button_data:
            buttons.append({
                'rect': pygame.Rect(x, y_start, button_width, button_height),
                'color': color,
                'text': text,
                'active': False
            })
        
        return buttons
    
    def create_input_boxes(self):
        input_boxes = []
        y_pos = 50
        
        # Grid dimensions
        input_boxes.append({
            'rect': pygame.Rect(10, y_pos, 60, 25),
            'text': str(self.grid_width),
            'active': False,
            'label': 'Width:'
        })
        
        input_boxes.append({
            'rect': pygame.Rect(100, y_pos, 60, 25),
            'text': str(self.grid_height),
            'active': False,
            'label': 'Height:'
        })
        
        # Speed control
        input_boxes.append({
            'rect': pygame.Rect(200, y_pos, 60, 25),
            'text': str(self.speed),
            'active': False,
            'label': 'Speed(ms):'
        })
        
        return input_boxes
    
    def calculate_grid_size(self):
        available_width = self.width - 20
        available_height = self.height - self.control_height - 20
        
        cell_width = available_width // self.grid_width
        cell_height = available_height // self.grid_height
        
        self.cell_size = min(cell_width, cell_height, 20)  # Max cell size of 20
        self.cell_size = max(self.cell_size, 3)  # Min cell size of 3
        
        # Calculate grid offset for centering
        self.grid_x = (self.width - self.grid_width * self.cell_size) // 2
        self.grid_y = self.control_height + (self.height - self.control_height - self.grid_height * self.cell_size) // 2
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check button clicks
                for i, button in enumerate(self.buttons):
                    if button['rect'].collidepoint(mouse_pos):
                        self.handle_button_click(button['text'])
                
                # Check input box clicks
                for box in self.input_boxes:
                    box['active'] = box['rect'].collidepoint(mouse_pos)
            
                
                # Check grid clicks for manual cell placement
                if not self.running:
                    grid_x = (mouse_pos[0] - self.grid_x) // self.cell_size
                    grid_y = (mouse_pos[1] - self.grid_y) // self.cell_size
                    
                    if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
                        self.grid[grid_y, grid_x] = 1 - self.grid[grid_y, grid_x]  # Toggle cell
            
            elif event.type == pygame.KEYDOWN:
                # Handle input box typing
                for box in self.input_boxes:
                    if box['active']:
                        if event.key == pygame.K_BACKSPACE:
                            box['text'] = box['text'][:-1]
                        elif event.unicode.isdigit():
                            box['text'] += event.unicode
                
                # Keyboard shortcuts
                if event.key == pygame.K_SPACE:
                    self.toggle_simulation()
                elif event.key == pygame.K_r:
                    self.randomize_grid()
                elif event.key == pygame.K_c:
                    self.clear_grid()
                elif event.key == pygame.K_s:
                    self.step()
        
        return True
    
    def handle_button_click(self, button_text):
        if button_text == "Start":
            self.running = True
        elif button_text == "Stop":
            self.running = False
        elif button_text == "Step":
            self.step()
        elif button_text == "Clear":
            self.clear_grid()
        elif button_text == "Random":
            self.randomize_grid()
        elif button_text == "Apply Grid":
            self.apply_grid_settings()
    
    def apply_grid_settings(self):
        """Apply new grid dimensions and speed settings"""
        try:
            new_width = int(self.input_boxes[0]['text'])
            new_height = int(self.input_boxes[1]['text'])
            new_speed = int(self.input_boxes[2]['text'])
            
            # Validate inputs
            new_width = max(10, min(200, new_width))
            new_height = max(10, min(150, new_height))
            new_speed = max(1, min(2000, new_speed))
            
            self.grid_width = new_width
            self.grid_height = new_height
            self.speed = new_speed
            
            # Recreate grids
            self.grid = np.zeros((self.grid_height, self.grid_width), dtype=int)
            self.next_grid = np.zeros((self.grid_height, self.grid_width), dtype=int)
            
            # Recalculate grid size
            self.calculate_grid_size()
            
            # Reset simulation
            self.running = False
            self.generation = 0
            
            # Apply selected pattern
            if self.selected_pattern != "Random":
                self.apply_pattern(self.selected_pattern)
            
        except ValueError:
            pass  # Invalid input, ignore
    
    def apply_pattern(self, pattern_name):
        """Apply a predefined pattern to the grid"""
        self.clear_grid()
        self.randomize_grid()
    
    def toggle_simulation(self):
        self.running = not self.running
    
    def clear_grid(self):
        self.grid.fill(0)
        self.generation = 0
        self.running = False
    
    def randomize_grid(self):
        self.grid = np.random.choice([0, 1], size=(self.grid_height, self.grid_width), p=[0.7, 0.3])
        self.generation = 0
    
    def count_neighbors(self, x, y):
        """Count living neighbors for a cell"""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    count += self.grid[ny, nx]
        return count
    
    def step(self):
        """Perform one generation step"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                neighbors = self.count_neighbors(x, y)
                current_cell = self.grid[y, x]
                
                # Conway's rules
                if current_cell == 1:  # Alive
                    if neighbors < 2 or neighbors > 3:
                        self.next_grid[y, x] = 0  # Dies
                    else:
                        self.next_grid[y, x] = 1  # Lives
                else:  # Dead
                    if neighbors == 3:
                        self.next_grid[y, x] = 1  # Born
                    else:
                        self.next_grid[y, x] = 0  # Stays dead
        
        # Swap grids
        self.grid, self.next_grid = self.next_grid, self.grid
        self.generation += 1
        self.population = np.sum(self.grid)
    
    def draw_ui(self):
        """Draw the user interface"""
        # Control panel background
        pygame.draw.rect(self.screen, (40, 40, 40), (0, 0, self.width, self.control_height))
        
        # Draw buttons
        for button in self.buttons:
            color = button['color'] if not button['active'] else tuple(min(255, c + 30) for c in button['color'])
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, WHITE, button['rect'], 2)
            
            text_surf = self.small_font.render(button['text'], True, WHITE)
            text_rect = text_surf.get_rect(center=button['rect'].center)
            self.screen.blit(text_surf, text_rect)
        
        # Draw input boxes
        for box in self.input_boxes:
            color = LIGHT_GRAY if box['active'] else GRAY
            pygame.draw.rect(self.screen, color, box['rect'])
            pygame.draw.rect(self.screen, WHITE, box['rect'], 2)
            
            # Label
            label_surf = self.small_font.render(box['label'], True, WHITE)
            self.screen.blit(label_surf, (box['rect'].x, box['rect'].y + 40))
            
            # Text
            text_surf = self.small_font.render(box['text'], True, WHITE)
            self.screen.blit(text_surf, (box['rect'].x + 5, box['rect'].y + 5))
        
        # Draw stats
        stats_text = f"Generation: {self.generation}  |  Population: {self.population}  |  Status: {'Running' if self.running else 'Paused'}"
        stats_surf = self.score.render(stats_text, True, WHITE)
        self.screen.blit(stats_surf, (450, 100))
        
        # Draw instructions
        instructions = "Space: Play/Pause  |  R: Random  |  C: Clear  |  S: Step  |  Click cells to toggle"
        instr_surf = self.small_font.render(instructions, True, LIGHT_GRAY)
        self.screen.blit(instr_surf, (750, 40))
    
    def draw_grid(self):
        """Draw the game grid"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(
                    self.grid_x + x * self.cell_size,
                    self.grid_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                
                if self.grid[y, x] == 1:
                    pygame.draw.rect(self.screen, WHITE, rect)
                else:
                    pygame.draw.rect(self.screen, BLACK, rect)
                
                # Draw grid lines for larger cells
                if self.cell_size > 5:
                    pygame.draw.rect(self.screen, GRAY, rect, 1)
    
    def run(self):
        """Main game loop"""
        last_update = 0
        
        while True:
            current_time = pygame.time.get_ticks()
            
            if not self.handle_events():
                break
            
            # Update simulation
            if self.running and current_time - last_update > self.speed:
                self.step()
                last_update = current_time
            
            # Update population count
            self.population = np.sum(self.grid)
            
            # Draw everything
            self.screen.fill(BLACK)
            self.draw_grid()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = GameOfLife()
    game.run()