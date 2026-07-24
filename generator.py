from datetime import datetime
import re


TRACK_FOCUS = {
    "track_a": "Upper Body Width & Lat Expansion",
    "track_b": "Armor-Plate Chest Density & Triceps",
    "track_c": "Lower Body & Shredded Core Apex",
    "track_d": "Back Thickness, Traps & Biceps",
    "track_e": "Deltoid Hypertrophy & Abdominal Detail",
    "track_f": "Full-Body Combat Circuit & Anaerobic Conditioning",
    "recovery": "Full Recovery System Rest Arc"
}

TRACK_BY_WEEKDAY = {
    0: "track_a",
    1: "track_b",
    2: "track_c",
    3: "track_d",
    4: "track_d",
    5: "track_e",
    6: "recovery",
}


# --- Master Training Templates Database ---
CHARACTER_TEMPLATES = {
    "toji": { 
        "physique": {
            "track_a": [
                "HEAVENLY V-TAPER: Weighted Wide-Grip Pull-Ups (4 sets x 6-8 reps | 2 min rest)",
                "Neutral Grip Lat Pulldown (3 sets x 10-12 reps | Flare Lats)",
                "Dumbbell Lateral Raises (5 sets x 12-15 reps | 60s Rest)",
                "Behind-the-Back Cable Lateral Raises (3 sets x 15 reps per side)",
                "Incline Dumbbell Press (4 sets x 8-10 reps | Upper Chest Base)"
            ],
            "track_b": [
                "ARMOR-PLATE PECS: Incline Smith Machine Press (4 sets x 8-10 reps)",
                "Flat Barbell Bench Press or Heavy DB Press (3 sets x 8-10 reps)",
                "High-to-Low Cable Pec Flyes (4 sets x 12-15 reps | Sharp Pec Line)",
                "Weighted Dips (3 sets x 8-10 reps | Lower Chest & Triceps)",
                "Overhead Tricep Cable Extensions - Rope (4 sets x 12-15 reps)"
            ],
            "track_c": [
                "SHREDDED MIDSECTION: Barbell Back Squats or Hack Squats (4x8-10)",
                "Romanian Deadlifts - RDLs (3 sets x 10 reps | Hamstring Sweep)",
                "Walking Dumbbell Lunges (3 sets x 12 steps per leg)",
                "Hanging Leg Raises (4 sets x 12-15 reps | Controlled Descent)",
                "Ab Wheel Rollouts (3 sets x 10-12 reps)"
            ],
            "track_d": [
                "BACK DENSITY & TRAPS: Overhand Barbell Rows (4 sets x 8-10 reps)",
                "Chest-Supported T-Bar Rows (3 sets x 10-12 reps | Mid-Back Squeeze)",
                "Heavy Dumbbell Shrugs (4 sets x 12 reps | 2s Top Hold)",
                "Barbell Bicep Curls (4 sets x 10 reps)",
                "Incline Dumbbell Hammer Curls (3 sets x 12 reps | Brachialis Width)"
            ],
            "track_e": [
                "SUPERSET: Seated DB Shoulder Press (4x8-10) + DB Lateral Raises (4x15)",
                "Reverse Pec Deck Rear Delt Flyes (4 sets x 15 reps)",
                "Face Pulls (3 sets x 15-20 reps)",
                "High-to-Low Cable Woodchoppers (3 sets x 15 per side | Serratus Detail)",
                "Decline Bench Crunches with Twist (3 sets x 15-20 reps)"
            ],
            "recovery": [
                "HEAVENLY RESTORATION: Full Upper Body & Shoulder Girdle Decompression (20 min)",
                "Deep Thoracic Spine, Lat, & Hip Flexor Mobility Session"
            ]
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
            "track_a": [
                "Barbell Back Squats (4 sets x 8-10 reps | Deep ROM)",
                "Leg Press - Low Foot Placement (3 sets x 10-12 reps | Quad Teardrop)",
                "Walking Dumbbell Lunges (3 sets x 12 steps per leg)",
                "Standing Calf Raises (4 sets x 15-20 reps | 1s Hold)",
                "Hanging Leg Raises (4 sets x 12-15 reps)"
            ],
            "track_b": [
                "Incline Dumbbell Press (4 sets x 8-10 reps | Upper Chest Fill)",
                "Standing Dumbbell Shoulder Press (3 sets x 8-10 reps)",
                "Cable Pec Flyes (3 sets x 12-15 reps | Squeeze Center)",
                "Dumbbell Lateral Raises (4 sets x 15 reps | Strict Control)",
                "Ab Wheel Rollouts (3 sets x 10-12 reps | Core Bracing)"
            ],
            "track_c": [
                "Weighted Pull-Ups (4 sets x 6-8 reps | V-Taper Lats)",
                "Barbell or T-Bar Rows (3 sets x 8-10 reps | Mid-Back Thickness)",
                "Neutral Grip Lat Pulldowns (3 sets x 12 reps)",
                "Incline Dumbbell Curls (3 sets x 10-12 reps)",
                "High-to-Low Cable Woodchoppers (3 sets x 15 per side | Serratus Focus)"
            ],
            "track_d": [
    "POSTERIOR CHAIN & LEGS: Romanian Deadlifts - RDLs (4 sets x 8-10 reps | Hamstring Stretch)",
    "Bulgarian Split Squats (3 sets x 10 reps per leg | Unilateral Balance)",
    "Lying Leg Curls (3 sets x 12-15 reps)",
    "Seated Calf Raises (4 sets x 15 reps)",
    "Weighted Decline Bench Crunches (3 sets x 15 reps)"
], 
            "track_e": [
                "SUPERSET: Barbell Bicep Curls (4x10) + EZ-Bar Skull Crushers (4x10)",
                "Cable Lateral Raises (4 sets x 15 reps | Capped Delts)",
                "Incline Hammer Curls (3 sets x 12 reps)",
                "Tricep Rope Pushdowns (3 sets x 12-15 reps)",
                "Hanging Knee Raises with Twist (4 sets x 15 reps | Lower Abs)"
            ],
            "recovery": [
                "ITADORI ATHLETIC FLOW: Deep Hip Flexor & Glute Opening (20 min)",
                "Full-Body Hamstring, T-Spine, & Ankle Mobility Session"
            ]
        },
        "train-like": {
            "track_a": [ # Day 0 - Monday
                "BLACK FLASH POWER: Power Cleans or Trap Bar Jump Shrugs (4x3-5)",
                "Med Ball Rotational Wall Slams (4 sets x 6 reps per side)",
                "Landmine Punch Presses (4 sets x 6 reps per arm | Punching Drive)",
                "Weighted Pull-Ups (4 sets x 5 reps | Recoil Absorbing)",
                "Pallof Press Hold (3 sets x 30s per side | Anti-Rotation)"
            ],
            "track_b": [ # Day 1 - Tuesday
                "SPEED & LEAPING: Max Effort 30m Sprints (5-6 rounds | 2 min rest)",
                "Depth Jumps to Vertical Jump (4 sets x 4 reps | Explosive)",
                "Broad Jumps for Distance (3 sets x 5 max-distance jumps)",
                "Single-Leg Box Jumps (3 sets x 5 reps per leg | Unilateral)",
                "Med Ball Overhead Backward Throws (4 sets x 5 reps)"
            ],
            "track_c": [ # Day 2 - Wednesday
                "MARTIAL FLOW: Shadowboxing & Level Change Footwork (15 min)",
                "Heavy Bag Striking Intervals (5 rounds x 3 min | Combos)",
                "Flying / Clinch Knee Strikes on Bag (4 sets x 10 reps per leg)",
                "Head Movement & Slip-Bag Reflex Drills (10 min)"
            ],
            "track_d": [ # Day 3 - Thursday (REST DAY RESTORATION)
                "ITADORI ATHLETIC MOBILITY: Deep Hip & Ankle Flow (20-30 min)",
                "Thoracic Spine, Hamstrings, & Hip Flexor Opening Protocol"
            ],
            "track_e": [ # Day 4 - Friday 
                "JOINT ARMOR: Barbell Front Squats (4 sets x 5 reps | Quad Power)",
                "Explosive Bulgarian Split Squats (3 sets x 6 reps per leg)",
                "Romanian Deadlifts - RDLs (4 sets x 8 reps | Posterior Chain)",
                "Heavy Farmer's Walks (4 rounds x 30m | Grip & Stability)",
                "Tibialis & Calf Raises (3 sets x 15 reps | Knee Bulletproofing)"
            ],
            "track_f": [ # Day 5 - Saturday
                "CURSE ENERGY CIRCUIT: 4 Rounds Fast (90s Rest between rounds)",
                "10 Kettlebell Cleans to Press + 15 Plyo Clapping Push-Ups",
                "10 Heavy Med Ball Slams + 12 Box Jumps + 100m Sprint"
            ],
            "recovery": [ # Day 6 - Sunday
                "Full Recovery System Rest Arc & CNS Reset",
                "Deep Muscle Tissue Decompression Flow"
            ]
        } 
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
            "track_a": [
                "Deadlifts (3 sets x 5 reps | Raw Power)",
                "Weighted Pull-Ups (4 sets x 6-8 reps)",
                "Towel Pull-Ups (3 sets x AMRAP | Grip Focus)",
                "Behind-Back Barbell Wrist Curls (4 sets x 15 reps)",
                "Plate Pinches (3 sets x Max Time Hold)"
            ],
            "track_b": [
                "Barbell Front or Goblet Squats (4 sets x 10-12 reps)",
                "Walking Lunges (3 sets x 20 steps total)",
                "Standing Calf Raises (5 sets x 20-25 reps | 2s Hold)",
                "Jump Squats (3 sets x 15 reps | Explosive Leg Power)"
            ],
            "track_c": [
                "Weighted Push-Ups (4 sets x 10-12 reps)",
                "Overhead Dumbbell Press (3 sets x 8-10 reps)",
                "Dip Station Dips (3 sets x 10-12 reps)",
                "Hanging Leg Raises (4 sets x 12-15 reps | Controlled)",
                "Ab Wheel Rollouts (3 sets x 10 reps)"
            ],
            "track_d": [
                "SHRED CIRCUIT: 4 Rounds (Rest 60s between rounds)",
                "Pull-Ups (10 reps) + Clapping Push-Ups (12 reps)",
                "Fast Bodyweight Squats (20 reps) + Knee Tucks (15 reps)",
                "Burpees Finisher (10 reps)"
            ],
            "track_e": [
                "CHARCOAL CARRIER: Heavy Farmer's Walks (4 rounds x 50m)",
                "Zercher Carries - Sandbag or Barbell (3 rounds x 30m)",
                "Weighted Russian Twists (3 sets x 20 reps per side)",
                "Plank with Protraction (3 sets x 60s Hold | Serratus Focus)"
            ],
            "recovery": [
                "Deep Lower Body Stretching (Hamstrings, Hip Flexors, Calves)",
                "Thoracic Spine & Shoulder Mobility Flow (20 min)",
                "Active Recovery Walk & Breathwork Station"
            ]
        }, 
        "train-like": {
            "track_a": [
                "TOTAL CONCENTRATION: Box Breathing Warm-Up (5 min)",
                "Hindu Push-Ups (4 sets x 15-20 reps | Fluid Spine Power)",
                "Dead-stop Pull-Ups (4 sets x 8-12 reps | Full Extension)",
                "Parallel Bar Dips (3 sets x 15 reps)",
                "Hollow Body Holds (4 sets x 45s | Midsection Rigidity)"
            ],
            "track_b": [
                "MOUNTAIN AGILITY: Footwork Drills (15 min Non-Stop)",
                "Suicide Sprints - 30yd Shuttle (5 rounds | Low Center)",
                "Single-Leg Balance Ball Toss (3 sets x 1 min per leg)",
                "Lateral Bounds / Skater Hops (4 sets x 20 total reps)"
            ],
            "track_c": [
                "CONSTANT STAMINA: Incline Run or Stair Climb (45-60 min)",
                "THE RULE: Strict Nasal-Only Breathing (Build CO2 Tolerance)"
            ],
            "track_d": [
                "HINDU SQUATS: Rhythmic Bodyweight (4 sets x 30-40 reps)",
                "Jump Squats / Power Jumps (3 sets x 15 reps | Explosive Hip)",
                "Walking Lunges (4 sets x 24 steps total | Endurance)",
                "Towel Dead-Hangs (3 sets x Max Time | Sword Retention Grip)"
            ],
            "track_e": [
                "WEAPON FLOW: Overhead Slashes (200 reps | 4 sets of 50)",
                "WEAPON FLOW: Diagonal Slashes (200 reps | Core Rotational)",
                "Reflex Ball Headband Kit Training (10-15 min Continuous)"
            ],
            "track_f": [
                "FINAL SELECTION CIRCUIT: 4-5 Rounds (90s Rest between rounds)",
                "400m Run + 15 Burpees + 20 Mountain Climbers",
                "15 Push-Ups + 15 Jump Squats"
            ],
            "recovery": [
                "Diaphragmatic Breathing Meditation & Belly Control (10 min)",
                "Full-Body Flexibility Flow - T-Spine, Hips, Hamstrings (30 min)"
            ]
        } 
    },
    "tengen": {
        "physique": {
            "track_a": [
                "FLASHY CHEST DENSITY: Incline Dumbbell Press (4 sets x 8-10 reps)",
                "Flat Barbell Bench Press (3 sets x 8-12 reps)",
                "Chest-Supported T-Bar Row (3 sets x 10-12 reps)",
                "SUPERSET: DB Hammer Curls + Overhead Ext (4 sets x 10/12 reps)",
                "Cable Bicep Curls (3 sets x 12-15 reps | Last set Drop-Set)"
            ],
            "track_b": [
                "GOD OF FESTIVITIES DELTS: Seated Dumbbell Shoulder Press (4 sets x 8-10 reps)",
                "Incline Smith Machine Press (3 sets x 10-12 reps)",
                "Dumbbell Lateral Raises (4 sets x 12-15 reps | Strict Form)",
                "Cable Pec Flyes (3 sets x 12-15 reps | Deep Stretch)",
                "Tricep Rope Pushdowns (4 sets x 12-15 reps | 1s Hold)"
            ],
            "track_c": [
                "SOUND HASHIRA GUNS: Barbell Bicep Curls (4 sets x 8-10 reps)",
                "EZ-Bar Skull Crushers (4 sets x 10-12 reps)",
                "SUPERSET: Cable Lat Raises + Behind-Back Wrist Curls (4 sets x 15/20 reps)",
                "Dumbbell Incline Hammer Curls (3 sets x 12 reps)",
                "Tricep Overhead Cable Extensions (3 sets x 12-15 reps)"
            ],
            "track_d": [
                "WIDE LATS & BACK THICKNESS: Heavy Weighted Pull-Ups (4 sets x 6-8 reps)",
                "Neutral Grip Lat Pulldown (3 sets x 10-12 reps | Squeeze Lats)",
                "Barbell Bent-Over Rows (4 sets x 8-10 reps)",
                "Dumbbell Shrugs (4 sets x 12-15 reps | Squeeze Top)",
                "Face Pulls (3 sets x 15-20 reps | Rear Delts & Traps)"
            ],
            "track_e": [
                "EXPLOSIVE SHINOBI LEGS: Barbell Back Squats or Hack Squats (4 sets x 8-10 reps)",
                "Romanian Deadlifts - RDLs (3 sets x 10 reps | Posterior Chain)",
                "Dumbbell Walking Lunges (3 sets x 12 steps per leg)",
                "Standing Calf Raises (4 sets x 15 reps)",
                "Hanging Leg Raises (4 sets x 12-15 reps | Core Bracing)"
            ],
            "recovery": [
                "FLASHY RESTORATION: Deep Full-Body Muscle Stretching & Joint Decompression (20 min)",
                "Mobility Arc Recovery Drill",
                "Diaphragmatic Breathing Rhythm Cycle"
            ],
        },
        "train-like": {
            "track_a": [
                "FLASHY AGILITY & SPEED: Power Cleans (4 sets x 3-5 reps | 2-3 min rest)",
                "Med Ball Rotational Slams (4 sets x 8 reps per side)",
                "Landmine Press & Pivot (3 sets x 8 reps per side)",
                "Weighted Pull-Ups (4 sets x 6 reps | Heavy Pulling)",
                "Pallof Press (3 sets x 12 reps per side | Core Stability)"
            ],
            "track_b": [
                "EXPLOSIVE SHINOBI POWER: Front Squats (4 sets x 5 reps | High Core Demand)",
                "Heavy Farmer's Walks (4 rounds x 40 meters | Grip Focus)",
                "Kettlebell Swings (3 sets x 15 reps | Posterior Snap)",
                "Z Press - Seated on Floor (3 sets x 8 reps | Pure Shoulders)",
                "Hanging Leg Raises with a Twist (3 sets x 12 reps)"
            ],
            "track_c": [
                "SHINOBI SPEED DRILLS: 40m Max-Effort Sprints (6-8 rounds)",
                "Depth Jumps into Broad Jump (4 sets x 5 reps | Explosive)",
                "Lateral Box Jumps (3 sets x 8 reps per side)",
                "Single-Leg Bounds (3 sets x 15 yards per leg)",
                "Med Ball Overhead Backward Throws (4 sets x 5 reps)"
            ],
            "track_d": [
                "RESONANCE COMBAT CIRCUIT: Kettlebell Swings (4 sets x 15 reps)",
                "Band-Resisted Sprints (4 sets x 15 meters)",
                "Zercher Squat Explosions (4 sets x 6 reps)",
                "Overhead Slam Ball (4 sets x 10 reps)",
                "Ab Wheel Rollouts (3 sets x 10 reps)"
            ],
            "track_e": [
                "MAXIMUM VELOCITY & STRENGTH: Depth Jumps to Sprint (4 sets x 4 reps)",
                "Push Press (4 sets x 5 reps)",
                "Behind-Back Wrist Curls (4 sets x 20 reps | Explosive Grip)",
                "Decline Crunches with Twist (3 sets x 15 reps)"
            ],
            "recovery": [
                "Light Yoga Flow & Joint Decompression (20-30 min)",
                "Deep Shinobi Stretching (Hamstrings, Hip Flexors, Calves)",
                "Tactical Stance Work & Flow Recovery Drill"
            ]
        }
    },
    "inosuke": {
        "physique": {
            "track_a": [
                "Incline Dumbbell Bench Press (4 sets x 8-10 reps | 2 min rest)",
                "Flat Barbell Bench Press (3 sets x 8-12 reps)",
                "Standing Overhead Barbell Press - OHP (3 sets x 8 reps)",
                "High-to-Low Cable Pec Flyes (4 sets x 12-15 reps | Sharp Pec Line)",
                "Dumbbell Lateral Raises (4 sets x 15 reps | Pump Focus)"
            ],
            "track_b": [
                "Heavy Barbell Shrugs (4 sets x 10-12 reps | 1s Trap Hold)",
                "Overhand Barbell Rows (4 sets x 8-10 reps)",
                "Chest-Supported Dumbbell Rows (3 sets x 12 reps | Deep Squeeze)",
                "Neutral Grip Lat Pulldown (3 sets x 10-12 reps)",
                "Face Pulls (4 sets x 15-20 reps | Rear Delt Health)"
            ],
            "track_c": [
                "BEAST MIDSECTION: Weighted Russian Twists (4 sets x 20 reps per side)",
                "Hanging Leg Raises (4 sets x 12-15 reps | Controlled)",
                "Ab Wheel Rollouts or Planks (3 sets x Max Effort)",
                "SUPERSET: Barbell Bicep Curls (4x10) + Cable Tricep Extensions (4x12)",
                "Hammer Curls (3 sets x 12 reps | Thick Forearms)"
            ],
            "track_d": [
                "Weighted Dips (4 sets x 8-10 reps | Lower Pec Focus)",
                "Dumbbell Incline Flyes (3 sets x 12 reps)",
                "Seated Dumbbell Shoulder Press (3 sets x 10 reps)",
                "Cable Lateral Raises (4 sets x 15 reps | Constant Tension)",
                "Push-Ups Finisher (3 sets x AMRAP | Maximum Flush)"
            ],
            "track_e": [
                "Wide-Grip Pull-Ups (4 sets x 8-12 reps | Back Width)",
                "Single-Arm Dumbbell Row (3 sets x 10 reps per arm)",
                "Dumbbell Shrugs with Forward Lean (3 sets x 15 reps)",
                "Reverse Dumbbell Flyes (4 sets x 15 reps | Rear Delts)",
                "Incline Dumbbell Curls (3 sets x 12 reps)"
            ],
            "track_f": [
                "DYNAMIC OBLIQUES: Hanging Knee Raises with Side Twist (4x12 per side)",
                "Cable Woodchoppers (3 sets x 15 reps per side)",
                "Behind-the-Back Wrist Curls (4 sets x 15-20 reps | Vascular Forearms)",
                "Standing Calf Raises (5 sets x 20 reps | Slow Tempo)"
            ],
            "recovery": [
                "INOSUKE FLEXIBILITY: Deep Static Stretching Flow (20-30 min)",
                "Spine Decompression, Hip Openers, & Shoulder Mobility Flow"
            ]
        }, 
        
        "train-like": {
            "track_a": [
                "PRIMAL LOCOMOTION: Bear Crawls (4 rounds x 30m | Low Hips)",
                "Crab Walks (3 rounds x 20m | Shoulder & Hip Focus)",
                "Frogger Hops - Lateral & Forward (3 sets x 15 reps)",
                "Directional Reactive Sprints (6 rounds x 20m | Instantly Adjust)"
            ],
            "track_b": [
                "HYPER-MOBILITY: Bridge Wall Walks (3 sets x 4-6 reps)",
                "Deep Cossack Squats (3 sets x 10 reps per side | Deep Sink)",
                "Skin-the-Cat on Gymnastic Rings (3 sets x 5 reps | Shoulder Mobility)",
                "Active Floor Spine Decompression & Twists (10 min Continuous)"
            ],
            "track_c": [
                "BEAST STRIKING: Med Ball Rotational Throws (4 sets x 8 reps per side)",
                "Landmine Rainbows / Twists (3 sets x 10 reps total | Core Torque)",
                "Kettlebell Windmills (3 sets x 5 reps per side | Deep Obliques)",
                "Sledgehammer Tire Slams or Mace Swings (4 sets x 1 min Continuous)"
            ],
            "track_d": [
                "MULTI-PLANAR STRENGTH: Sandbag Cleans & Throws (4 sets x 6 reps)",
                "Heavy Farmer's Walks with Fat Grips (4 rounds x 40m | Wild Grip)",
                "Alternating Commando Grip Pull-Ups (4 sets x AMRAP)",
                "Zercher Squats - Barbell or Object (3 sets x 8 reps | Core Bracing)"
            ],
            "track_e": [
                "SPATIAL PERCEPTION: Low-Stance Shadow Sparring (20 min Dual Flow)",
                "Tennis Ball Blind-Drop Drill (10 min Auditory Perception Focus)",
                "Sprawl Drills to Low Athletic Stance (3 sets x 1 min)"
            ],
            "track_f": [
                "MOUNT FUJIKASANE CIRCUIT: 4 Brutal Rounds (2 min Rest between rounds)",
                "20m Fast Bear Crawl + 10 Sandbag Ground-to-Overhead",
                "15 Bodyweight Jump Squats + 50m Full Out Sprint"
            ],
            "recovery": [
                "Passive Stretching Flow - Long 2 min Holds (30 min)",
                "Deep Oblique, Lat, & Forearm Tissue Recovery Foam Roll"
            ]
        } 
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
    raw_strategy = str(profile_data.get("strategyGoal", "physique")).lower().replace("_", "-")
    if "train" in raw_strategy:
        strategy = "train-like"
    else:
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
    char_template = CHARACTER_TEMPLATES.get(char_key, CHARACTER_TEMPLATES.get("toji", {}))
    if strategy not in char_template:
        strategy = "physique" if "physique" in char_template else list(char_template.keys())[0]
    
    selected_template = char_template[strategy] 
    # Dynamic Focus Directive Extraction (Auto-extracts header before ':')
    raw_exercises = selected_template.get(track_key, [])
    first_exercise_str = raw_exercises[0] if raw_exercises else ""
    if ":" in first_exercise_str:
        focus_directive = first_exercise_str.split(":")[0].strip()
    else:
        # Generic fallback that fits any character without breaking the UI
        focus_directive = f"{strategy.replace('-', ' ').upper()} PROTOCOL" 
    exercises = replace_heavy_bodyweight_movements(raw_exercises, weight) 
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

    # focus_directive = TRACK_FOCUS[track_key] 
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
