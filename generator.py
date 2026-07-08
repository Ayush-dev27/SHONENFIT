from datetime import datetime


TRACK_FOCUS = {
    "track_a": "Upper Body Kinetic Thickness / Push-Pull",
    "track_b": "Lower Body Athletic Base / Core Apex",
    "track_c": "Active Mobility / Functional Conditioning Recovery Station",
    "recovery": "Full Recovery System Rest Arc",
}

TRACK_BY_WEEKDAY = {
    0: "track_a",
    1: "track_b",
    2: "track_c",
    3: "track_a",
    4: "track_b",
    5: "track_c",
    6: "recovery",
}


# --- Master Training Templates Database ---
CHARACTER_TEMPLATES = {
    "toji": {
        "physique": {
            "track_a": ["Weighted Pull-Ups", "Incline Dumbbell Bench Press", "Cable Rows", "Lateral Raises"],
            "track_b": ["Barbell Romanian Deadlifts", "Bulgarian Split Squats", "Hanging Leg Raises", "Farmer's Walks"],
            "track_c": ["Kettlebell Swings", "Medicine Ball Rotational Slams", "Agility Ladder Chains", "Loaded Carries"],
            "recovery": ["Breath-Controlled Walk", "Hip Mobility Flow", "Thoracic Spine Openers", "Deep Core Bracing"],
        },
        "train-like": {
            "track_a": ["Heavy Pull-Ups", "Explosive Push-Ups", "Landmine Press", "Towel Grip Rows"],
            "track_b": ["Heavy Barbell Deadlifts", "Plyometric Box Jumps", "Farmer's Walks", "Hanging Knee Raises"],
            "track_c": ["Medicine Ball Rotational Slams", "Kettlebell Swings", "Shuttle Runs", "Animal Flow Crawls"],
            "recovery": ["Joint Prep Flow", "Zone 2 Walk", "Grip Flush Carries", "Breathing Reset Holds"],
        },
    },
    "itadori": {
        "physique": {
            "track_a": ["Weighted Dips", "Barbell Bent Over Rows", "Hammer Curls", "Push-Up Volume Sets"],
            "track_b": ["Barbell Back Squats", "Walking Lunges", "Ab Wheel Rollouts", "Calf Raises"],
            "track_c": ["Burpee Pull-Ups", "Jump Rope Intervals", "Medicine Ball Throws", "Plank Shoulder Taps"],
            "recovery": ["Low-Impact Cardio", "Hip Flexor Mobility", "Shoulder CARs", "Box Breathing"],
        },
        "train-like": {
            "track_a": ["Power Push-Ups", "Sandbag Bear-Hug Carries", "Explosive Rows", "Medicine Ball Chest Passes"],
            "track_b": ["Power Cleans", "Plyometric Knee-to-Chest Jumps", "Heavy Sandbag Carries", "Core Impact Holds"],
            "track_c": ["Medicine Ball Underhand Throws", "Burpee Pull-Ups", "Sprint Starts", "Reaction Footwork"],
            "recovery": ["Shadowboxing Flow", "Easy Bike Intervals", "Spinal Decompression", "Breathing Cadence Work"],
        },
    },
    "maki": {
        "physique": {
            "track_a": ["Lat Pulldowns", "Overhead Dumbbell Press", "Single-Arm Cable Rows", "Rear Delt Flyes"],
            "track_b": ["Dumbbell Romanian Deadlifts", "Bulgarian Split Squats", "Plank Variations", "Step-Ups"],
            "track_c": ["Jump Rope Double Unders", "Agility Ladder Fast-Footwork Chains", "Kettlebell Halos", "Bear Crawls"],
            "recovery": ["Weapon-Range Shoulder Flow", "Hamstring Mobility", "Core Breathing Holds", "Easy Walk"],
        },
        "train-like": {
            "track_a": ["Kettlebell Snatches", "Towel Pull-Ups", "Landmine Press", "Grip Crush Carries"],
            "track_b": ["Barbell Landmine Rotations", "Lateral Lunges", "Copenhagen Planks", "Single-Leg RDLs"],
            "track_c": ["Agility Ladder Fast-Footwork Chains", "Jump Rope Double Unders", "Shuttle Cuts", "Kettlebell Windmills"],
            "recovery": ["Joint Mobility Circuit", "Light Technical Footwork", "Wrist Conditioning", "Nasal Breathing Walk"],
        },
    },
    "tanjiro": {
        "physique": {
            "track_a": ["Barbell Rows", "Overhead Press", "Incline Push-Ups", "Face Pulls"],
            "track_b": ["Front Squats", "Calf Raises", "Ab Wheel Rollouts", "Split Squats"],
            "track_c": ["Dumbbell Thrusters", "Sprint Intervals (400m)", "Plank-to-Pushups", "Kettlebell Slashes"],
            "recovery": ["Total Concentration Breathing Walk", "Ankle Mobility", "Thoracic Rotations", "Easy Cycling"],
        },
        "train-like": {
            "track_a": ["Breath-Control Push-Ups", "Barbell Rows", "Dumbbell Thrusters", "Band Pull-Aparts"],
            "track_b": ["Front Squats", "Walking Lunges", "Rotational Core Chops", "Calf Spring Sets"],
            "track_c": ["High-Intensity Kettlebell Slashes", "Sprint Intervals (400m)", "Burpees", "Footwork Ladder Drills"],
            "recovery": ["Breathing Cadence Flow", "Long Walk", "Hip Mobility", "Low-Intensity Core Holds"],
        },
    },
    "tengen": {
        "physique": {
            "track_a": ["Dumbbell Lateral Raises (High Volume)", "Incline Barbell Bench Press", "Barbell Bicep Curls", "Cable Flyes"],
            "track_b": ["Dumbbell Shrugs", "Goblet Squats", "Weighted Sit-Ups", "Farmer's Walks"],
            "track_c": ["Assault Bike Sprints", "Sledgehammer Tire Slams", "Renegade Rows", "Jump Rope Tempo Sets"],
            "recovery": ["Shoulder Flush Circuit", "Easy Bike Ride", "Forearm Mobility", "Box Breathing"],
        },
        "train-like": {
            "track_a": ["Explosive Push-Ups (Clapping)", "Dumbbell Renegade Rows", "Kettlebell Push Press", "Heavy Rope Pulls"],
            "track_b": ["Heavy Farmer's Walks", "Trap Bar Deadlifts", "Hanging Knee Raises", "Lateral Bounds"],
            "track_c": ["Sledgehammer Tire Slams", "Assault Bike Sprints", "Battle Rope Waves", "Cone Cut Drills"],
            "recovery": ["Grip Recovery Flow", "Mobility Walk", "Upper Back Release", "Nasal Breathing Reset"],
        },
    },
    "inosuke": {
        "physique": {
            "track_a": ["Pull-Ups (Wide Grip)", "Decline Dumbbell Bench Press", "Cable Rows", "Hindu Push-Ups"],
            "track_b": ["Walking Lunges", "Hanging Toes-to-Bar", "Russian Twists", "Deep Cossack Squats"],
            "track_c": ["Bear Crawls (Timed)", "Kettlebell Windmills", "Burpee Broad Jumps", "Animal Flow Transitions"],
            "recovery": ["Deep Mobility Flow", "Easy Trail Walk", "Spinal Wave Drills", "Breathing Holds"],
        },
        "train-like": {
            "track_a": ["Hindu Push-Ups", "Wide-Grip Pull-Ups", "Crawl-to-Push Combos", "Primal Rows"],
            "track_b": ["Deep Cossack Squats", "Kettlebell Windmills", "Walking Lunges", "Core Twist Holds"],
            "track_c": ["Bear Crawls (Timed)", "Burpee Broad Jumps", "Quadruped Flow", "Shuttle Crawls"],
            "recovery": ["Animal Mobility Reset", "Joint Circles", "Low Heart-Rate Walk", "Diaphragm Breathing"],
        },
    },
    "deku": {
        "physique": {
            "track_a": ["Overhead Barbell Press", "Push-Ups (Weighted)", "Dumbbell Shrugs", "Cable Rows"],
            "track_b": ["Barbell Back Squats", "Hamstring Curls", "Jump Squats", "Hanging Leg Raises"],
            "track_c": ["Depth Jumps to Explosive Bounds", "Clapping Push-Ups", "Heavy Sled Pushes", "Medicine Ball Slams"],
            "recovery": ["Joint Impact Prep", "Easy Bike", "Ankle-Knee-Hip Mobility", "Breathing Control"],
        },
        "train-like": {
            "track_a": ["Clapping Push-Ups", "Power Cleans", "Explosive Pulls", "Overhead Carries"],
            "track_b": ["Depth Jumps to Explosive Bounds", "Heavy Sled Pushes", "Jump Squats", "Core Bracing Carries"],
            "track_c": ["Reactive Bounds", "Medicine Ball Slams", "Agility Deceleration Drills", "Sprint Mechanics"],
            "recovery": ["Impact Recovery Flow", "Zone 2 Bike", "Soft Tissue Mobility", "Controlled Breath Work"],
        },
    },
    "bakugo": {
        "physique": {
            "track_a": ["Close-Grip Bench Press", "Weighted Pull-Ups", "Dumbbell Overhead Extensions", "Cable Rows"],
            "track_b": ["Box Drills (Lateral Bounds)", "Plank Jacks", "Goblet Squats", "Barbell Wrist Curls"],
            "track_c": ["Battle Rope Slams (Fast Tempo)", "Medicine Ball Chest Passes", "Kettlebell Push Presses", "Lateral Bounds"],
            "recovery": ["Forearm Tendon Care", "Shoulder Mobility", "Easy Row Erg", "Breathing Reset"],
        },
        "train-like": {
            "track_a": ["Medicine Ball Chest Passes", "Battle Rope Slams (Fast Tempo)", "Kettlebell Push Presses", "Explosive Dips"],
            "track_b": ["Box Drills (Lateral Bounds)", "Plank Jacks", "Loaded Step-Ups", "Rotational Core Throws"],
            "track_c": ["Rapid Direction-Shift Drills", "Assault Bike Bursts", "Battle Rope Alternating Waves", "Sprint Deceleration"],
            "recovery": ["Wrist Mobility Flow", "Low-Intensity Cardio", "Scapular Control", "Nasal Breathing"],
        },
    },
    "all-might": {
        "physique": {
            "track_a": ["Barbell Bench Press (Heavy)", "Seated Barbell Overhead Press", "Barbell Curls", "Heavy Cable Rows"],
            "track_b": ["Barbell Back Squats (Heavy)", "Barbell Deadlifts (Heavy)", "Farmer's Carries", "Weighted Sit-Ups"],
            "track_c": ["Medicine Ball Overhead Slams", "Heavy Sled Drags", "Log Clean Technique", "Loaded Carries"],
            "recovery": ["Golden-Era Mobility Flow", "Long Walk", "Shoulder Care", "Breathing Reset"],
        },
        "train-like": {
            "track_a": ["Heavy Log Clean and Press", "Barbell Bench Press (Heavy)", "Rack Lockouts", "Weighted Pull-Ups"],
            "track_b": ["Rack Pulls (Above Knee)", "Heavy Sled Drags", "Farmer's Carries (Max Weight)", "Core Bracing Holds"],
            "track_c": ["Medicine Ball Overhead Slams", "Heavy Sled Pushes", "Power Step-Ups", "Conditioning Carries"],
            "recovery": ["Full Recovery System Walk", "Loaded Stretching", "Breath-Control Reset", "Joint Prep Circuit"],
        },
    },
}


