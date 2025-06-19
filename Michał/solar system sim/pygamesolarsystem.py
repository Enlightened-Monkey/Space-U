import asyncio
import math
import pygame
import platform

# Screen dimensions
WIDTH, HEIGHT = 1200, 800
CENTER = (WIDTH // 2, HEIGHT // 2)

# Planet data from Table 1 (a, b, c in gigameters, eccentricity)
PLANETS = [
    {"name": "Mercury", "a": 57.9, "b": 56.6703, "c": 11.8695, "color": (128, 128, 128)},
    {"name": "Venus", "a": 108, "b": 107.9974, "c": 0.756, "color": (255, 165, 0)},
    {"name": "Earth", "a": 150, "b": 149.9783, "c": 2.55, "color": (0, 0, 255)},
    {"name": "Mars", "a": 228, "b": 226.9905, "c": 21.432, "color": (255, 0, 0)},
    {"name": "Jupiter", "a": 779, "b": 778.0643, "c": 38.171, "color": (255, 215, 0)},
    {"name": "Saturn", "a": 1430, "b": 488.1149, "c": 81.51, "color": (210, 180, 140)},  # Note: b seems off in document, using for consistency
    {"name": "Uranus", "a": 2870, "b": 2866.9619, "c": 132.02, "color": (0, 255, 255)},
    {"name": "Neptune", "a": 4500, "b": 4499.7277, "c": 49.5, "color": (0, 0, 139)}
]

# Scaling factor (fit Neptune's orbit to screen)
MAX_A = max(planet["a"] for planet in PLANETS)  # Neptune's semi-major axis
SCALE = (WIDTH * 0.4) / MAX_A  # Scale to fit 40% of screen width
SUN_RADIUS = 10
PLANET_RADIUS = 5
FPS = 60

# Calculate orbital periods using Kepler's Third Law (T^2 = k * a^3), scaled to Earth's period
EARTH_A = 150  # Earth's semi-major axis
EARTH_PERIOD = 60  # Earth orbit in 60 seconds for visibility
K = EARTH_PERIOD**2 / EARTH_A**3  # Constant for Kepler's Third Law
for planet in PLANETS:
    planet["period"] = math.sqrt(K * planet["a"]**3)

def setup():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solar System Simulation")
    screen.fill((0, 0, 0))  # Black background

def draw_ellipse(planet):
    """Draw the elliptical orbit centered at (0,0) with Sun at (c,0)."""
    a_pixels = planet["a"] * SCALE
    b_pixels = planet["b"] * SCALE
    c_pixels = planet["c"] * SCALE
    rect = pygame.Rect(CENTER[0] - a_pixels, CENTER[1] - b_pixels, 2 * a_pixels, 2 * b_pixels)
    pygame.draw.ellipse(screen, (50, 50, 50), rect, 1)  # Gray orbit
    # Draw Sun at (c,0) relative to center
    sun_pos = (CENTER[0] + c_pixels, CENTER[1])
    pygame.draw.circle(screen, (255, 255, 0), sun_pos, SUN_RADIUS)

def get_planet_position(planet, t):
    """Calculate planet position on ellipse at time t."""
    period = planet["period"]
    a_pixels = planet["a"] * SCALE
    b_pixels = planet["b"] * SCALE
    c_pixels = planet["c"] * SCALE
    # Parametric angle based on time (2pi per period)
    theta = (2 * math.pi * t) / period
    x = a_pixels * math.cos(theta)
    y = b_pixels * math.sin(theta)
    # Shift to account for Sun at (c,0)
    return (CENTER[0] + x, CENTER[1] + y)

async def main():
    setup()
    t = 0
    running = True
    clock = pygame.time.Clock()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 0, 0))  # Clear screen
        
        # Draw orbits and Sun for each planet
        for planet in PLANETS:
            draw_ellipse(planet)
        
        # Draw planets
        for planet in PLANETS:
            pos = get_planet_position(planet, t)
            pygame.draw.circle(screen, planet["color"], pos, PLANET_RADIUS)
        
        pygame.display.flip()
        t += 1 / FPS  # Increment time
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)
    
    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())