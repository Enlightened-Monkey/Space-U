import random
import mysql.connector
from datetime import datetime, timedelta
from solarsystemtimeanddistcalc import calculate_trip_times

def run_simulation(start_budget, start_date, end_date):
    try:
        # Połączenie z bazą danych
        con = mysql.connector.connect(
            host="giniewicz.it",
            user="team07",
            password="te@mlot",
            database="team07",
            charset="utf8"
        )
        cursor = con.cursor(dictionary=True)

        # Inicjalizacja budżetu
        budget = start_budget
        print(f"Startowy budżet: {budget}")

        # Symulacja w krokach półrocznych
        current_date = start_date
        while current_date <= end_date:
            print(f"\nSymulacja dla daty: {current_date}")

            # Generowanie klientów
            cursor.execute("SELECT COUNT(*) AS total_customers FROM Customers")
            total_customers = cursor.fetchone()['total_customers']
            print(f"Liczba klientów: {total_customers}")

            # Pobieranie dostępnych statków i rakiet
            cursor.execute("""
                SELECT spaceship_id, capacity, travel_speed, status 
                FROM Spaceships 
                WHERE status = 'active'
            """)
            spaceships = cursor.fetchall()

            cursor.execute("""
                SELECT rocket_id, status 
                FROM Rockets 
                WHERE status = 'active'
            """)
            rockets = cursor.fetchall()

            if not spaceships or not rockets:
                print("Brak dostępnych statków lub rakiet.")
                break

            # Obsługa klientów
            for spaceship in spaceships:
                if total_customers <= 0:
                    break

                # Wybór rakiety
                rocket = random.choice(rockets)

                # Wybór wycieczki
                cursor.execute("SELECT * FROM Destinations ORDER BY RAND() LIMIT 1")
                destination = cursor.fetchone()

                # Obliczanie czasu i dystansu
                travel_to_days, total_time_days, travel_back_days = calculate_trip_times(
                    current_date, 
                    random.randint(3, 14),  # Losowa długość pobytu
                    destination['destination_id'],
                    spaceship['travel_speed']
                )

                if not travel_to_days:
                    print("Nie udało się obliczyć czasu podróży.")
                    continue

                # Koszt organizacji
                base_cost = random.randint(100000, 500000)  # Koszt pobytu na miejscu
                organization_cost = (
                    (spaceship['capacity'] / total_customers) * sum_employee_salaries(cursor) +
                    rocket['initial_cost'] * 0.7 +
                    spaceship['initial_cost'] * 0.15 +
                    base_cost
                )
                budget -= organization_cost

                # Dodanie wycieczki do Trips
                return_date = current_date + timedelta(days=total_time_days)
                cursor.execute("""
                    INSERT INTO Trips (name, description, destination_id, launch_date, duration_of_stay, return_date, spaceship_id, rocket_id, status, organization_cost)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'planned', %s)
                """, (
                    f"Wycieczka do {destination['name']}",
                    destination['description'],
                    destination['destination_id'],
                    current_date,
                    total_time_days,
                    return_date,
                    spaceship['spaceship_id'],
                    rocket['rocket_id'],
                    organization_cost
                ))
                trip_id = cursor.lastrowid

                # Dodanie klientów do TripParticipants
                participants = min(spaceship['capacity'], total_customers)
                for _ in range(participants):
                    cursor.execute("SELECT pesel FROM Customers ORDER BY RAND() LIMIT 1")
                    customer = cursor.fetchone()
                    ticket_price = organization_cost / participants
                    cursor.execute("""
                        INSERT INTO TripParticipants (trip_id, customer_id, ticket_price, status, satisfaction_level)
                        VALUES (%s, %s, %s, 'confirmed', %s)
                    """, (
                        trip_id,
                        customer['pesel'],
                        ticket_price,
                        round(random.uniform(0.5, 1.0), 2)
                    ))
                    total_customers -= 1

                print(f"Zorganizowano wycieczkę {trip_id} do {destination['name']} z {participants} uczestnikami.")

                # Przekazanie rakiety do serwisu
                repair_start_date = return_date
                repair_end_date = repair_start_date + timedelta(days=random.randint(30, 60))
                cursor.execute("""
                    INSERT INTO RecoveryTasks (employee_id, rocket_id, start_date, end_date, status)
                    VALUES (%s, %s, %s, %s, 'in_progress')
                """, (
                    assign_employee(cursor, 'rockets'),
                    rocket['rocket_id'],
                    repair_start_date,
                    repair_end_date
                ))

            # Wypłata pensji pracownikom raz na rok
            if current_date.month == 12:
                salaries = sum_employee_salaries(cursor)
                budget -= salaries
                print(f"Wypłacono pensje pracownikom: {salaries}. Pozostały budżet: {budget}")

            # Przejście do następnego półrocza
            current_date += timedelta(days=182)

        con.commit()
        print(f"Symulacja zakończona. Pozostały budżet: {budget}")

    except mysql.connector.Error as err:
        print(f"Błąd podczas operacji na bazie danych: {err}")
    finally:
        if 'con' in locals() and con.is_connected():
            cursor.close()
            con.close()
            print("Połączenie z bazą danych zostało zamknięte.")

def sum_employee_salaries(cursor):
    """Oblicza sumę pensji wszystkich pracowników."""
    cursor.execute("SELECT SUM(salary) AS total_salaries FROM Employees")
    return cursor.fetchone()['total_salaries']

def assign_employee(cursor, specialization):
    """Przypisuje pracownika o danej specjalizacji."""
    cursor.execute("SELECT pesel FROM Employees WHERE specialization = %s ORDER BY RAND() LIMIT 1", (specialization,))
    employee = cursor.fetchone()
    return employee['pesel'] if employee else None

if __name__ == "__main__":
    start_budget = 100000000  # Startowy budżet firmy
    start_date = datetime(2167, 1, 1)
    end_date = datetime(2177, 12, 31)
    run_simulation(start_budget, start_date, end_date)