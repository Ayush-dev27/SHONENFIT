// --- Database Configuration for Characters ---
const UNIVERSE_CHARACTERS = {
    'jjk': [
        { id: 'itadori', name: 'Yuji Itadori', img: 'images/itadori.jpg', desc: 'Incredible explosiveness, high leaping power, and raw brute strength endurance.' },
        { id: 'toji', name: 'Toji Fushiguro', img: 'images/toji.jpg', desc: 'Peak human anatomy. Unmatched functional core power, lean density, and velocity.' },
        { id: 'maki', name: 'Maki Zenin', img: 'images/maki.jpg', desc: 'High-tier agility conditioning, weapon core stability, and relentless physical output.' }
    ],
    'demon-slayer': [
        { id: 'tanjiro', name: 'Tanjiro Kamado', img: 'images/tanjiro.jpg', desc: 'Constant cardio lung-capacity adaptation, unilateral leg drive, and rotational sword speed.' },
        { id: 'tengen', name: 'Tengen Uzui', img: 'images/tengen.jpg', desc: 'Massive shoulder/arm power, explosive speed bursts, and highly coordinated stamina chains.' },
        { id: 'inosuke', name: 'Inosuke Hashibira', img: 'images/inosuke.jpg', desc: 'Extreme multi-directional joint mobility, core flexibility, and unanchored athletic stamina.' }
    ],
    'mha': [
        { id: 'deku', name: 'Izuku Midoriya (Deku)', img: 'images/deku.jpg', desc: 'Full-body impact mechanics, reactive plyometrics, and progressive scaling overload resistance.' },
        { id: 'bakugo', name: 'Katsuki Bakugo', img: 'images/bakugo.jpg', desc: 'Explosive wrist/forearm mechanics, rapid direction-shift reaction tracking, and upper-body power.' },
        { id: 'all-might', name: 'All Might (Prime)', img: 'images/all-might.jpg', desc: 'Maximum mass hypertrophy blueprint, foundational heavy compounds, and ultimate raw force generation.' }
    ]
};

// --- App State Engine Data Structure ---
let userSessionProfile = {
    selectedUniverse: '',
    selectedCharacter: '',
    age: null,
    height: null,
    weight: null,
    medicalHistory: '',
    specialPreferences: '',
    strategyGoal: '' // 'physique' or 'train-like'
};

document.addEventListener('DOMContentLoaded', () => {
    
    // --- Step Navigation Mechanism ---
    function navigateToView(viewId) {
        // Hide all structural blocks
        document.querySelectorAll('.flow-view').forEach(view => {
            view.classList.remove('active');
        });
        
        // Show specified view target
        const targetView = document.getElementById(viewId);
        if (targetView) {
            targetView.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
        
        // Synchronize Global Navbar Link Highlighting State
        document.querySelectorAll('.nav-links a').forEach(link => {
            if (link.getAttribute('data-target') === viewId) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // Direct routing listeners (Logo, Home Links, CTAs)
    document.querySelectorAll('.view-router-btn, .nav-item').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            const targetView = element.getAttribute('data-target') || 'hero-view';
            navigateToView(targetView);
        });
    });

    // Handle generic structural back buttons
    document.querySelectorAll('.back-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const fallbackTarget = btn.getAttribute('data-target');
            navigateToView(fallbackTarget);
        });
    });

    // --- Universe Selection Processing ---
    document.querySelectorAll('.universe-card').forEach(card => {
        card.addEventListener('click', () => {
            const universeKey = card.getAttribute('data-universe');
            userSessionProfile.selectedUniverse = universeKey;
            
            buildCharacterSelectionInterface(universeKey);
            navigateToView('character-view');
        });
    }); 

    // --- Dynamic Character Selection Content Generation ---
    function buildCharacterSelectionInterface(universeKey) {
        const characterPool = document.getElementById('character-pool');
        characterPool.innerHTML = ''; // Wipe existing items
        
        const characters = UNIVERSE_CHARACTERS[universeKey] || [];
        
        characters.forEach(char => {
            // Build elements carefully without merging inline logic
            const cardFrame = document.createElement('div');
            cardFrame.className = 'character-card';
            cardFrame.setAttribute('data-char-id', char.id);
            
            const backgroundDiv = document.createElement('div');
            backgroundDiv.className = 'card-bg char-fallback';
            backgroundDiv.style.backgroundImage = `linear-gradient(to top, #12141c 30%, rgba(0, 0, 0, 0.2)), url('${char.img}')`;
            
            const contentFrame = document.createElement('div');
            contentFrame.className = 'card-content';
            
            const nameHeader = document.createElement('h3');
            nameHeader.textContent = char.name;
            
            const descriptionPara = document.createElement('p');
            descriptionPara.textContent = char.desc;
            
            // Append structures down the hierarchy tree cleanly
            contentFrame.appendChild(nameHeader);
            contentFrame.appendChild(descriptionPara);
            cardFrame.appendChild(backgroundDiv);
            cardFrame.appendChild(contentFrame);
            
            // Add click engagement tracking inside dynamic factory context
            cardFrame.addEventListener('click', () => {
                userSessionProfile.selectedCharacter = char.name;
                
                // Configure structural fallback navigation for back button on Form view
                document.getElementById('form-back-btn').setAttribute('data-target', 'character-view');
                
                navigateToView('form-view');
            });
            
            characterPool.appendChild(cardFrame);
        });
    }

    // --- Profile Data Form Submission Handler ---
    const metricsForm = document.getElementById('vitals-form');
    if (metricsForm) {
        metricsForm.addEventListener('submit', (event) => {
            event.preventDefault(); // Intercept page reload mechanics
            
            // Map inputs to data state dictionary object
            userSessionProfile.age = document.getElementById('user-age').value;
            userSessionProfile.height = document.getElementById('user-height').value;
            userSessionProfile.weight = document.getElementById('user-weight').value;
            userSessionProfile.medicalHistory = document.getElementById('user-history').value;
            userSessionProfile.specialPreferences = document.getElementById('user-prefs').value;
            
            // Extract selected strategy choice
            const checkedStrategy = document.querySelector('input[name="training-strategy"]:checked');
            userSessionProfile.strategyGoal = checkedStrategy ? checkedStrategy.value : 'physique';
            
            // Execute view render processing
            renderDashboardSummary();
            navigateToView('dashboard-view');
        });
    }

    // --- Final Step Summary Builder ---
    function renderDashboardSummary() {
        const targetString = `${userSessionProfile.selectedCharacter} (${userSessionProfile.selectedUniverse.toUpperCase()})`;
        const strategyString = userSessionProfile.strategyGoal === 'physique' ? 'Physique Structural Optimization' : 'Functional Performance & Training Protocol';
        
        document.getElementById('summary-target').textContent = targetString;
        document.getElementById('summary-strategy').textContent = strategyString;
        
        console.log("SHONENFIT Profile Construction Complete. Profile Payload Context Compiled:", userSessionProfile);
    }
}); 