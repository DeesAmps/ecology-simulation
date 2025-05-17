import pygame
from entities.vegetation import Vegetation
from entities.herbivore import Herbivore
from entities.carnivore import Carnivore

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text

    def draw(self, surf, font):
        pygame.draw.rect(surf, (70, 70, 70), self.rect)
        txt = font.render(self.text, True, (255, 255, 255))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            return True
        return False

class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min, self.max = min_val, max_val
        self.value = initial
        self.handle_radius = 8
        self.label = label
        self.dragging = False
        self._update_handle_pos()

    def _update_handle_pos(self):
        frac = (self.value - self.min) / (self.max - self.min)
        self.handle_x = self.rect.x + int(frac * self.rect.width)
        self.handle_y = self.rect.y + self.rect.height // 2

    def draw(self, surf, font):
        pygame.draw.line(surf, (200,200,200),
                         (self.rect.x, self.handle_y),
                         (self.rect.x + self.rect.width, self.handle_y), 2)
        pygame.draw.circle(surf, (100,200,250),
                           (self.handle_x, self.handle_y),
                           self.handle_radius)
        txt = font.render(f"{self.label}: {self.value:.2f}", True, (255,255,255))
        surf.blit(txt, (self.rect.x, self.rect.y - txt.get_height() - 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            dx = event.pos[0] - self.handle_x
            dy = event.pos[1] - self.handle_y
            if dx*dx + dy*dy <= self.handle_radius**2:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width))
            self.handle_x = x
            frac = (x - self.rect.x) / self.rect.width
            self.value = self.min + frac * (self.max - self.min)
            return True
        return False

class Renderer:
    def __init__(self, world, cell_size=10, panel_width=150, fps=10):
        self.world       = world
        self.cell_size   = cell_size
        self.panel_width = panel_width
        self.grid_width  = world.width * cell_size
        self.grid_height = world.height * cell_size
        self.screen_w    = self.grid_width + panel_width
        self.screen_h    = self.grid_height
        self.init_plants     = world.initial_plants
        self.init_herb       = world.initial_herb_count
        self.init_carn       = world.initial_carn_count

        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("Ecological Simulation")
        self.clock = pygame.time.Clock()
        self.font  = pygame.font.SysFont(None, 24)
        self.fps   = fps

        # -- Controls (bottom of panel) --
        btn_w    = panel_width - 20
        btn_h    = 30
        spacing  = 10
        n_buttons = 3
        total_h  = n_buttons * btn_h + (n_buttons - 1) * spacing
        # leave 10px margin above bottom
        start_y  = self.screen_h - total_h - 10  

        labels = ["Restart", "Pause", "Next"]
        self.buttons = []
        for i, text in enumerate(labels):
            y = start_y + i * (btn_h + spacing)
            x = self.grid_width + 10
            self.buttons.append(Button(x, y, btn_w, btn_h, text))
        self.paused     = False
        self.restart    = False
        self.next_frame = False

        # -- Sliders --
        self.sliders = [
            # 0 → plant_spawn_rate
            Slider(self.grid_width+10, 140, btn_w,
                0.0, 0.05, world.plant_spawn_rate,        "Plant Spawn"),
            # 1 → herb_reproduce_threshold
            Slider(self.grid_width+10, 180, btn_w,
                1.0, 20.0, world.herb_reproduce_threshold, "Herb Repro"),
            # 2 → carn_reproduce_threshold
            Slider(self.grid_width+10, 220, btn_w,
                1.0, 20.0, world.carn_reproduce_threshold, "Carn Repro"),
            # 3 → max_herbivores
            Slider(self.grid_width+10, 260, btn_w,
                100, 2000, world.max_herbivores,          "Max Herb"),
            # 4 → reproduce_cooldown
            Slider(self.grid_width+10, 300, btn_w,
                0.0, 20.0, world.reproduce_cooldown,      "Repro Cool"),
            # 5 → init_plants
            Slider(self.grid_width+10, 340, btn_w,
                0, 2000, world.initial_plants,            "Init Plants"),
            # 6 → init_herb
            Slider(self.grid_width+10, 380, btn_w,
                0,  500, world.initial_herb_count,      "Init Herb"),
            # 7 → init_carn
            Slider(self.grid_width+10, 420, btn_w,
                0,  200, world.initial_carn_count,      "Init Carn"),
        ]

    def handle_event(self, event):
    # Buttons
        for btn in self.buttons:
            if btn.handle_event(event):
                if btn.text == "Restart":
                    self.restart = True

                # ← use “in” here, not ==
                elif btn.text in ("Pause", "Resume"):
                    self.paused = not self.paused
                    btn.text = "Resume" if self.paused else "Pause"

                elif btn.text == "Next":
                    self.next_frame = True

        # Sliders
        updated = False
        for s in self.sliders:
            if s.handle_event(event):
                updated = True
        if updated:
            
            self.world.plant_spawn_rate         = self.sliders[0].value
            self.world.herb_reproduce_threshold = self.sliders[1].value
            self.world.carn_reproduce_threshold = self.sliders[2].value
            self.world.max_herbivores           = int(self.sliders[3].value)
            self.world.reproduce_cooldown       = self.sliders[4].value
            self.init_plants                    = int(self.sliders[5].value)
            self.init_herb                      = int(self.sliders[6].value)
            self.init_carn                      = int(self.sliders[7].value)

    def draw(self):
        # 1) clear
        self.screen.fill((0,0,0))

        # 2) draw grid
        for e in self.world.entities:
            if isinstance(e, Vegetation): color=(0,200,0)
            elif isinstance(e, Herbivore): color=(0,0,200)
            elif isinstance(e, Carnivore): color=(200,0,0)
            else: continue
            r = pygame.Rect(e.x*self.cell_size, e.y*self.cell_size,
                            self.cell_size, self.cell_size)
            pygame.draw.rect(self.screen, color, r)

        # 3) draw panel bg
        panel = pygame.Rect(self.grid_width, 0, self.panel_width, self.screen_h)
        pygame.draw.rect(self.screen, (30,30,30), panel)

        # 4) draw counts
        y = 10
        for label, count in [("Plants:", sum(isinstance(u,Vegetation) for u in self.world.entities)),
                             ("Herbivores:", sum(isinstance(u,Herbivore) for u in self.world.entities)),
                             ("Carnivores:", sum(isinstance(u,Carnivore) for u in self.world.entities))]:
            surf = self.font.render(f"{label} {count}", True, (255,255,255))
            self.screen.blit(surf, (self.grid_width+10, y))
            y += surf.get_height() + 5

        # 5) draw buttons
        for btn in self.buttons:
            btn.draw(self.screen, self.font)

        # 6) draw sliders
        for s in self.sliders:
            s.draw(self.screen, self.font)

        # 7) flip
        pygame.display.flip()

    def tick(self):
        self.clock.tick(self.fps)
