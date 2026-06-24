import re

# --- Master Training Templates Database ---
CHARACTER_TEMPLATES = {
    "toji": {
        "physique": {
            "focus": "Hypertrophy for dense muscular mass, wide V-taper lat width, and low body fat symmetry.",
            "exercises": ["Weighted Pull-Ups", "Incline Dumbbell Bench Press", "Barbell Romanian Deadlifts", "Lateral Raises", "Hanging Leg Raises"]
        },
        "train-like": {
            "focus": "Peak human functional power, explosive speed output, rotational core velocity, and spatial agility.",
            "exercises": ["Heavy Barbell Deadlifts", "Medicine Ball Rotational Slams", "Plyometric Box Jumps", "Kettlebell Swings", "Farmer's Walks"]
        }
    },
    "tanjiro": {
        "physique": {
            "focus": "Lean, athletic muscle retention with high emphasis on quadriceps, core thickness, and upper back density.",
            "exercises": ["Front Squats", "Barbell Rows", "Overhead Press", "Ab Wheel Rollouts", "Calf Raises"]
        },
        "train-like": {
            "focus": "Absolute VO2 max cardiovascular endurance, continuous breath control conditioning, and high-velocity sword forms.",
            "exercises": ["Dumbbell Thrusters", "High-Intensity Kettlebell Slashes", "Sprint Intervals (400m)", "Burpees", "Plank-to-Pushups"]
        }
    },
    "deku": {
        "physique": {
            "focus": "Full-body thickness, massive shoulder cap rounding, thick traps, and powerful explosive lower body hypertrophy.",
            "exercises": ["Barbell Back Squats", "Overhead Barbell Press", "Dumbbell Shrugs", "Push-Ups (Weighted)", "Hamstring Curls"]
        },
        "train-like": {
            "focus": "Reactive plyometric impact management, full-body power distribution, kinetic chain conversion, and shock absorption.",
            "exercises": ["Depth Jumps to Explosive Bounds", "Power Cleans", "Clapping Push-Ups", "Heavy Sled Pushes", "Jump Squats"]
        }
    }
}

def generate_custom_routine(profile_data):
    """
    Takes a user profile data dictionary and calculates a personalized, 
    biologically scaled, safety-filtered Shonen training program.
    """
    # Clean string matching identifiers
    universe = profile_data.get("selectedUniverse", "").lower()
    char_name = profile_data.get("selectedCharacter", "").lower().split(" ")[0] # extract 'toji', 'tanjiro', 'deku'
    strategy = profile_data.get("strategyGoal", "physique").lower()
    
    weight = float(profile_data.get("weight", 70))
    height = float(profile_data.get("height", 175))
    medical_history = profile_data.get("medicalHistory", "").lower()

    # 1. Fallback Route Protection: Ensure character template mapping exists
    if char_name not in CHARACTER_TEMPLATES:
        # Default fallback to Toji paradigm if unknown
        char_name = "toji"
        
    base_plan = CHARACTER_TEMPLATES[char_name][strategy]
    
    # 2. The Biometric Scaling Algorithm
    # We dynamically calculate working sets and target rep ranges based on biological baselines
    calculated_routines = []
    
    for exercise in base_plan["exercises"]:
        # If strategy is bodybuilding/hypertrophy: volume balances between 3-4 sets of 8-12 reps
        if strategy == "physique":
            sets = 4 if weight >= 75 else 3
            reps = "8 to 12 reps"
            intensity = "Focus on a 3-second negative eccentric tempo for maximal mechanical hypertrophy damage."
        # If strategy is athletic conditioning: performance requires explosive power sets or structural time windows
        else:
            sets = 5 if height >= 180 else 4
            reps = "5 explosive reps" if "Deadlift" in exercise or "Clean" in exercise else "45 seconds max effort"
            intensity = "Execute with maximal concentric velocity. Rest fully between sets to prevent neural fatigue."
            
        calculated_routines.append({
            "name": exercise,
            "sets": sets,
            "reps": reps,
            "coaching_cue": intensity
        })

    # 3. The Medical Injury Safety Filtering Engine
    # If the user has joint injuries, we actively intercept dangerous movements and swap them with safe isolations
    final_filtered_routines = []
    knee_injury_keywords = ["knee", "acl", "meniscus", "patella"]
    back_injury_keywords = ["back", "spine", "lumber", "herniated", "slip disc"]

    for item in calculated_routines:
        ex_name = item["name"]
        
        # Filter for Knee Injuries
        if any(keyword in medical_history for keyword in knee_injury_keywords):
            if any(unsafe in ex_name.lower() for unsafe in ["squat", "box jump", "depth jump", "sled"]):
                item["name"] = "Isolated Leg Extensions (Slow Tempo)"
                item["reps"] = "15 controlled reps"
                item["coaching_cue"] = "⚠️ SAFETY ALTERNATIVE: Replaced explosive lower body knee flexion with an open-chain static isolation to fully protect your joint injury configuration."
                
        # Filter for Lower Back/Spine Injuries
        if any(keyword in medical_history for keyword in back_injury_keywords):
            if any(unsafe in ex_name.lower() for unsafe in ["deadlift", "squat", "row", "clean"]):
                item["name"] = "Chest-Supported Dumbbell Rows or Glute Bridges"
                item["reps"] = "12 to 15 reps"
                item["coaching_cue"] = "⚠️ SAFETY ALTERNATIVE: Compounding load removed from the lumbar spine column. Axial skeleton loading avoided to shield your lower back injury."

        final_filtered_routines.append(item)

    # 4. Compile Output Payload Context
    return {
        "character_alignment": char_name.upper(),
        "strategy_paradigm": strategy.upper(),
        "core_focus_directive": base_plan["focus"],
        "assigned_workout_routine": final_filtered_routines
    }

# Quick testing loop to ensure your code runs cleanly locally
if __name__ == "__main__":
    test_user_profile = {
        "selectedUniverse": "jjk",
        "selectedCharacter": "Toji Fushiguro",
        "strategyGoal": "train-like",
        "weight": 82,
        "height": 185,
        "medicalHistory": "I have chronic lower back pain and a mild slip disc issue."
    }
    
    result = generate_custom_routine(test_user_profile)
    print(f"--- PROTOCOL INITIALIZATION FOR USER TARGET: {result['character_alignment']} ({result['strategy_paradigm']}) ---")
    print(f"Directive Focus: {result['core_focus_directive']}\n")
    for index, ex in enumerate(result['assigned_workout_routine'], start=1):
        print(f"{index}. {ex['name']} -> {ex['sets']} sets x {ex['reps']}")
        print(f"   Cue: {ex['coaching_cue']}") 