def resolve_character_key(profile_data):
    selected_character = profile_data.get("selectedCharacter", "").lower()
    character_aliases = {
        "yuji": "itadori",
        "itadori": "itadori",
        "toji": "toji",
        "maki": "maki",
        "tanjiro": "tanjiro",
        "tengen": "tengen",
        "inosuke": "inosuke",
        "izuku": "deku",
        "deku": "deku",
        "bakugo": "bakugo",
        "katsuki": "bakugo",
        "all": "all-might",
        "all-might": "all-might",
    }

    first_token = selected_character.split(" ")[0] if selected_character else ""
    return character_aliases.get(first_token, "toji")


def build_routine_items(exercises, strategy, weight, height, medical_history):
    calculated_routines = []

    for exercise in exercises:
        if strategy == "physique":
            sets = 4 if weight >= 75 else 3
            reps = "8 to 12 reps"
            intensity = "Focus on a 3-second negative eccentric tempo for maximal mechanical hypertrophy damage."
        else:
            sets = 5 if height >= 180 else 4
            reps = "5 explosive reps" if any(keyword in exercise.lower() for keyword in ["deadlift", "clean", "pull"]) else "45 seconds max effort"
            intensity = "Execute with maximal concentric velocity. Rest fully between sets to prevent neural fatigue."

        calculated_routines.append({
            "name": exercise,
            "sets": sets,
            "reps": reps,
            "coaching_cue": intensity,
        })

    final_filtered_routines = []
    knee_injury_keywords = ["knee", "acl", "meniscus", "patella"]
    back_injury_keywords = ["back", "spine", "lumbar", "lumber", "herniated", "slip disc"]

    for item in calculated_routines:
        ex_name = item["name"]

        if any(keyword in medical_history for keyword in knee_injury_keywords):
            if any(unsafe in ex_name.lower() for unsafe in ["squat", "box jump", "depth jump", "sled", "lunge", "bound"]):
                item["name"] = "Isolated Leg Extensions (Slow Tempo)"
                item["reps"] = "15 controlled reps"
                item["coaching_cue"] = "SAFETY ALTERNATIVE: Replaced explosive lower body knee flexion with an open-chain static isolation to protect your joint injury configuration."

        if any(keyword in medical_history for keyword in back_injury_keywords):
            if any(unsafe in ex_name.lower() for unsafe in ["deadlift", "squat", "row", "clean", "pull"]):
                item["name"] = "Chest-Supported Dumbbell Rows or Glute Bridges"
                item["reps"] = "12 to 15 reps"
                item["coaching_cue"] = "SAFETY ALTERNATIVE: Compounding load removed from the lumbar spine column. Axial skeleton loading avoided to shield your lower back injury."

        final_filtered_routines.append(item)

    return final_filtered_routines


