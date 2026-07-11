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

def calculate_fatigue_status(user_id):
    """
    Queries the workout_logs table to evaluate the user's 7-day acute workload 
    against their 28-day chronic baseline, preventing burnout using the ACWR model.
    """
    import sqlite3
    
    conn = sqlite3.connect('shonenfit.db')
    cursor = conn.cursor()
    
    try:
        # 1. Fetch total training volume for the Acute phase (Last 7 Days)
        cursor.execute('''
            SELECT COALESCE(SUM(reps_completed * weight_kg), 0) 
            FROM workout_logs 
            WHERE user_id = ? AND log_date >= date('now', '-7 days')
        ''', (user_id,))
        acute_workload = cursor.fetchone()[0]
        
        # 2. Fetch total training volume for the Chronic phase (Last 28 Days)
        cursor.execute('''
            SELECT COALESCE(SUM(reps_completed * weight_kg), 0) 
            FROM workout_logs 
            WHERE user_id = ? AND log_date >= date('now', '-28 days')
        ''', (user_id,))
        total_chronic_volume = cursor.fetchone()[0]
        
        # Calculate weekly average baseline over a 4-week span
        chronic_workload = total_chronic_volume / 4.0
        
        # 3. Base Case: If the user has sparse history, keep status baseline optimal
        if chronic_workload == 0:
            return {
                "ratio": 1.0,
                "status": "OPTIMAL",
                "message": "🔥 Baseline established. Body is fully adapted and ready to train."
            }
            
        # 4. Compute Acute-to-Chronic Ratio
        acwr_ratio = round(acute_workload / chronic_workload, 2)
        
        # 5. Route threshold conditions to provide actionable training advice
        if acwr_ratio < 0.8:
            status = "UNDER_TRAINING"
            message = "💤 Fatigue is low, but volume dropped. Time to scale up intensity to prevent detraining!"
        elif 0.8 <= acwr_ratio <= 1.3:
            status = "OPTIMAL"
            message = "💪 Sweet spot achieved! Workload is perfectly balanced. Prime state to push for a new PR!"
        elif 1.3 < acwr_ratio <= 1.5:
            status = "HIGH_FATIGUE"
            message = "⚠️ Workload climbing fast. Fatigue accumulation is out-pacing recovery. Focus on deep rest cycles."
        else: # Ratio climbs greater than 1.5
            status = "DANGER_ZONE"
            message = "🚨 CRITICAL OVER-TRAINING! Workload spike detected. Deload immediately to protect against systemic breakdown."
            
        return {
            "ratio": acwr_ratio,
            "status": status,
            "message": message
        }
        
    except Exception as e:
        print(f"❌ Error computing fatigue engine metrics: {e}")
        return {"ratio": 1.0, "status": "OPTIMAL", "message": "Error reading metrics."}
        
    finally:
        conn.close() 