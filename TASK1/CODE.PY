class ScholarshipSystem:
    def __init__(self, min_aggregate, min_subject_score, min_attendance, max_income, quota):
        self.min_aggregate = min_aggregate
        self.min_subject_score = min_subject_score
        self.min_attendance = min_attendance
        self.max_income = max_income
        self.quota = quota

    def evaluate_applicants(self, applicants):
        eligible_pool = []
        rejected_pool = []

        for app in applicants:
            reasons = []
            
            # 1. Check aggregate marks
            if app["aggregate"] < self.min_aggregate:
                reasons.append(f"Aggregate marks {app['aggregate']}% below minimum {self.min_aggregate}%")
            
            # 2. Check subject-wise minimum scores
            for subject, score in app["subject_scores"].items():
                if score < self.min_subject_score:
                    reasons.append(f"Score in {subject} ({score}) below minimum {self.min_subject_score}")
            
            # 3. Check attendance
            if app["attendance"] < self.min_attendance:
                reasons.append(f"Attendance {app['attendance']}% below minimum {self.min_attendance}%")
            
            # 4. Check income criteria
            if app["income"] > self.max_income:
                reasons.append(f"Income ${app['income']} exceeds maximum limit ${self.max_income}")

            if reasons:
                app["reasons"] = "; ".join(reasons)
                rejected_pool.append(app)
            else:
                eligible_pool.append(app)

        # Sort eligible students: Aggregate (DESC), Attendance (DESC), Income (ASC)
        eligible_pool.sort(key=lambda x: (-x["aggregate"], -x["attendance"], x["income"]))

        # Allocate scholarships based on quota
        allocated_scholars = eligible_pool[:self.quota]
        waitlisted = eligible_pool[self.quota:]

        return allocated_scholars, waitlisted, rejected_pool

# --- Sample Execution ---
if __name__ == "__main__":
    system = ScholarshipSystem(
        min_aggregate=80.0,
        min_subject_score=65.0,
        min_attendance=75.0,
        max_income=50000.0,
        quota=2
    )

    applicants = [
        {
            "id": "A001", "name": "Alice Smith", "aggregate": 92.5,
            "subject_scores": {"Math": 90, "Physics": 95, "English": 88},
            "attendance": 94.0, "income": 42000.0
        },
        {
            "id": "A002", "name": "Bob Jones", "aggregate": 85.0,
            "subject_scores": {"Math": 60, "Physics": 80, "English": 85}, # Fails Math min (60 < 65)
            "attendance": 88.0, "income": 35000.0
        },
        {
            "id": "A003", "name": "Charlie Brown", "aggregate": 92.5,
            "subject_scores": {"Math": 92, "Physics": 93, "English": 92},
            "attendance": 98.0, "income": 38000.0
        },
        {
            "id": "A004", "name": "Diana Prince", "aggregate": 89.0,
            "subject_scores": {"Math": 85, "Physics": 90, "English": 92},
            "attendance": 90.0, "income": 55000.0 # Exceeds max income
        }
    ]

    scholars, waitlisted, rejected = system.evaluate_applicants(applicants)

    print("=== ALLOCATED SCHOLARS ===")
    for s in scholars:
        print(f"ID: {s['id']}, Name: {s['name']}, Aggregate: {s['aggregate']}%")

    print("\n=== WAITLISTED ===")
    for w in waitlisted:
        print(f"ID: {w['id']}, Name: {w['name']}")

    print("\n=== REJECTED ===")
    for r in rejected:
        print(f"ID: {r['id']}, Name: {r['name']} | Reason: {r['reasons']}")
