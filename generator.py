from datetime import datetime
import re


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


STRUCTURAL_REPLACEMENTS = {
    "bench": "Incline Dumbbell Bench Press",
    "press": "Machine Chest Press",
    "pull": "Lat Pulldowns (Adjustable Load)",
    "row": "Chest-Supported Cable Rows",
    "squat": "Leg Presses",
    "deadlift": "Hip Thrusts",
    "lunge": "Step-Ups",
    "jump": "Low-Impact Step-Ups",
    "sled": "Incline Treadmill March",
    "curl": "Cable Hammer Curls",
    "carry": "Suitcase Carries",
    "core": "Dead Bug Core Holds",
}

MUSCLE_FINISHERS = {
    "arms": "Barbell Spider Curls super-setted with Tricep Pushdowns",
    "chest": "Cable Flyes super-setted with Machine Chest Press",
    "legs": "Leg Extensions super-setted with Seated Hamstring Curls",
    "back": "Straight-Arm Pulldowns super-setted with Chest-Supported Rows",
    "shoulders": "Cable Lateral Raises super-setted with Rear Delt Flyes",
}

COMPOUND_KEYWORDS = [
    "squat", "deadlift", "pull-up", "pull-ups", "bench", "press", "row", "clean",
    "sled", "lunge", "carry", "carries", "thruster", "dip", "dips",
]

AXIAL_LOADING_KEYWORDS = [
    "barbell back squat", "front squat", "squat", "deadlift", "power clean",
    "heavy log clean", "rack pull", "overhead press", "sled", "jump", "bound",
]

DYNAMIC_CUE_RULES = [
    (
        ["slam", "slams", "sledgehammer", "battle rope", "rope", "sprint", "burpee", "shuttle", "assault bike"],
        "Attack each rep explosively, then reset your breathing before fatigue turns power into sloppy motion.",
    ),
    (
        ["curl", "curls", "extension", "pushdown", "tricep", "bicep", "forearm"],
        "Lock the elbows in place, squeeze the target muscle hard, and avoid swinging momentum through the rep.",
    ),
    (
        ["carry", "carries", "walk", "farmer", "suitcase", "sandbag", "sled"],
        "Brace the ribs down, keep posture tall, and move with controlled steps so the core—not momentum—owns the load.",
    ),
    (
        ["squat", "squats", "lunge", "lunges", "step-up", "step ups", "split squat", "leg press"],
        "Root your feet into the floor, track knees over toes, and keep tension through the hips on every rep.",
    ),
    (
        ["press", "push-up", "push ups", "push-ups", "dip", "dips", "bench", "thruster"],
        "Stack wrists over elbows, brace before pressing, and drive the weight with a powerful but controlled lockout.",
    ),
    (
        ["row", "rows", "pull-up", "pull-ups", "pulldown", "pull", "face pull"],
        "Lead with the elbows, pull the shoulder blades down and back, and pause briefly at peak contraction.",
    ),
    (
        ["deadlift", "rdl", "romanian", "hinge", "swing", "swings", "clean"],
        "Hinge from the hips, keep the spine locked neutral, and finish with glutes instead of yanking through the low back.",
    ),
    (
        ["plank", "core", "ab wheel", "sit-up", "leg raise", "knee raise", "chop", "twist", "bracing"],
        "Exhale into a hard brace, keep the pelvis controlled, and resist rotation instead of rushing the movement.",
    ),
    (
        ["jump", "jumps", "bound", "bounds", "ladder", "agility", "footwork", "cut", "deceleration"],
        "Land softly, stay springy through the ankles, and prioritize crisp direction changes over reckless speed.",
    ),
    (
        ["mobility", "flow", "breathing", "walk", "easy", "recovery", "reset", "stretching", "openers"],
        "Keep the pace restorative, breathe through the nose, and chase better range of motion without forcing pain.",
    ),
]


def parse_float(value, fallback):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def parse_int(value, fallback):
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def is_compound_exercise(exercise):
    lower_name = exercise.lower()
    return any(keyword in lower_name for keyword in COMPOUND_KEYWORDS)


def find_structural_replacement(exercise):
    lower_name = exercise.lower()
    for keyword, replacement in STRUCTURAL_REPLACEMENTS.items():
        if keyword in lower_name:
            return replacement
    return "Cable Machine Pattern Replacement"


