import random, sys, pygame
import matplotlib.pyplot as plt
from world      import World
from renderer   import Renderer
from entities.vegetation import Vegetation
from entities.herbivore import Herbivore
from entities.carnivore import Carnivore

# 1) Setup live plot
plt.ion()
fig, ax = plt.subplots()
ax.set_title("Population Over Time")
ax.set_xlabel("Tick")
ax.set_ylabel("Count")
line_pl, = ax.plot([], [], label="Plants (x100)",    color="green")
line_hv, = ax.plot([], [], label="Herbivores ",color="blue")
line_cv, = ax.plot([], [], label="Carnivores",color="red")
ax.legend()

# 2) History buffers
ticks = []
plants_hist = []
herb_hist   = []
carn_hist   = []

def make_world(w, h):
    world = World(w, h)
    for _ in range(500):
        x,y = random.randrange(w), random.randrange(h)
        world.add_entity(Vegetation(x,y))
    for _ in range(200):
        x,y = random.randrange(w), random.randrange(h)
        world.add_entity(Herbivore(x,y))
    for _ in range(20):
        x,y = random.randrange(w), random.randrange(h)
        world.add_entity(Carnivore(x,y))
    return world

def main():
    W, H = 80, 60
    world    = make_world(W, H)
    renderer = Renderer(world, cell_size=10, panel_width=150, fps=10)
    seed_world(world, renderer)
    running  = True
    tick     = 0

    while running:
        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False
            renderer.handle_event(evt)

        # restart
        if renderer.restart:
            world = make_world(W, H)
            renderer.world = world
            seed_world(world, renderer)
            ticks.clear(); plants_hist.clear(); herb_hist.clear(); carn_hist.clear()
            tick = 0
            renderer.restart = False

        # step simulation
        if not renderer.paused or renderer.next_frame:
            world.tick()
            tick += 1

            # record populations
            p = sum(isinstance(e,Vegetation) for e in world.entities)
            h = sum(isinstance(e,Herbivore)   for e in world.entities)
            c = sum(isinstance(e,Carnivore)   for e in world.entities)
            ticks.append(tick)
            plants_hist.append(p/100.0)
            herb_hist.append(h)
            carn_hist.append(c)

            # update plot
            line_pl.set_data(ticks, plants_hist)
            line_hv.set_data(ticks, herb_hist)
            line_cv.set_data(ticks, carn_hist)
            ax.relim(); ax.autoscale_view()
            fig.canvas.draw(); fig.canvas.flush_events()

            renderer.next_frame = False

        renderer.draw()
        renderer.tick()

    pygame.quit()
    sys.exit()

def seed_world(world, renderer):
    # clear any old entities
    world.entities = []
    world.grid     = [[[] for _ in range(world.height)] for _ in range(world.width)]

    # spawn plants
    for _ in range(renderer.init_plants):
        x,y = random.randrange(world.width), random.randrange(world.height)
        world.add_entity(Vegetation(x,y))

    # spawn herbivores
    for _ in range(renderer.init_herb):
        x,y = random.randrange(world.width), random.randrange(world.height)
        world.add_entity(Herbivore(x,y))

    # spawn carnivores
    for _ in range(renderer.init_carn):
        x,y = random.randrange(world.width), random.randrange(world.height)
        world.add_entity(Carnivore(x,y))
if __name__ == "__main__":
    main()
