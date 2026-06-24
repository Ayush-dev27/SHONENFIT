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
    "itadori": {
        "physique": {
            "focus": "Thick, athletic torso development, explosive quad mass, and high-density functional shoulder width.",
            "exercises": ["Barbell Back Squats", "Weighted Dips", "Barbell Bent Over Rows", "Hammer Curls", "Ab Wheel Rollouts"]
        },
        "train-like": {
            "focus": "Insane knee/hip extension power, raw martial arts durability, and high-impact kinetic force tracking.",
            "exercises": ["Power Cleans", "Plyometric Knee-to-Chest Jumps", "Heavy Sandbag Carries", "Medicine Ball Underhand Throws", "Burpee Pull-Ups"]
        }
    },
    "maki": {
        "physique": {
            "focus": "V-taper upper back expansion, lean core definition, posture corrections, and unilateral lower body symmetry.",
            "exercises": ["Lat Pulldowns", "Dumbbell Romanian Deadlifts", "Overhead Dumbbell Press", "Bulgarian Split Squats", "Plank Variations"]
        },
        "train-like": {
            "focus": "Weapon handling grip stamina, elite rotational core velocity, lightning agility reflexes, and systemic conditioning.",
            "exercises": ["Kettlebell Snatches", "Barbell Landmine Rotations", "Towel Pull-Ups", "Agility Ladder Fast-Footwork Chains", "Jump Rope Double Unders"]
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
    "tengen": {
        "physique": {
            "focus": "Flashy, maximalist hypertrophy design targeting explosive shoulder caps, massive bicep peaks, and thick chest volume.",
            "exercises": ["Dumbbell Lateral Raises (High Volume)", "Incline Barbell Bench Press", "Barbell Bicep Curls", "Dumbbell Shrugs", "Cable Flyes"]
        },
        "train-like": {
            "focus": "Heavy dual-load grip endurance, rapid directional kinetic speed bursts, and upper-body shock absorption.",
            "exercises": ["Heavy Farmer's Walks", "Explosive Push-Ups (Clapping)", "Dumbbell Renegade Rows", "Sledgehammer Tire Slams", "Assault Bike Sprints"]
        }
    },
    "inosuke": {
        "physique": {
            "focus": "Gritty, serratus anterior visibility, jagged lower abdominal definitions, and highly functional kinetic spinal thickness.",
            "exercises": ["Hanging Toes-to-Bar", "Decline Dumbbell Bench Press", "Pull-Ups (Wide Grip)", "Walking Lunges", "Russian Twists"]
        },
        "train-like": {
            "focus": "Unanchored multi-directional joint mobility, extreme posterior chain flexibility, and unpredictable animalistic endurance.",
            "exercises": ["Deep Cossack Squats", "Bear Crawls (Timed)", "Kettlebell Windmills", "Burping Broad Jumps", "Hindu Push-Ups"]
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
    },
    "bakugo": {
        "physique": {
            "focus": "Explosive upper body symmetry focusing heavily on high-density forearms, wide lats, and powerful tricep extensions.",
            "exercises": ["Close-Grip Bench Press", "Weighted Pull-Ups", "Barbell Wrist Curls", "Dumbbell Overhead Extensions", "Cable Rows"]
        },
        "train-like": {
            "focus": "Rapid-fire upper extremity force output, elastic wrist/forearm conditioning, and fast-twitch dynamic redirection capabilities.",
            "exercises": ["Medicine Ball Chest Passes", "Battle Rope Slams (Fast Tempo)", "Kettlebell Push Presses", "Box Drills (Lateral Bounds)", "Plank Jacks"]
        }
    },
    "all-might": {
        "physique": {
            "focus": "Classic Golden-Era absolute mass hypertrophy, maximum skeletal load density, wide armor plate chest configuration.",
            "exercises": ["Barbell Bench Press (Heavy)", "Barbell Back Squats (Heavy)", "Barbell Deadlifts (Heavy)", "Seated Barbell Overhead Press", "Barbell Curls"]
        },
        "train-like": {
            "focus": "Ultimate kinetic force generation, breaking absolute maximal strength thresholds, full-body absolute structural stability.",
            "exercises": ["Heavy Log Clean and Press", "Rack Pulls (Above Knee)", "Heavy Sled Drags", "Medicine Ball Overhead Slams", "Farmer's Carries (Max Weight)"]
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