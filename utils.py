def print_plan(plan: dict) -> None:
    print("=" * 50)
    print("STUDY PLAN ")
    print("=" * 50)

    print(f"Goal: {plan.get('goal', 'N/A')}")
    print(f"Days: {plan.get('days', 'N/A')}")

    daily = plan.get("daily_plan", [])
    if isinstance(daily, list):
        for d in daily:
            day = d.get('day', '?')
            focus = d.get("focus", "")
            minutes = d.get('minutes', "")
            tasks = d.get("tasks", [])
            print(f"Day {day}: {focus} ({minutes} min)")
            if isinstance(tasks, list):
                for t in tasks:
                    print(f"   - {t}")
            print()

    tips = plan.get("tips", [])
    if isinstance(tips, list) and tips:
        print('Tips:')
        for tip in tips:
            print(f"- {tip}")
    print()