def generate_custom_routine(profile_data):
    """
    Takes a user profile data dictionary and calculates a personalized,
    biologically scaled, safety-filtered Shonen training program.
    """
    char_key = resolve_character_key(profile_data)
    strategy = profile_data.get("strategyGoal", "physique").lower()
    if strategy not in ("physique", "train-like"):
        strategy = "physique"

    weight = float(profile_data.get("weight", 70))
    height = float(profile_data.get("height", 175))
    medical_history = profile_data.get("medicalHistory", "").lower()

    current_day = datetime.now().weekday()
    track_key = TRACK_BY_WEEKDAY.get(current_day, "recovery")
    selected_template = CHARACTER_TEMPLATES.get(char_key, CHARACTER_TEMPLATES["toji"])[strategy]
    exercises = selected_template[track_key]

    final_filtered_routines = build_routine_items(
        exercises, strategy, weight, height, medical_history
    )

    return {
        "character_alignment": char_key.upper(),
        "strategy_paradigm": strategy.upper(),
        "core_focus_directive": TRACK_FOCUS[track_key],
        "daily_track": track_key,
        "weekday_index": current_day,
        "assigned_workout_routine": final_filtered_routines,
    }


if __name__ == "__main__":
    test_user_profile = {
        "selectedUniverse": "jjk",
        "selectedCharacter": "Toji Fushiguro",
        "strategyGoal": "train-like",
        "weight": 82,
        "height": 185,
        "medicalHistory": "I have chronic lower back pain and a mild slip disc issue.",
    }

    result = generate_custom_routine(test_user_profile)
    print(f"--- PROTOCOL INITIALIZATION FOR USER TARGET: {result['character_alignment']} ({result['strategy_paradigm']}) ---")
    print(f"Directive Focus: {result['core_focus_directive']}\n")
    for index, ex in enumerate(result["assigned_workout_routine"], start=1):
        print(f"{index}. {ex['name']} -> {ex['sets']} sets x {ex['reps']}")
        print(f"   Cue: {ex['coaching_cue']}")
