import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from scipy.optimize import newton

# Dane planet (a, b, c w gigametrach, mimośród)
PLANETS = [
    {"name": "Merkury", "a": 57.9, "b": 56.6703, "c": 11.8695, "color": "gray"},
    {"name": "Wenus", "a": 108, "b": 107.9974, "c": 0.756, "color": "orange"},
    {"name": "Ziemia", "a": 150, "b": 149.9783, "c": 2.55, "color": "blue"},
    {"name": "Mars", "a": 228, "b": 226.9905, "c": 21.432, "color": "red"},
    {"name": "Jowisz", "a": 779, "b": 778.0643, "c": 38.171, "color": "gold"},
    {"name": "Saturn", "a": 1430, "b": 1428.9, "c": 80.08, "color": "tan"},  # Poprawione b i c
    {"name": "Uran", "a": 2870, "b": 2866.9619, "c": 132.02, "color": "cyan"},
    {"name": "Neptun", "a": 4500, "b": 4499.7277, "c": 49.5, "color": "darkblue"}
]

# Obliczanie mimośrodu e = c / a
for planet in PLANETS:
    planet["e"] = planet["c"] / planet["a"]

# Skala do dopasowania orbity Neptuna w wykresie
MAX_A = max(planet["a"] for planet in PLANETS)  # Półosie wielka Neptuna
SCALE = 1.0 / (MAX_A * 1.2)  # Skala z 20% marginesem
SUN_SIZE = 50
PLANET_SIZE = 20
FPS = 60
FRAMES = 1000  # ~16.67 sekund przy 60 FPS

# Obliczanie okresów orbitalnych zgodnie z III prawem Keplera (T^2 = k * a^3)
EARTH_A = 150  # Półosie wielka Ziemi
EARTH_PERIOD = 60  # Orbita Ziemi w 60 sekund dla widoczności
K = EARTH_PERIOD**2 / EARTH_A**3  # Stała Keplera
for planet in PLANETS:
    planet["period"] = np.sqrt(K * planet["a"]**3)

# Ustawienie wykresu
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_aspect("equal")
ax.set_facecolor("black")
ax.set_xlim(-MAX_A * 1.2 * SCALE, MAX_A * 1.2 * SCALE)
ax.set_ylim(-MAX_A * 1.2 * SCALE, MAX_A * 1.2 * SCALE)
ax.set_xlabel("X (skalowane gigametry)")
ax.set_ylabel("Y (skalowane gigametry)")
ax.set_title("Orbity Układu Słonecznego")

# Rysowanie Słońca w (0,0)
ax.scatter([0], [0], color="yellow", marker="*", s=SUN_SIZE, label="Słońce")

# Rysowanie orbit i planet
lines = []
points = []
for planet in PLANETS:
    # Rysowanie eliptycznej orbity z przesunięciem środka o -c
    theta = np.linspace(0, 2 * np.pi, 100)
    x = (planet["a"] * np.cos(theta) - planet["c"]) * SCALE
    y = planet["b"] * np.sin(theta) * SCALE
    line, = ax.plot(x, y, color="gray", linestyle="--", linewidth=0.5)
    lines.append(line)
    # Inicjalizacja pozycji planety
    point, = ax.plot([], [], color=planet["color"], marker="o", markersize=PLANET_SIZE/2, label=planet["name"])
    points.append(point)

# Rozwiązanie równania Keplera
def kepler_equation(E, M, e):
    return E - e * np.sin(E) - M

def get_true_anomaly(t, period, e):
    M = (2 * np.pi * t) / period  # Anomalia średnia
    E = newton(kepler_equation, M, args=(M, e))  # Anomalia mimośrodowa
    nu = 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))  # Anomalia prawdziwa
    return nu

# Funkcja aktualizująca animację
def update(t):
    for planet, point in zip(PLANETS, points):
        period = planet["period"]
        e = planet["e"]
        nu = get_true_anomaly(t, period, e)
        x = planet["a"] * (np.cos(nu) - e) * SCALE
        y = planet["b"] * np.sin(nu) * SCALE
        point.set_data([x], [y])
    return points

# Tworzenie animacji
YEARS = 20
ani = FuncAnimation(
    fig,
    update,
    frames=np.linspace(0, EARTH_PERIOD * YEARS, FRAMES),
    interval=1000/FPS,
    blit=True
)

# Zapis jako GIF
ani.save("solar_system.gif", writer=PillowWriter(fps=FPS))

# Wyświetlenie wykresu
plt.legend()
plt.show()