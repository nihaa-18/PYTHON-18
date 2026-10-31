class ElectricityBillingSystem:
    def __init__(self, slabs, fixed_charge, surcharge_pct, anomaly_threshold_pct=35.0):
        """
        slabs: List of tuples -> (upper_limit, rate_per_unit)
               e.g., [(100, 1.50), (300, 2.75), (float('inf'), 4.25)]
        """
        self.slabs = slabs
        self.fixed_charge = fixed_charge
        self.surcharge_pct = surcharge_pct
        self.anomaly_threshold_pct = anomaly_threshold_pct

    def calculate_energy_charge(self, units):
        remaining_units = units
        total_energy_cost = 0.0
        previous_limit = 0

        for limit, rate in self.slabs:
            if remaining_units <= 0:
                break
            
            # Determine units falling in the current slab
            slab_capacity = limit - previous_limit
            units_in_slab = min(remaining_units, slab_capacity)
            
            total_energy_cost += units_in_slab * rate
            remaining_units -= units_in_slab
            previous_limit = limit

        return round(total_energy_cost, 2)

    def generate_bill(self, current_reading, previous_reading, history_months):
        units_consumed = current_reading - previous_reading
        if units_consumed < 0:
            raise ValueError("Current reading cannot be less than previous reading.")

        # 1. Base Energy Cost Calculation
        energy_cost = self.calculate_energy_charge(units_consumed)

        # 2. Surcharges and Fixed Fees
        surcharge = round(energy_cost * (self.surcharge_pct / 100.0), 2)
        total_bill = round(energy_cost + self.fixed_charge + surcharge, 2)

        # 3. Anomaly Detection
        anomaly_flag = False
        avg_historical = 0.0
        if history_months:
            avg_historical = sum(history_months) / len(history_months)
            percentage_increase = ((units_consumed - avg_historical) / avg_historical) * 100
            if percentage_increase >= self.anomaly_threshold_pct:
                anomaly_flag = True

        return {
            "units_consumed": units_consumed,
            "energy_cost": energy_cost,
            "fixed_charge": self.fixed_charge,
            "surcharge": surcharge,
            "total_bill": total_bill,
            "historical_average": round(avg_historical, 2),
            "anomaly_detected": anomaly_flag
        }

# --- Sample Execution ---
if __name__ == "__main__":
    # Slabs: First 100 units @ $1.50/unit, Next 200 units (101-300) @ $2.75/unit, Above 300 units @ $4.00/unit
    slabs = [
        (100, 1.50),
        (300, 2.75),
        (float('inf'), 4.00)
    ]
    
    billing_system = ElectricityBillingSystem(
        slabs=slabs,
        fixed_charge=15.00,
        surcharge_pct=5.0, # 5% tax/fuel surcharge
        anomaly_threshold_pct=30.0
    )

    # Historical monthly consumption for the past 3 months (in kWh)
    history = [220, 240, 210]
    
    # Current month meter readings
    prev_reading = 4500
    curr_reading = 4880  # Consumed 380 units

    bill_details = billing_system.generate_bill(curr_reading, prev_reading, history)

    print("=== ELECTRICITY BILL STATEMENT ===")
    print(f"Units Consumed: {bill_details['units_consumed']} kWh")
    print(f"Energy Charges: ${bill_details['energy_cost']:.2f}")
    print(f"Fixed Service Charge: ${bill_details['fixed_charge']:.2f}")
    print(f"Surcharge (5%): ${bill_details['surcharge']:.2f}")
    print(f"-----------------------------------")
    print(f"TOTAL BILL: ${bill_details['total_bill']:.2f}")
    print(f"\n=== HISTORICAL & ANOMALY ANALYSIS ===")
    print(f"Past 3-Month Average: {bill_details['historical_average']} kWh")
    if bill_details['anomaly_detected']:
        print("⚠️ WARNING: Unusual consumption spike detected compared to your historical average!")
    else:
        print("✅ Status: Consumption is within normal historical ranges.")
