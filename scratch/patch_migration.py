import sys

def patch():
    with open('scratch/migrate_to_new_school.py', 'r') as f:
        content = f.read()

    old_slot_loop = """for slot in sqlite_slots:
    new_id = str(uuid.uuid4())
    slot_map[slot[0]] = new_id
    pg_slot = TimetableSlot(
        id=new_id,
        division_id=div_map[slot[1]],
        subject_id=subject_map[slot[2]],
        teacher_id=teacher_map[slot[3]],
        day_of_week=slot[4],
        period_number=slot[5]
    )
    pg_db.add(pg_slot)"""

    new_slot_loop = """for slot in sqlite_slots:
    if slot[1] not in div_map or slot[2] not in subject_map or slot[3] not in teacher_map:
        continue
    new_id = str(uuid.uuid4())
    slot_map[slot[0]] = new_id
    pg_slot = TimetableSlot(
        id=new_id,
        division_id=div_map[slot[1]],
        subject_id=subject_map[slot[2]],
        teacher_id=teacher_map[slot[3]],
        day_of_week=slot[4],
        period_number=slot[5]
    )
    pg_db.add(pg_slot)"""

    content = content.replace(old_slot_loop, new_slot_loop)

    with open('scratch/migrate_to_new_school.py', 'w') as f:
        f.write(content)

patch()
