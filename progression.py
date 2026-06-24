from datetime import datetime, timedelta

# Core Progression Constants
EXP_TARGET_GRADE_3 = 15000  # Sets up the target 4-5 month grind
BASE_WORKOUT_EXP = 150
PERFECT_WEEK_BONUS = 200
STREAK_BONUS_PER_WEEK = 10
MAX_STREAK_BONUS = 50

def process_workout_log(current_exp, current_grade, last_logged_str, weekly_count, current_streak):
    """
    Evaluates progression metrics, updates EXP balances, calculates streaks,
    and enforces the strict 24-hour time-lock anti-cheat mechanic.
    """
    now = datetime.now()
    
    # 1. TIME-LOCK CHECK: Anti-Cheat Mechanism
    if last_logged_str:
        # Convert stored ISO timestamp string back to a Python datetime object
        last_logged_time = datetime.fromisoformat(last_logged_str)
        
        # Calculate time delta since last submission
        time_elapsed = now - last_logged_time
        
        # Enforce strict 24-hour cooldown lock
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

    # 2. CALCULATE THE DISCIPLINE STREAK MULTIPLIER
    # Streak bonus scales up by +10 EXP per consecutive training week, maxing out at +50
    streak_modifier = min(current_streak * STREAK_BONUS_PER_WEEK, MAX_STREAK_BONUS)
    earned_exp = BASE_WORKOUT_EXP + streak_modifier
    
    new_exp = current_exp + earned_exp
    new_weekly_count = weekly_count + 1
    
    # 3. CALCULATE PERFECT WEEK BONUS (Triggers on 4th workout of the week)
    triggered_bonus = False
    if new_weekly_count == 4:
        new_exp += PERFECT_WEEK_BONUS
        triggered_bonus = True
        
    # 4. EVALUATE RANK PROMOTION (Grade 4 -> Grade 3)
    new_grade = current_grade
    rank_upgraded = False
    
    if current_grade == "Grade 4" and new_exp >= EXP_TARGET_GRADE_3:
        new_grade = "Grade 3"
        rank_upgraded = True

    return {
        "status": "success",
        "message": f"🔥 Workout Logged! Claimed +{earned_exp} EXP" + (" plus a +200 EXP Perfect Week Bonus!" if triggered_bonus else "."),
        "total_exp": new_exp,
        "current_grade": new_grade,
        "weekly_count": new_weekly_count,
        "rank_upgraded": rank_upgraded,
        "timestamp_iso": now.isoformat()
    }

# Local verification block to test the math execution
if __name__ == "__main__":
    print("--- TESTING RECENT LOG ATTEMPT (CHEAT PREVENT CHECK) ---")
    # Simulate a user trying to log a workout just 3 hours after their last one
    three_hours_ago = (datetime.now() - timedelta(hours=3)).isoformat()
    cheat_test = process_workout_log(
        current_exp=1200, current_grade="Grade 4", last_logged_str=three_hours_ago, weekly_count=1, current_streak=2
    )
    print(cheat_test["message"])
    
    print("\n--- TESTING LEGITIMATE LOG ATTEMPT (EXP CALC CHECK) ---")
    # Simulate a user logging a valid session after 26 hours
    over_a_day_ago = (datetime.now() - timedelta(hours=26)).isoformat()
    valid_test = process_workout_log(
        current_exp=14800, current_grade="Grade 4", last_logged_str=over_a_day_ago, weekly_count=3, current_streak=3
    )
    print(valid_test["message"])
    print(f"Updated Profile State -> Grade: {valid_test['current_grade']} | Total EXP: {valid_test['total_exp']}") 