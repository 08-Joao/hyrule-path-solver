import tkinter as tk
import random
from noise import pnoise2
from PIL import Image, ImageTk

ROWS, COLS = 42, 42
CELL_SIZE = 15

TERRAIN_TYPES = {0: "Água", 1: "Areia", 2: "Grama", 3: "Floresta", 4: "Montanha"}
COLORS = {0: "#1e90ff", 1: "#f4e19c", 2: "#66cc66", 3: "#228b22", 4: "#8b4513"}

class MapEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Mapa com Dungeons e Seed")
        
        self.canvas = tk.Canvas(root, width=COLS*CELL_SIZE, height=ROWS*CELL_SIZE)
        self.canvas.pack(side=tk.LEFT)
        
        self.map_data = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.selected_terrain = 2  # Grama por padrão
        self.current_seed = None
        
        # Carregar imagem da dungeon door
        img = Image.open("dungeon-door.png").resize((CELL_SIZE, CELL_SIZE))
        self.door_image = ImageTk.PhotoImage(img)
        
        # Lista para armazenar onde estão as portas
        self.dungeon_doors = []
        
        frame = tk.Frame(root)
        frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(frame, text="Terrenos").pack()
        for t in TERRAIN_TYPES:
            tk.Button(frame, text=TERRAIN_TYPES[t], bg=COLORS[t],
                      command=lambda val=t: self.select_terrain(val)).pack(fill=tk.X)
        
        tk.Label(frame, text="Seed atual:").pack()
        self.seed_entry = tk.Entry(frame)
        self.seed_entry.pack(fill=tk.X)
        
        self.seed_label = tk.Label(frame, text="Nenhuma")
        self.seed_label.pack()
        
        tk.Button(frame, text="Copiar Seed", command=self.copy_seed).pack(fill=tk.X)
        
        tk.Button(frame, text="Gerar Mapa", command=self.generate_map).pack(fill=tk.X)
        
        self.draw_map()
        
        self.canvas.bind("<Button-1>", self.paint_cell)
        self.canvas.bind("<B1-Motion>", self.paint_cell)
    
    def select_terrain(self, terrain):
        self.selected_terrain = terrain
    
    def generate_map(self):
        # Sempre gerar uma seed aleatória
        seed = random.randint(0, 999999)
        self.current_seed = seed
        
        # Atualizar UI com a nova seed
        self.seed_entry.delete(0, tk.END)
        self.seed_entry.insert(0, str(seed))
        self.seed_label.config(text=f"Seed atual: {seed}")
        
        # Usar seed para deslocamento no Perlin
        offset_x = seed % 10000
        offset_y = (seed // 10000) % 10000
        
        scale = 20.0
        for r in range(ROWS):
            for c in range(COLS):
                height = pnoise2((r+offset_x)/scale, (c+offset_y)/scale, octaves=4)
                height = (height + 0.5)
                if height < 0.3:
                    self.map_data[r][c] = 0  # Água
                elif height < 0.4:
                    self.map_data[r][c] = 1  # Areia
                elif height < 0.6:
                    self.map_data[r][c] = 2  # Grama
                elif height < 0.8:
                    self.map_data[r][c] = 3  # Floresta
                else:
                    self.map_data[r][c] = 4  # Montanha
        
        # Colocar portas de dungeon em blocos de areia
        self.place_dungeon_doors(num_doors=3)  # Define quantas portas
    
        self.draw_map()
    
    def place_dungeon_doors(self, num_doors=1):
        self.dungeon_doors.clear()
        sand_positions = [(r, c) for r in range(ROWS) for c in range(COLS) if self.map_data[r][c] == 1]
        
        if len(sand_positions) == 0:
            return
        
        random.shuffle(sand_positions)
        
        for i in range(min(num_doors, len(sand_positions))):
            pos = sand_positions[i]
            self.dungeon_doors.append(pos)
    
    def copy_seed(self):
        if self.current_seed is not None:
            self.root.clipboard_clear()
            self.root.clipboard_append(str(self.current_seed))
            self.root.update()
    
    def draw_map(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                self.draw_cell(r, c)
        
        # Desenhar as dungeon doors por cima
        for (r, c) in self.dungeon_doors:
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            self.canvas.create_image(x, y, image=self.door_image, anchor="nw")
    
    def draw_cell(self, r, c):
        color = COLORS[self.map_data[r][c]]
        x1 = c * CELL_SIZE
        y1 = r * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
    
    def paint_cell(self, event):
        c = event.x // CELL_SIZE
        r = event.y // CELL_SIZE
        if 0 <= r < ROWS and 0 <= c < COLS:
            if self.map_data[r][c] != self.selected_terrain:
                self.map_data[r][c] = self.selected_terrain
                self.draw_cell(r, c)
                # Se pintar por cima da porta, removemos a porta
                if (r, c) in self.dungeon_doors:
                    self.dungeon_doors.remove((r, c))

if __name__ == "__main__":
    root = tk.Tk()
    app = MapEditor(root)
    root.mainloop()
