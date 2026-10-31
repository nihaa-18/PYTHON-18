class HospitalBillingSystem:
    def __init__(self, max_discount_pct=40.0):
        self.max_discount_pct = max_discount_pct

    def classify_patient(self, profile):
        if profile.get("is_indigent") or profile.get("annual_income", 999999) < 20000:
            return "Subsidized (BPL)"
        elif profile.get("corporate_partner"):
            return "Corporate Tier-1"
        elif profile.get("has_insurance"):
            return "Insured Private"
        else:
            return "General Cash"

    def process_bill(self, profile, line_items):
        # 1. Calculate Gross Subtotal
        consultation = sum(line_items.get("consultation", []))
        diagnostics = sum(line_items.get("diagnostics", []))
        treatment = sum(line_items.get("treatment", []))
        room_rent = sum(line_items.get("room_rent", []))
        
        gross_total = consultation + diagnostics + treatment + room_rent

        # 2. Classify Patient
        category = self.classify_patient(profile)

        # 3. Apply Concessions based on Classification
        discount_amount = 0.0
        if category == "Subsidized (BPL)":
            discount_amount = gross_total * 0.50  # 50% subsidy
        elif profile.get("age", 0) >= 60:
            discount_amount = gross_total * 0.10  # 10% senior citizen discount
        elif category == "Corporate Tier-1":
            discount_amount = gross_total * 0.15  # 15% corporate discount

        # Validate against maximum discount cap
        max_allowed_discount = gross_total * (self.max_discount_pct / 100.0)
        if discount_amount > max_allowed_discount:
            discount_amount = max_allowed_discount

        net_after_discount = gross_total - discount_amount

        # 4. Process Insurance / Co-pay
        insurance_payout = 0.0
        patient_payable = net_after_discount

        if profile.get("has_insurance") and category != "Subsidized (BPL)":
            deductible = profile.get("insurance_deductible", 500.0)
            coverage_pct = profile.get("insurance_coverage_pct", 80.0)
            max_claim = profile.get("insurance_max_claim", 10000.0)

            eligible_for_insurance = max(0.0, net_after_discount - deductible)
            calculated_payout = eligible_for_insurance * (coverage_pct / 100.0)
            
            insurance_payout = min(calculated_payout, max_claim)
            patient_payable = net_after_discount - insurance_payout

        return {
            "patient_name": profile.get("name"),
            "classification": category,
            "gross_total": round(gross_total, 2),
            "discount_applied": round(discount_amount, 2),
            "net_after_discount": round(net_after_discount, 2),
            "insurance_payout": round(insurance_payout, 2),
            "patient_payable": round(patient_payable, 2)
        }

# --- Sample Execution ---
if __name__ == "__main__":
    billing_system = HospitalBillingSystem(max_discount_pct=40.0)

    # Sample Patient Profile
    patient = {
        "name": "Eleanor Vance",
        "age": 64,
        "is_indigent": False,
        "corporate_partner": False,
        "has_insurance": True,
        "insurance_deductible": 250.0,
        "insurance_coverage_pct": 85.0,
        "insurance_max_claim": 8000.0
    }

    # Itemized Charges
    charges = {
        "consultation": [150.0, 200.0],
        "diagnostics": [350.0, 120.0],
        "treatment": [2400.0],
        "room_rent": [600.0, 600.0]
    }

    statement = billing_system.process_bill(patient, charges)

    print("=== HOSPITAL BILLING STATEMENT ===")
    print(f"Patient Name: {statement['patient_name']}")
    print(f"Patient Classification: {statement['classification']}")
    print(f"----------------------------------------")
    print(f"Gross Subtotal:     ${statement['gross_total']:.2f}")
    print(f"Concession/Discount: -${statement['discount_applied']:.2f}")
    print(f"Net Amount:         ${statement['net_after_discount']:.2f}")
    print(f"Insurance Payout:   -${statement['insurance_payout']:.2f}")
    print(f"========================================")
    print(f"PATIENT PAYABLE:    ${statement['patient_payable']:.2f}")
