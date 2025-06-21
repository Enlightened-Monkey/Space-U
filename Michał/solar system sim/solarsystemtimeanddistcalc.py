import numpy as np
from scipy.optimize import fsolve

# Parametry planet: a (promień orbity w AU), T (okres orbitalny w latach)
planets = {
    "Mercury": {"a": 0.387, "T": 0.241},
    "Venus": {"a": 0.723, "T": 0.615},
    "Earth": {"a": 1.0, "T": 1.0},
    "Mars": {"a": 1.524, "T": 1.88},
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
    planet_name = "Mars"  # Przykładowa planeta
    t0 = 6  # Czas startu w latach (np. t=0)
    v_kms = 11.0  # Prędkość rakiety w km/s
    result = find_travel_time(t0, v_kms, planet_name)
    if result:
        travel_time_days, distance_AU = result
        print(f"Dla planety {planet_name}, przy v={v_kms} km/s:")
        print(f"Czas podróży: {travel_time_days:.2f} dni")
        print(f"Dystans: {distance_AU:.2f} AU")
    else:
        print("Nie znaleziono rozwiązania")