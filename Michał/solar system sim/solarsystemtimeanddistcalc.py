import numpy as np
from scipy.optimize import fsolve
from datetime import datetime, timedelta

# Parametry planet: a (promień orbity w AU), T (okres orbitalny w latach)
planets = {
    "Mercury": {"a": 0.387, "T": 0.241},
    "Venus": {"a": 0.723, "T": 0.615},
    "Earth": {"a": 1.0, "T": 1.0},
    "Mars": {"a": 1.524, "T": 1.88},
}

# Mapowanie destination_id na nazwy planet (do dostosowania do tabeli Destinations)
destination_to_planet = {
    1: "Mars",
    2: "Venus",
    3: "Mercury",
    4: "Earth",  # Stacja Kosmiczna może być traktowana jako orbita Ziemi
    5: "Mars"    # Możesz dostosować dla innych celów
}

def position(t, a, T, phi=0):
    """Oblicza położenie planety w czasie t (w latach od epoki)."""
    theta = 2 * np.pi * t / T + phi
    return np.array([a * np.cos(theta), a * np.sin(theta)])

def find_travel_time(t0_years, v_kms, planet_name, return_time=False):
    """Oblicza czas podróży i dystans między Ziemią a planetą."""
    # Przeliczenie prędkości z km/s na AU/rok
    km_per_au = 149597870.7
    seconds_per_year = 3.15576e7
    v = v_kms * (seconds_per_year / km_per_au)  # AU/rok

    a_P = planets[planet_name]["a"]
    T_P = planets[planet_name]["T"]
    a_E = 1.0
    T_E = 1.0

    def func(delta_t):
        pos_earth = position(t0_years, a_E, T_E)
        pos_planet = position(t0_years + delta_t, a_P, T_P) if not return_time else position(t0_years + delta_t, a_P, T_P, phi=2*np.pi*delta_t/T_P)
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

def calculate_trip_times(launch_date, duration_of_stay_days, destination_id, v_kms=11.0):
    """Oblicza czasy podróży: dojazd, pobyt i powrót."""
    # Konwersja launch_date na lata od epoki (np. 2167-01-01 = 0)
    epoch = datetime(2167, 1, 1)
    t0 = (launch_date - epoch).days / 365.25

    # Mapowanie destination_id na nazwę planety
    planet_name = destination_to_planet.get(destination_id)
    if not planet_name or planet_name == "Earth":
        return None, None, None  # Nie obliczamy dla Ziemi

    # 1. Czas dojazdu
    travel_to_days, distance_to_AU = find_travel_time(t0, v_kms, planet_name)
    if travel_to_days is None:
        return None, None, None

    # 2. Całkowity czas na planecie (dojazd + pobyt)
    total_time_on_planet_days = travel_to_days + duration_of_stay_days

    # 3. Czas powrotu (po upływie czasu dojazdu i pobytu)
    t_return = t0 + (total_time_on_planet_days / 365.25)
    travel_back_days, distance_back_AU = find_travel_time(t_return, v_kms, planet_name, return_time=True)
    if travel_back_days is None:
        return None, None, None

    return travel_to_days, total_time_on_planet_days, travel_back_days

# Przykładowe użycie z danymi z TripOffers
if __name__ == "__main__":
    # Przykładowe dane z TripOffers (do zastąpienia zapytaniem SQL)
    launch_date = datetime(2167, 6, 1)  # Przykładowa data startu
    duration_of_stay_days = 14  # Przykładowa długość pobytu (np. dwutygodniowy obóz na Marsie)
    destination_id = 1  # Mars

    result = calculate_trip_times(launch_date, duration_of_stay_days, destination_id)
    if result:
        travel_to_days, total_time_days, travel_back_days = result
        print(f"Czas dojazdu: {travel_to_days:.2f} dni")
        print(f"Całkowity czas (dojazd + pobyt): {total_time_days:.2f} dni")
        print(f"Czas powrotu: {travel_back_days:.2f} dni")
    else:
        print("Nie znaleziono rozwiązania")