from datetime import datetime, timedelta

# --- Scaled Progression Constants ---
EXP_TARGET_GRADE_3 = 15000  # Threshold to hit Grade 3
EXP_TARGET_GRADE_2 = 60000  # Threshold to hit Grade 2 (Cumulative)

PERFECT_WEEK_BONUS_G4 = 200
PERFECT_WEEK_BONUS_G3 = 350

STREAK_BONUS_PER_WEEK = 10

def process_workout_log(current_exp, current_grade, last_logged_str, weekly_count, current_streak):
    """
    Evaluates progression metrics, updates EXP balances, calculates streaks,
    and enforces dynamic rewards based on the user's current Shonen Grade.
    """
    now = datetime.now()
    
    # 1. TIME-LOCK CHECK: Anti-Cheat Mechanism
    if last_logged_str:
        last_logged_time = datetime.fromisoformat(last_logged_str)
        time_elapsed = now - last_logged_time
        
        if time_elapsed < timedelta(hours=24):
            time_remaining = timedelta(hours=24) - time_elapsed
            hours, remainder = divmod(time_remaining.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return {
                "status": "locked",
                "message": f"⚠️ Training cooldown active! Your muscles need rest. Try again in {hours}h {minutes}m.",
                "total_exp": current_exp,
                "current_grade": current_grade
            }

    # 2. DYNAMIC BASE EXP & STREAK SCALING BASED ON GRADE
    if current_grade == "Grade 4":
        base_exp = 150
        max_streak_bonus = 50
        perfect_week_bonus = PERFECT_WEEK_BONUS_G4
    else:  # Grade 3 and above scales up in intensity
        base_exp = 200
        max_streak_bonus = 100
        perfect_week_bonus = PERFECT_WEEK_BONUS_G3
        
    streak_modifier = min(current_streak * STREAK_BONUS_PER_WEEK, max_streak_bonus)
    earned_exp = base_exp + streak_modifier
    
    new_exp = current_exp + earned_exp
    new_weekly_count = weekly_count + 1
    
    # 3. EVALUATE PERFECT WEEK BONUS (Triggers on 4th workout of the week)
    triggered_bonus = False
    if new_weekly_count == 4:
        new_exp += perfect_week_bonus
        triggered_bonus = True
        
    # 4. MULTI-TIER RANK PROMOTION LOGIC
    new_grade = current_grade
    rank_upgraded = False
    
    if current_grade == "Grade 4" and new_exp >= EXP_TARGET_GRADE_3:
        new_grade = "Grade 3"
        rank_upgraded = True
    elif current_grade == "Grade 3" and new_exp >= EXP_TARGET_GRADE_2:
        new_grade = "Grade 2"
        rank_upgraded = True

    return {
        "status": "success",
        "message": f"🔥 Workout Logged! Claimed +{earned_exp} EXP" + (f" plus a +{perfect_week_bonus} EXP Perfect Week Bonus!" if triggered_bonus else "."),
        "total_exp": new_exp,
        "current_grade": new_grade,
        "weekly_count": new_weekly_count,
        "rank_upgraded": rank_upgraded,
        "timestamp_iso": now.isoformat()
    }

# Local verification block to test Grade 3 execution
if __name__ == "__main__":
    print("--- TESTING GRADE 3 LOG ATTEMPT (SCALED REWARDS CHECK) ---")
    over_a_day_ago = (datetime.now() - timedelta(hours=26)).isoformat()
    
    # Simulate a Grade 3 user with a strong 8-week streak logging their 4th workout
    grade3_test = process_workout_log(
        current_exp=59400, current_grade="Grade 3", last_logged_str=over_a_day_ago, weekly_count=3, current_streak=8
    )
    print(grade3_test["message"])
    print(f"Updated Profile State -> Grade: {grade3_test['current_grade']} | Total EXP: {grade3_test['total_exp']} | Rank Up: {grade3_test['rank_upgraded']}") 