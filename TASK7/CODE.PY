class RetailBillingSystem:
    def __init__(self, category_taxes, discount_thresholds, max_discount_cap_pct=25.0):
        """
        category_taxes: Dict mapping category names to tax rates (e.g., {"Grocery": 0.0, "Electronics": 0.18})
        discount_thresholds: List of tuples -> (spending_limit, discount_percentage)
                             Sorted in ascending order of spending limit.
        max_discount_cap_pct: Maximum allowable discount percentage of the subtotal
        """
        self.category_taxes = category_taxes
        self.discount_thresholds = discount_thresholds
        self.max_discount_cap_pct = max_discount_cap_pct

    def process_bill(self, cart_items):
        gross_subtotal = 0.0
        total_tax = 0.0
        itemized_receipt = []

        # 1. Process Cart Line Items
        for item in cart_items:
            name = item["name"]
            category = item["category"]
            price = item["price"]
            qty = item["quantity"]

            line_subtotal = round(price * qty, 2)
            tax_rate = self.category_taxes.get(category, 0.05)  # Default 5% tax if category not found
            line_tax = round(line_subtotal * tax_rate, 2)

            gross_subtotal += line_subtotal
            total_tax += line_tax

            itemized_receipt.append({
                "name": name,
                "category": category,
                "price": price,
                "quantity": qty,
                "subtotal": line_subtotal,
                "tax": line_tax
            })

        gross_subtotal = round(gross_subtotal, 2)
        total_tax = round(total_tax, 2)

        # 2. Evaluate Threshold Discounts
        applicable_discount_pct = 0.0
        for threshold, disc_pct in self.discount_thresholds:
            if gross_subtotal >= threshold:
                applicable_discount_pct = disc_pct

        raw_discount_amount = gross_subtotal * (applicable_discount_pct / 100.0)

        # 3. Enforce Maximum Concession Cap
        max_allowed_discount = gross_subtotal * (self.max_discount_cap_pct / 100.0)
        final_discount = min(raw_discount_amount, max_allowed_discount)
        final_discount = round(final_discount, 2)

        # 4. Calculate Final Net Payable
        net_payable = round((gross_subtotal + total_tax) - final_discount, 2)

        return {
            "receipt": itemized_receipt,
            "gross_subtotal": gross_subtotal,
            "total_tax": total_tax,
            "discount_pct_applied": applicable_discount_pct,
            "discount_amount": final_discount,
            "net_payable": net_payable
        }

# --- Sample Execution ---
if __name__ == "__main__":
    # Category Tax Rates
    tax_rules = {
        "Grocery": 0.0,       # Tax-free essentials
        "Clothing": 0.08,     # 8% clothing tax
        "Electronics": 0.18,  # 18% electronics tax
        "Home": 0.10          # 10% home goods tax
    }

    # Threshold Discounts: Spend >= $100 -> 5% off, >= $250 -> 12% off, >= $500 -> 20% off
    threshold_rules = [
        (100.0, 5.0),
        (250.0, 12.0),
        (500.0, 20.0)
    ]

    billing_engine = RetailBillingSystem(
        category_taxes=tax_rules,
        discount_thresholds=threshold_rules,
        max_discount_cap_pct=25.0
    )

    # Sample Shopping Cart
    cart = [
        {"name": "Organic Almond Milk", "category": "Grocery", "price": 4.50, "quantity": 3},
        {"name": "Designer Denim Jeans", "category": "Clothing", "price": 85.00, "quantity": 2},
        {"name": "Wireless Mechanical Keyboard", "category": "Electronics", "price": 120.00, "quantity": 1},
        {"name": "Ceramic Coffee Mug Set", "category": "Home", "price": 32.00, "quantity": 2}
    ]

    invoice = billing_engine.process_bill(cart)

    print("==================================================")
    print("                RETAIL TAX INVOICE                ")
    print("==================================================")
    for row in invoice['receipt']:
        print(f"{row['name']} ({row['quantity']}x @ ${row['price']:.2f})")
        print(f"  Category: {row['category']} | Subtotal: ${row['subtotal']:.2f} | Tax: ${row['tax']:.2f}")
        print("-" * 50)

    print("==================================================")
    print(f"GROSS SUBTOTAL      : ${invoice['gross_subtotal']:.2f}")
    print(f"TOTAL TAX           : ${invoice['total_tax']:.2f}")
    print(f"DISCOUNT ({invoice['discount_pct_applied']}%)       : -${invoice['discount_amount']:.2f}")
    print("==================================================")
    print(f"FINAL NET PAYABLE   : ${invoice['net_payable']:.2f}")
    print("==================================================")