def replace_heavy_bodyweight_movements(exercises, weight):
    if weight <= 90:
        return list(exercises)

    guarded_exercises = []
    for exercise in exercises:
        lower_name = exercise.lower()
        if "weighted pull-up" in lower_name or "weighted pull-ups" in lower_name:
            guarded_exercises.append("Lat Pulldowns (Adjustable Load)")
        elif "heavy pull-up" in lower_name or "pull-ups" in lower_name:
            guarded_exercises.append("Assisted Banded Pull-Ups")
        else:
            guarded_exercises.append(exercise)
    return guarded_exercises


def extract_preference_phrases(workout_preferences):
    preference_text = workout_preferences.lower()
    exclusions = []
    inclusions = []

    exclusion_patterns = [
        r"\bno\s+([a-z0-9 \-/]+)",
        r"\bremove\s+([a-z0-9 \-/]+)",
        r"\bdon't want\s+([a-z0-9 \-/]+)",
        r"\bwithout\s+([a-z0-9 \-/]+)",
    ]
    inclusion_patterns = [
        r"\binclude\s+([a-z0-9 \-/]+)",
        r"\badd\s+([a-z0-9 \-/]+)",
        r"\bwant\s+([a-z0-9 \-/]+)",
    ]

    for pattern in exclusion_patterns:
        exclusions.extend(match.strip() for match in re.findall(pattern, preference_text))

    for pattern in inclusion_patterns:
        inclusions.extend(match.strip() for match in re.findall(pattern, preference_text))

    return exclusions, inclusions


def phrase_matches_exercise(phrase, exercise):
    phrase_tokens = [token for token in re.split(r"[^a-z0-9]+", phrase.lower()) if len(token) > 2]
    exercise_lower = exercise.lower()
    return bool(phrase_tokens) and any(token in exercise_lower for token in phrase_tokens)


def clean_preferred_exercise_name(phrase):
    cleaned = re.split(r"\b(?:and|but|with|for|please|thanks)\b", phrase, maxsplit=1)[0]
    cleaned = re.sub(r"[^a-z0-9 \-/]", "", cleaned).strip()
    return cleaned.title() if cleaned else ""


def apply_preference_rules(exercises, workout_preferences):
    exclusions, inclusions = extract_preference_phrases(workout_preferences)
    adjusted_exercises = []

    for exercise in exercises:
        if any(phrase_matches_exercise(phrase, exercise) for phrase in exclusions):
            adjusted_exercises.append(find_structural_replacement(exercise))
        else:
            adjusted_exercises.append(exercise)

    for inclusion in inclusions:
        preferred_exercise = clean_preferred_exercise_name(inclusion)
        if not preferred_exercise:
            continue

        replaced = False
        for index, exercise in enumerate(adjusted_exercises):
            if (
                any(keyword in preferred_exercise.lower() for keyword in ["bench", "press", "chest"])
                and any(keyword in exercise.lower() for keyword in ["press", "push", "bench", "fly"])
            ):
                adjusted_exercises[index] = preferred_exercise
                replaced = True
                break
            if (
                any(keyword in preferred_exercise.lower() for keyword in ["row", "pull", "pulldown", "back"])
                and any(keyword in exercise.lower() for keyword in ["row", "pull", "pulldown"])
            ):
                adjusted_exercises[index] = preferred_exercise
                replaced = True
                break
            if (
                any(keyword in preferred_exercise.lower() for keyword in ["squat", "leg", "lunge"])
                and any(keyword in exercise.lower() for keyword in ["squat", "leg", "lunge", "step"])
            ):
                adjusted_exercises[index] = preferred_exercise
                replaced = True
                break

        if not replaced:
            adjusted_exercises.append(preferred_exercise)

    return adjusted_exercises


def find_muscle_focus_finishers(workout_preferences):
    preference_text = workout_preferences.lower()
    finishers = []

    for keyword, finisher in MUSCLE_FINISHERS.items():
        if keyword in preference_text:
            finishers.append(finisher)

    return finishers


def apply_medical_safety(exercise, medical_conditions):
    lower_name = exercise.lower()
    medical_text = medical_conditions.lower()
    injury_keywords = ["knee", "back", "injury", "spine", "acl", "meniscus", "herniated", "slip disc"]

    if not any(keyword in medical_text for keyword in injury_keywords):
        return exercise, False

    if any(keyword in lower_name for keyword in AXIAL_LOADING_KEYWORDS):
        if any(keyword in medical_text for keyword in ["knee", "acl", "meniscus"]):
            return "Leg Presses (Injury Modification Applied)", True
        if any(keyword in medical_text for keyword in ["back", "spine", "herniated", "slip disc", "injury"]):
            return "Box Squats (Injury Modification Applied)", True

    return exercise, False


