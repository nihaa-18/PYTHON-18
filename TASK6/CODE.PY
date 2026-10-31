class RailwayFareCalculator:
    def __init__(self, class_multipliers, base_rate_per_km=1.25, reservation_fee=30.0):
        """
        class_multipliers: Dict of class names to multiplier factors (e.g., {"SL": 1.0, "3AC": 2.2, "1AC": 4.0})
        base_rate_per_km: Base charge per kilometer
        reservation_fee: Flat booking fee per passenger
        """
        self.class_multipliers = class_multipliers
        self.base_rate_per_km = base_rate_per_km
        self.reservation_fee = reservation_fee

    def calculate_passenger_fare(self, distance, travel_class, passenger):
        multiplier = self.class_multipliers.get(travel_class, 1.0)
        base_fare = distance * self.base_rate_per_km * multiplier

        # Age-based concessions
        age = passenger["age"]
        concession_desc = "None (Standard Adult)"
        discount_multiplier = 1.0

        if age < 5:
            # Toddlers travel free without berth
            discount_multiplier = 0.0
            concession_desc = "Infant (100% Concession)"
        elif age < 12:
            discount_multiplier = 0.50
            concession_desc = "Child (50% Concession)"
        elif age >= 60:
            discount_multiplier = 0.60  # 40% off
            concession_desc = "Senior Citizen (40% Concession)"

        net_fare = (base_fare * discount_multiplier) + self.reservation_fee

        return {
            "name": passenger["name"],
            "age": age,
            "base_fare": round(base_fare, 2),
            "concession": concession_desc,
            "fare_after_concession": round(base_fare * discount_multiplier, 2),
            "reservation_fee": self.reservation_fee,
            "total_passenger_fare": round(net_fare, 2)
        }

    def process_booking(self, distance, travel_class, passengers, is_cancelled=False, cancellation_penalty_pct=15.0):
        if travel_class not in self.class_multipliers:
            raise ValueError(f"Invalid travel class: {travel_class}")

        itemized_passengers = []
        total_gross_fare = 0.0

        for p in passengers:
            p_details = self.calculate_passenger_fare(distance, travel_class, p)
            itemized_passengers.append(p_details)
            total_gross_fare += p_details["total_passenger_fare"]

        total_gross_fare = round(total_gross_fare, 2)
        refund_amount = 0.0
        net_payable = total_gross_fare

        if is_cancelled:
            penalty_amount = round(total_gross_fare * (cancellation_penalty_pct / 100.0), 2)
            refund_amount = round(total_gross_fare - penalty_amount, 2)
            net_payable = 0.0

        return {
            "distance": distance,
            "travel_class": travel_class,
            "passengers": itemized_passengers,
            "total_gross_fare": total_gross_fare,
            "is_cancelled": is_cancelled,
            "cancellation_penalty": round(total_gross_fare * (cancellation_penalty_pct / 100.0), 2) if is_cancelled else 0.0,
            "refund_amount": refund_amount,
            "net_payable": net_payable
        }

# --- Sample Execution ---
if __name__ == "__main__":
    # Class Multipliers
    multipliers = {
        "SL": 1.0,    # Sleeper
        "3AC": 2.4,   # AC 3-Tier
        "2AC": 3.2,   # AC 2-Tier
        "1AC": 4.5    # First AC
    }

    calculator = RailwayFareCalculator(
        class_multipliers=multipliers,
        base_rate_per_km=1.10,
        reservation_fee=40.0
    )

    # Sample Group Passengers
    group_passengers = [
        {"name": "Arthur Pendelton", "age": 65},  # Senior Citizen
        {"name": "Guinevere Pendelton", "age": 62}, # Senior Citizen
        {"name": "Lancelot Pendelton", "age": 34},  # Adult
        {"name": "Mordred Pendelton", "age": 8}     # Child
    ]

    # Booking parameters: 850 km journey in AC 3-Tier ("3AC")
    booking_result = calculator.process_booking(
        distance=850,
        travel_class="3AC",
        passengers=group_passengers,
        is_cancelled=False
    )

    print("==================================================")
    print("            RAILWAY TICKET INVOICE                ")
    print("==================================================")
    print(f"Travel Distance : {booking_result['distance']} km")
    print(f"Travel Class    : {booking_result['travel_class']}")
    print("--------------------------------------------------")
    for p in booking_result['passengers']:
        print(f"Passenger: {p['name']} (Age: {p['age']})")
        print(f"  Concession Applied: {p['concession']}")
        print(f"  Base Fare Share   : ${p['fare_after_concession']:.2f}")
        print(f"  Reservation Fee   : ${p['reservation_fee']:.2f}")
        print(f"  Subtotal          : ${p['total_passenger_fare']:.2f}")
        print("-" * 50)

    print(f"==================================================")
    print(f"TOTAL GROSS FARE    : ${booking_result['total_gross_fare']:.2f}")
    if booking_result['is_cancelled']:
        print(f"Cancellation Penalty: ${booking_result['cancellation_penalty']:.2f}")
        print(f"REFUNDABLE AMOUNT   : ${booking_result['refund_amount']:.2f}")
    else:
        print(f"NET AMOUNT PAYABLE  : ${booking_result['net_payable']:.2f}")
    print("==================================================")
