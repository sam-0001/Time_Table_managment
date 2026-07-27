from ortools.sat.python import cp_model
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class TimetableGenerator:
    def __init__(
        self,
        teachers: List[Dict], # [{id, max_weekly, max_daily, is_class_teacher_of}]
        classes: List[Dict], # [{id, name}]
        divisions: List[Dict], # [{id, class_id}]
        subjects: List[Dict], # [{id, is_lab, double_period_allowed}]
        teacher_subjects: List[Dict], # [{teacher_id, subject_id, division_id, weekly_periods}]
        days: int = 5,
        periods_per_day: int = 7,
        lunch_break_period: int = 4,
        weekly_schedule: List[Dict] = None,
        global_max_weekly_teacher_periods: int = 32
    ):
        self.teachers = teachers
        self.classes = classes
        self.divisions = divisions
        self.subjects = subjects
        self.teacher_subjects = teacher_subjects
        self.days = days
        self.global_max_weekly = global_max_weekly_teacher_periods
        self.periods = periods_per_day
        self.lunch_break_period = lunch_break_period
        
        self.schedule_config = []
        if weekly_schedule:
            for day_conf in weekly_schedule:
                if not day_conf.get("is_working", True):
                    continue
                day_index = day_conf["day"]
                periods = day_conf["periods"]
                for p in range(periods):
                    self.schedule_config.append((day_index, p))
        else:
            for day_index in range(self.days):
                for p in range(self.periods):
                    self.schedule_config.append((day_index, p))
        
        self.model = cp_model.CpModel()
        self.assignments = {} # (teacher, division, subject, day, period) -> BoolVar
        
    def generate(self):
        # 1. Create variables
        for ts in self.teacher_subjects:
            t = ts["teacher_id"]
            d = ts["division_id"]
            s = ts["subject_id"]
            for day, p in self.schedule_config:
                name = f"assign_t{t}_d{d}_s{s}_day{day}_p{p}"
                self.assignments[(t, d, s, day, p)] = self.model.NewBoolVar(name)
        
        # 2. Constraints
        
        # C1: Complete required weekly subject periods
        for ts in self.teacher_subjects:
            t = ts["teacher_id"]
            d = ts["division_id"]
            s = ts["subject_id"]
            required_periods = ts["weekly_periods"]
            
            # Sum of assignments for this teacher-subject-division must equal required_periods
            self.model.Add(
                sum(self.assignments[(t, d, s, day, p)] 
                    for day, p in self.schedule_config) == required_periods
            )
            
        # C2: No teacher clashes (teacher can be in only one division at a time)
        for t in {ts["teacher_id"] for ts in self.teacher_subjects}:
            for day, p in self.schedule_config:
                # Sum of assignments for this teacher on this day and period across all divisions/subjects <= 1
                self.model.Add(
                    sum(self.assignments[(t, ts["division_id"], ts["subject_id"], day, p)]
                        for ts in self.teacher_subjects if ts["teacher_id"] == t) <= 1
                )
                    
        # C3: No division clashes (division can have only one teacher/subject at a time)
        for d in {ts["division_id"] for ts in self.teacher_subjects}:
            for day, p in self.schedule_config:
                self.model.Add(
                    sum(self.assignments[(ts["teacher_id"], d, ts["subject_id"], day, p)]
                        for ts in self.teacher_subjects if ts["division_id"] == d) <= 1
                )
                    
        # C4: Maximum daily periods per teacher (Auto-calculated as total periods - 1)
        for t_info in self.teachers:
            t = t_info["id"]
            
            unique_days = list(set([day for day, p in self.schedule_config]))
            for day in unique_days:
                day_periods = [p for d_i, p in self.schedule_config if d_i == day]
                periods_today = len(day_periods)
                
                # Rule: Max daily is ALWAYS one less than total periods today, but respect individual teacher limits if lower
                max_daily = min(t_info.get("max_daily", 7), max(0, periods_today - 1))
                
                self.model.Add(
                    sum(self.assignments[(ts["teacher_id"], ts["division_id"], ts["subject_id"], day, p)]
                        for ts in self.teacher_subjects if ts["teacher_id"] == t 
                        for day_i, p in self.schedule_config if day_i == day) <= max_daily
                )

        # C5: Teacher workload balancing (Respect teacher's max_weekly with a +2 tolerance)
        for t_info in self.teachers:
            t = t_info["id"]
            max_weekly = t_info.get("max_weekly", self.global_max_weekly) + 2
            
            total_assigned = sum(
                self.assignments[(ts["teacher_id"], ts["division_id"], ts["subject_id"], day, p)]
                for ts in self.teacher_subjects if ts["teacher_id"] == t 
                for day, p in self.schedule_config
            )
            self.model.Add(total_assigned <= max_weekly)

        # C8: Class teacher takes first period (attendance)
        for t_info in self.teachers:
            t = t_info["id"]
            d = t_info.get("is_class_teacher_of")
            if d:
                teaches_d = [ts for ts in self.teacher_subjects if ts["teacher_id"] == t and ts["division_id"] == d]
                if teaches_d:
                    total_weekly = sum(ts["weekly_periods"] for ts in teaches_d)
                    unique_days = list(set([day for day, p in self.schedule_config]))
                    days_with_p0 = [day for day in unique_days if any(day_i == day and p == 0 for day_i, p in self.schedule_config)]
                    
                    if total_weekly >= len(days_with_p0):
                        for day in days_with_p0:
                            self.model.Add(
                                sum(self.assignments[(ts["teacher_id"], ts["division_id"], ts["subject_id"], day, 0)]
                                    for ts in teaches_d) == 1
                            )

        # C9: No subject more than 2 consecutive periods
        for d in {ts["division_id"] for ts in self.teacher_subjects}:
            for s in {ts["subject_id"] for ts in self.teacher_subjects if ts["division_id"] == d}:
                # Find which teacher teaches this subject to this division
                t = next((ts["teacher_id"] for ts in self.teacher_subjects if ts["division_id"] == d and ts["subject_id"] == s), None)
                if not t: continue
                
                unique_days = list(set([day for day, p in self.schedule_config]))
                for day in unique_days:
                    day_periods = [p for d_i, p in self.schedule_config if d_i == day]
                    day_periods.sort()
                    for i in range(len(day_periods) - 2):
                        p1, p2, p3 = day_periods[i], day_periods[i+1], day_periods[i+2]
                        # Prevent 3 consecutive periods of the same subject
                        self.model.Add(
                            self.assignments[(t, d, s, day, p1)] + 
                            self.assignments[(t, d, s, day, p2)] + 
                            self.assignments[(t, d, s, day, p3)] <= 2
                        )

        # C7: Class Teacher in First Period
        for d in {ts["division_id"] for ts in self.teacher_subjects}:
            # Find class teacher for this division
            t = next((t_info["id"] for t_info in self.teachers if t_info.get("is_class_teacher_of") == d), None)
            if t:
                subjects_taught = [ts["subject_id"] for ts in self.teacher_subjects if ts["teacher_id"] == t and ts["division_id"] == d]
                if subjects_taught:
                    total_periods = sum(ts["weekly_periods"] for ts in self.teacher_subjects if ts["teacher_id"] == t and ts["division_id"] == d)
                    unique_days = list(set([day for day, p in self.schedule_config]))
                    first_periods_count = len([day for day in unique_days if (day, 0) in self.schedule_config])
                    
                    # Number of 1st periods the class teacher MUST take
                    required_first_periods = min(first_periods_count, total_periods)
                    
                    first_periods_vars = []
                    for day in unique_days:
                        if (day, 0) in self.schedule_config:
                            first_periods_vars.extend([self.assignments[(t, d, s, day, 0)] for s in subjects_taught])
                    
                    if first_periods_vars:
                        # Enforce they take exactly the required number of first periods
                        self.model.Add(sum(first_periods_vars) == required_first_periods)

        # Objectives (Soft Constraints)
        objective_terms = []
        
        # O1: Maximize assignments of class teacher to the first period of the day (fallback/bonus for edge cases)
        for t_info in self.teachers:
            t = t_info["id"]
            ct_div = t_info.get("is_class_teacher_of")
            if ct_div:
                subjects_taught = [ts["subject_id"] for ts in self.teacher_subjects if ts["teacher_id"] == t and ts["division_id"] == ct_div]
                unique_days = list(set([day for day, p in self.schedule_config]))
                for day in unique_days:
                    if (day, 0) in self.schedule_config:
                        var_sum = sum(self.assignments[(t, ct_div, s, day, 0)] for s in subjects_taught)
                        objective_terms.append(100 * var_sum)

        # O2: Subject specific time preferences
        for s_info in self.subjects:
            s_id = s_info["id"]
            s_code = s_info.get("code", "").upper()
            is_double = s_info.get("double_period_allowed", False)
            
            for ts in self.teacher_subjects:
                if ts["subject_id"] == s_id:
                    t = ts["teacher_id"]
                    d = ts["division_id"]
                    
                    unique_days = list(set([day for day, p in self.schedule_config]))
                    for day in unique_days:
                        day_periods = [p for d_i, p in self.schedule_config if d_i == day]
                        day_periods.sort()
                        total_p = len(day_periods)
                        if total_p == 0: continue
                        
                        half_point = total_p // 2
                        
                        for p in day_periods:
                            var = self.assignments[(t, d, s_id, day, p)]
                            
                            s_name = s_info.get("name", "").lower()
                            
                            # Identify non-core subjects that should ideally be late in the day
                            is_late_subject = any(kw in s_name for kw in ["game", "jal suraksha", "pe", "pt", "art", "craft", "music", "sport", "yoga", "we"]) or s_code in ["PE", "WE", "ART"]
                            
                            # Math preferably in first half (core subject)
                            if s_code == "MATH" and p < half_point:
                                objective_terms.append(2 * var)
                            
                            if is_late_subject:
                                # Strong bonus for being in the last 4 periods
                                if p >= max(0, total_p - 4):
                                    objective_terms.append(5 * var)
                                # Medium bonus just for being after the halfway point (post-lunch)
                                elif p >= half_point:
                                    objective_terms.append(2 * var)
                                
                        # Double periods (consecutive) for science practicals or allowed subjects
                        if is_double:
                            for i in range(total_p - 1):
                                p1, p2 = day_periods[i], day_periods[i+1]
                                # We want to maximize the AND of (p1, p2).
                                # We can approximate by adding a bonus for both being true using a boolean indicator
                                b_and = self.model.NewBoolVar(f"double_{t}_{d}_{s_id}_{day}_{p1}")
                                self.model.AddBoolOr([self.assignments[(t, d, s_id, day, p1)].Not(), self.assignments[(t, d, s_id, day, p2)].Not(), b_and])
                                self.model.AddImplication(b_and, self.assignments[(t, d, s_id, day, p1)])
                                self.model.AddImplication(b_and, self.assignments[(t, d, s_id, day, p2)])
                                objective_terms.append(4 * b_and)

        if objective_terms:
            self.model.Maximize(sum(objective_terms))

        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        status = solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            timetable = []
            for (t, d, s, day, p), var in self.assignments.items():
                if solver.Value(var) == 1:
                    timetable.append({
                        "teacher_id": t,
                        "division_id": d,
                        "subject_id": s,
                        "day": day,
                        "period": p
                    })
            return {"status": "SUCCESS", "timetable": timetable}
        else:
            return {"status": "FAILED", "reason": "Could not find a feasible timetable satisfying all constraints."}