def get_dynamic_coaching_cue(exercise_name, strategy):
    lower_name = exercise_name.lower()

    for keywords, cue in DYNAMIC_CUE_RULES:
        if any(keyword in lower_name for keyword in keywords):
            return cue

    if strategy == "physique":
        return "Control the eccentric, own the peak contraction, and keep every rep inside clean hypertrophy mechanics."

    return "Move with decisive intent, maintain technical shape under fatigue, and stop before speed breaks form."


def build_routine_items(exercises, strategy, age, weight, height, medical_conditions, workout_preferences):
    calculated_routines = []

    for exercise in exercises:
        safe_exercise, injury_modified = apply_medical_safety(exercise, medical_conditions)

        if strategy == "physique":
            sets = 4 if weight >= 75 else 3
            reps = "8 to 12 reps"
        else:
            sets = 5 if height >= 180 else 4
            reps = "5 explosive reps" if any(keyword in safe_exercise.lower() for keyword in ["deadlift", "clean", "pull"]) else "45 seconds max effort"

        intensity = get_dynamic_coaching_cue(safe_exercise, strategy)

        if age > 40 and is_compound_exercise(safe_exercise):
            sets = 3
            intensity += " Recovery Tip: Volume reduced for structural recovery and joint resilience."

        if injury_modified:
            intensity += " Injury Modification Applied: keep range pain-free and prioritize stable control over load."

        calculated_routines.append({
            "name": safe_exercise,
            "sets": sets,
            "reps": reps,
            "coaching_cue": intensity,
        })

    for finisher in find_muscle_focus_finishers(workout_preferences):
        calculated_routines.append({
            "name": finisher,
            "sets": 3,
            "reps": "12 reps",
            "coaching_cue": f"Preference Finisher: Added to match your requested muscle-group focus. {get_dynamic_coaching_cue(finisher, strategy)}",
        })

    return calculated_routines


def generate_custom_routine(profile_data):
    """
    Takes a user profile data dictionary and calculates a personalized,
    biologically scaled, safety-filtered Shonen training program.
    """
    char_key = resolve_character_key(profile_data)
    strategy = profile_data.get("strategyGoal", "physique").lower()
    if strategy not in ("physique", "train-like"):
        strategy = "physique"

    age = parse_int(profile_data.get("age"), 25)
    weight = parse_float(profile_data.get("weight"), 70)
    height = parse_float(profile_data.get("height"), 175)
    medical_conditions = (
        profile_data.get("medical_conditions")
        or profile_data.get("medicalHistory")
        or ""
    )
    workout_preferences = (
        profile_data.get("workout_preferences")
        or profile_data.get("specialPreferences")
        or ""
    )

    current_day = datetime.now().weekday()
    track_key = TRACK_BY_WEEKDAY.get(current_day, "recovery")
    selected_template = CHARACTER_TEMPLATES.get(char_key, CHARACTER_TEMPLATES["toji"])[strategy]
    exercises = replace_heavy_bodyweight_movements(selected_template[track_key], weight)
    exercises = apply_preference_rules(exercises, workout_preferences)

    final_filtered_routines = build_routine_items(
        exercises, strategy, age, weight, height, medical_conditions, workout_preferences
    )
    
    # ⚡ HOOK INTERCEPT: Fetch current ACWR status from progression engine
    from progression import calculate_fatigue_status
    user_id = profile_data.get("user_id") or profile_data.get("id")
    
    if user_id:
        fatigue_data = calculate_fatigue_status(user_id)
        status = fatigue_data.get("status", "OPTIMAL")
        
        # Scale the routine parameters if neural strain is elevated
        if status in ["HIGH_FATIGUE", "DANGER_ZONE"]:
            for ex in final_filtered_routines:
                # Deload target rep numbers dynamically
                if "8 to 12" in ex["reps"]:
                    ex["reps"] = "6 to 8 deload reps"
                elif "12 reps" in ex["reps"]:
                    ex["reps"] = "8 reps"
                elif "5 explosive" in ex["reps"]:
                    ex["reps"] = "3 controlled reps"
                
                # Drop target working sets by 1 to manage training volume
                if ex["sets"] > 2:
                    ex["sets"] -= 1
                    
                # Inject recovery coaching modifiers to the cues
                ex["coaching_cue"] += " [FATIGUE DELOAD ACTIVE: Focus strictly on form over load]"

    focus_directive = TRACK_FOCUS[track_key]
    if age > 40:
        focus_directive += " | Recovery Tip: reduced compound volume for structural recovery."

    return {
        "character_alignment": char_key.upper(),
        "strategy_paradigm": strategy.upper(),
        "core_focus_directive": focus_directive,
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
