import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Parametry planet: a (promień orbity w AU), T (okres orbitalny w latach)
planets = {
    "Mercury": {"a": 0.387, "T": 0.241},
    "Venus": {"a": 0.723, "T": 0.615},
    "Earth": {"a": 1.0, "T": 1.0},
    "Mars": {"a": 1.524, "T": 1.88},
    "Jupiter": {"a": 5.203, "T": 11.86},
    "Saturn": {"a": 9.539, "T": 29.46},
    "Uranus": {"a": 19.191, "T": 84.01},
    "Neptune": {"a": 30.069, "T": 164.79}
}

def position(t, a, T, phi=0):
    """Oblicza położenie planety w czasie t."""
    theta = 2 * np.pi * t / T + phi
    return np.array([a * np.cos(theta), a * np.sin(theta)])

def find_travel_time(t0, v_kms, planet_name):
    """Oblicza czas podróży i dystans do planety."""
    # Przeliczenie prędkości z km/s na AU/rok
    km_per_au = 149597870.7
    seconds_per_year = 3.15576e7
    v = v_kms * (seconds_per_year / km_per_au)  # AU/rok

    a_P = planets[planet_name]["a"]
    T_P = planets[planet_name]["T"]
    a_E = 1.0
    T_E = 1.0

    def func(delta_t):
        pos_earth = position(t0, a_E, T_E)
        pos_planet = position(t0 + delta_t, a_P, T_P)
        dist = np.linalg.norm(pos_planet - pos_earth)
        return dist - v * delta_t

    # Szukanie rozwiązania dla różnych początkowych przypuszczeń
    initial_guesses = [0.01, 0.1, 1.0, 5.0]
    solutions = []
    for guess in initial_guesses:
        delta_t, = fsolve(func, guess)
        if delta_t > 0:
            solutions.append(delta_t)

    if solutions:
        travel_time_years = min(solutions)
        distance_AU = v * travel_time_years
        travel_time_days = travel_time_years * 365.25
        return travel_time_days, distance_AU
    else:
        return None

if __name__ == "__main__":
    planet_name = "Neptune"  # Przykładowa planeta
    t0 = 6  # Czas startu w latach
    v_kms = 11.0  # Prędkość rakiety w km/s
    result = find_travel_time(t0, v_kms, planet_name)
    if result:
        travel_time_days, distance_AU = result
        print(f"Dla planety {planet_name}, przy v={v_kms} km/s:")
        print(f"Czas podróży: {travel_time_days:.2f} dni")
        print(f"Dystans: {distance_AU:.2f} AU")
        
        # --- Wizualizacja ---
        # Pozycje początkowe i końcowe
        pos_earth_start = position(t0, planets["Earth"]["a"], planets["Earth"]["T"])
        pos_planet_end = position(t0 + (travel_time_days / 365.25), planets[planet_name]["a"], planets[planet_name]["T"])

        # Rysuj orbity
        theta = np.linspace(0, 2 * np.pi, 200)
        fig, ax = plt.subplots(figsize=(8, 8))
        for pname, pdata in planets.items():
            orbit_x = pdata["a"] * np.cos(theta)
            orbit_y = pdata["a"] * np.sin(theta)
            ax.plot(orbit_x, orbit_y, '--', label=pname if pname in ["Earth", planet_name] else None, alpha=0.5)

        # Rysuj Słońce w centrum
        ax.scatter([0], [0], color='yellow', marker='*', s=100, label='Sun')

        # Przygotuj punkty dla planet
        earth_scatter, = ax.plot([], [], 'o', color='blue', label='Earth')
        planet_scatter, = ax.plot([], [], 'o', color='red', label=planet_name)
        # Przygotuj linię trajektorii
        line, = ax.plot([], [], color='green', linewidth=2, label='Trajectory')

        ax.set_aspect('equal')
        ax.set_xlabel('AU')
        ax.set_ylabel('AU')
        ax.set_title(f'Trajectory from Earth to {planet_name}')
        ax.legend()
        ax.grid(True)

        # Funkcja aktualizująca animację
        def animate(i):
            frac = i / 100
            t_current = t0 + frac * (travel_time_days / 365.25)
            # Aktualizuj pozycje planet
            pos_earth = position(t_current, planets["Earth"]["a"], planets["Earth"]["T"])
            pos_planet = position(t_current, planets[planet_name]["a"], planets[planet_name]["T"])
            earth_scatter.set_data([pos_earth[0]], [pos_earth[1]])
            planet_scatter.set_data([pos_planet[0]], [pos_planet[1]])
            # Aktualizuj trajektorię rakiety
            x = pos_earth_start[0] + frac * (pos_planet_end[0] - pos_earth_start[0])
            y = pos_earth_start[1] + frac * (pos_planet_end[1] - pos_earth_start[1])
            line.set_data([pos_earth_start[0], x], [pos_earth_start[1], y])
            return line, earth_scatter, planet_scatter

        anim = FuncAnimation(fig, animate, frames=101, interval=30, blit=True)

        # Zapisz jako GIF
        anim.save("trajectory_animated.gif", writer=PillowWriter(fps=30))

        plt.close(fig)  # Nie pokazuj okna podczas zapisu GIF
        print("GIF saved as trajectory_animated.gif")
    else:
        print("Nie znaleziono rozwiązania")