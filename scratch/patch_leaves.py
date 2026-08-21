import sys
import os

def patch_leaves():
    with open('app/api/routes/leaves.py', 'r') as f:
        content = f.read()

    # Replace KeyError prone section for today_slots
    old_slots_loop = """    for s in today_slots:
        if s.teacher_id in daily_loads:
            daily_loads[s.teacher_id] += 1
        busy_teachers_per_period[s.period_number].add(s.teacher_id)"""

    new_slots_loop = """    for s in today_slots:
        if s.teacher_id in daily_loads:
            daily_loads[s.teacher_id] += 1
        if s.period_number not in busy_teachers_per_period:
            busy_teachers_per_period[s.period_number] = set()
        busy_teachers_per_period[s.period_number].add(s.teacher_id)"""

    content = content.replace(old_slots_loop, new_slots_loop)

    # Replace KeyError prone section for today_subs
    old_subs_loop = """    for sub in today_subs:
        if sub.substitute_teacher_id in daily_loads:
            daily_loads[sub.substitute_teacher_id] += 1
        period = sub.original_slot.period_number
        busy_teachers_per_period[period].add(sub.substitute_teacher_id)"""

    new_subs_loop = """    for sub in today_subs:
        if sub.substitute_teacher_id in daily_loads:
            daily_loads[sub.substitute_teacher_id] += 1
        period = sub.original_slot.period_number
        if period not in busy_teachers_per_period:
            busy_teachers_per_period[period] = set()
        busy_teachers_per_period[period].add(sub.substitute_teacher_id)"""

    content = content.replace(old_subs_loop, new_subs_loop)

    with open('app/api/routes/leaves.py', 'w') as f:
        f.write(content)

patch_leaves()
