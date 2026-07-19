/* ============================================================================
   SHONENFIT - Application Logic
   ============================================================================ */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const API_PROFILE_ENDPOINT = 'http://127.0.0.1:5000/api/profile';
const API_SIGNUP_ENDPOINT = 'http://127.0.0.1:5000/api/signup';
const API_LOGIN_ENDPOINT = 'http://127.0.0.1:5000/api/login';
const API_WORKOUT_COMPLETE_ENDPOINT = 'http://127.0.0.1:5000/api/workout-complete';
const API_WORKOUT_HISTORY_ENDPOINT = 'http://127.0.0.1:5000/api/workout-history';
const TIMER_TOTAL_SECONDS = 90;

const DEFAULT_PROFILE_VALUES = {
  age: '25',
  height: '175',
  weight: '70',
  medicalHistory: 'No reported injuries',
  specialPreferences: 'Balanced strength and conditioning',
  strategyGoal: 'train-like',
};

function calculateGradeProgress(totalExp) {
    const thresholds = [
        { name: "Special Grade", minExp: 10000 },
        { name: "Grade 1",      minExp: 6000  },
        { name: "Grade 2",      minExp: 3000  },
        { name: "Grade 3",      minExp: 1000  },
        { name: "Grade 4",      minExp: 0     }
    ];

    let currentTierIndex = thresholds.findIndex(t => totalExp >= t.minExp);
    let currentTier = thresholds[currentTierIndex];
    
    if (currentTier.name === "Special Grade") {
        return {
            grade: currentTier.name,
            currentExpInTier: totalExp - currentTier.minExp,
            expNeededForNextTier: 0,
            progressPercentage: 100
        };
    }

    let nextTier = thresholds[currentTierIndex - 1];
    let tierRange = nextTier.minExp - currentTier.minExp;
    let currentExpInTier = totalExp - currentTier.minExp;
    let expNeededForNextTier = nextTier.minExp - totalExp;
    let progressPercentage = Math.min((currentExpInTier / tierRange) * 100, 100);

    return {
        grade: currentTier.name,
        currentExpInTier: currentExpInTier,
        expNeededForNextTier: expNeededForNextTier,
        progressPercentage: Math.round(progressPercentage)
    };
} 

const appState = {
  selectedUniverse: null,
  selectedCharacter: null,
  selectedDirection: null,
  latestWorkoutData: null,
  isSubmitting: false,
  isAuthenticated: false,
  userMetrics: {
    age: null,
    height: null,
    weight: null,
    medicalHistory: null,
    preferences: null, 
    totalExp: 0
  },
};

const userSessionProfile = appState;
window.userSessionProfile = userSessionProfile;

let timerRunning = false;
let timerInterval = null;
let timeRemaining = TIMER_TOTAL_SECONDS;
let audioContext = null;
let previousGrade = 'Grade 4';
let pendingAscensionState = null;

const characterDatabase = {
  jjk: [
    { id: 'itadori', name: 'Yuji Itadori', desc: 'Incredible explosiveness, high leaping power, and raw brute strength endurance.', image: 'images/itadori.jpg', imgFilename: './images/itadori.jpg', objectPosition: 'center' },
    { id: 'toji', name: 'Toji Fushiguro', desc: 'Peak human anatomy. Unmatched functional core power, lean density, and velocity.', image: 'images/toji.jpg', imgFilename: './images/toji.jpg', objectPosition: 'center' },
    { id: 'maki', name: 'Maki Zenin', desc: 'High-tier agility conditioning, weapon core stability, and relentless physical output.', image: 'images/maki.jpg', imgFilename: './images/maki.jpg', objectPosition: 'top' },
  ],
  'demon-slayer': [
    { id: 'tanjiro', name: 'Tanjiro Kamado', desc: 'Constant cardio lung-capacity adaptation, unilateral leg drive, and rotational sword speed.', image: 'images/tanjiro.jpg', imgFilename: './images/tanjiro.jpg', objectPosition: 'center' },
    { id: 'tengen', name: 'Tengen Uzui', desc: 'Massive shoulder/arm power, explosive speed bursts, and highly coordinated stamina chains.', image: 'images/tengen.jpg', imgFilename: './images/tengen.jpg', objectPosition: 'center' },
    { id: 'inosuke', name: 'Inosuke Hashibira', desc: 'Extreme multi-directional joint mobility, core flexibility, and unanchored athletic stamina.', image: 'images/inosuke.jpg', imgFilename: './images/inosuke.jpg', objectPosition: 'center' },
  ],
  mha: [
    { id: 'deku', name: 'Izuku Midoriya (Deku)', desc: 'Full-body impact mechanics, reactive plyometrics, and progressive scaling overload resistance.', image: 'images/deku.jpg', imgFilename: './images/deku.jpg', objectPosition: 'center' },
    { id: 'bakugo', name: 'Katsuki Bakugo', desc: 'Explosive wrist/forearm mechanics, rapid direction-shift reaction tracking, and upper-body power.', image: 'images/bakugo.jpg', imgFilename: './images/bakugo.jpg', objectPosition: 'center' },
    { id: 'all-might', name: 'All Might (Prime)', desc: 'Maximum mass hypertrophy blueprint, foundational heavy compounds, and ultimate raw force generation.', image: 'images/all-might.jpg', imgFilename: './images/all-might.jpg', objectPosition: 'center' },
  ],
};

const universeCardBackgrounds = {
  'Jujutsu Kaisen': 'images/jjk-bg.jpg.jpg',
  'Demon Slayer': 'images/ds-bg.jpg.jpg',
  'My Hero Academia': 'images/mha-bg.jpg.jpg',
};

// --- BULLETPROOF COMPLETED ARC CLICK HANDLER ---
document.addEventListener('click', (event) => {
    const button = event.target.closest('button');
    const buttonLabel = button?.textContent?.trim() || '';

    // Intercept only when clicking the specific Completed Training Arc button
    if (!button || !/COMPLETED TRAINING ARC/i.test(buttonLabel)) {
        return;
    }

    console.log('[SHONENFIT] Completed Arc Button click intercepted successfully!');
    event.preventDefault();
    event.stopPropagation();

    // Directly call the real function that removes the hidden class
    if (typeof showHonestyGate === 'function') {
        showHonestyGate();
    } else {
        console.error('[SHONENFIT] Architecture Error: showHonestyGate function definition not found!');
    }
}); 

// ============================================================================
// BOOTSTRAP
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  installGlobalNavigationInterception();
  applyUniverseCardGraphics();
  wireAuthPortal();
  wireMetricsSubmission();
  wireWorkoutRouteButton();
  wireWorkoutControlButtons();
  wireHonestyGateControls();
  wireAscensionOverlayControls();
  ensureWorkoutRuntimeStyles();
  bindSetTrackingSelectors();
  initializeTimerDisplay();
  fetchWorkoutHistory();
  checkAuthSessionOnLoad();
});

// ============================================================================
// VIEW NAVIGATION
// ============================================================================

function navigateView(viewId) {
  document.querySelectorAll('.flow-view').forEach((view) => {
    view.classList.remove('active-view');
    view.classList.remove('active');
  });

  const targetView = document.getElementById(viewId);
  if (targetView) {
    targetView.classList.add('active-view');
    targetView.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function MapsToView(viewId) {
  navigateView(viewId);
}

// ============================================================================
// UNIVERSE AND CHARACTER SELECTION
// ============================================================================

function selectUniverse(universeName) {
  const universeKey = normalizeUniverseKey(universeName);
  appState.selectedUniverse = universeKey;
  populateCharacterPool(universeKey);
  navigateView('character-view');
}

function populateCharacterPool(universeName) {
  const pool = document.getElementById('character-pool');
  const universeKey = normalizeUniverseKey(universeName);
  const characters = characterDatabase[universeKey] || [];

  if (!pool) {
    return;
  }

  pool.innerHTML = '';

  characters.forEach((character) => {
    const card = document.createElement('div');
    card.className = 'character-card';
    card.innerHTML = `
      <img src="${character.image || character.imgFilename}" alt="${character.name} Visual Inspiration" class="character-card-visual" style="object-fit: cover; object-position: ${character.objectPosition || 'center'};">
      <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">${character.name}</h4>
      <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">${character.desc}</p>
    `;
    card.addEventListener('click', () => selectCharacter(character.name, universeKey));
    pool.appendChild(card);
  });
}

function selectCharacter(characterName, universeName) {
  appState.selectedCharacter = characterName;
  appState.selectedUniverse = normalizeUniverseKey(universeName || appState.selectedUniverse);

  if (!appState.isAuthenticated) {
    showAuthPortal();
    return;
  }

  showPathGate();
  navigateView('path-gate');
}

function normalizeUniverseKey(universeName) {
  const universeMap = {
    'Jujutsu Kaisen': 'jjk',
    'Demon Slayer': 'demon-slayer',
    'My Hero Academia': 'mha',
  };

  return universeMap[universeName] || universeName;
}

function applyUniverseCardGraphics() {
  document.querySelectorAll('.universe-card').forEach((card) => {
    const title = card.querySelector('.card-title')?.textContent?.trim();
    const visual = card.querySelector('.card-visual');
    const imagePath = universeCardBackgrounds[title];

    if (!visual || !imagePath) {
      return;
    }

    visual.innerHTML = '';
    visual.style.backgroundImage = `linear-gradient(180deg, rgba(12, 14, 20, 0.1) 0%, rgba(12, 14, 20, 0.55) 62%, rgba(12, 14, 20, 0.92) 100%), url('${imagePath}')`;
    visual.style.backgroundSize = 'cover';
    visual.style.backgroundPosition = 'center';
    visual.style.filter = 'saturate(1.05) contrast(1.05)';

    const overlay = document.createElement('div');
    overlay.className = 'universe-card-visual-mask';
    Object.assign(overlay.style, {
      position: 'absolute',
      inset: '0',
      background: 'linear-gradient(135deg, rgba(12, 14, 20, 0.08), rgba(12, 14, 20, 0.72))',
      backdropFilter: 'brightness(0.95)',
      pointerEvents: 'none',
    });
    visual.appendChild(overlay);
  });
}

// ============================================================================
// AUTHENTICATION PORTAL
// ============================================================================

async function checkAuthSessionOnLoad() {
  try {
    const response = await fetch(API_PROFILE_ENDPOINT, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (response.status === 401) {
      showAuthPortal();
      return;
    }

    if (!response.ok) {
      console.info(`[SHONENFIT] Session probe skipped: HTTP ${response.status}`);
      return;
    }

    const result = await response.json();
    handleAuthSuccess(result);
  } catch (error) {
    console.info('[SHONENFIT] Auth session probe unavailable; continuing local SPA mode.', error);
  }
}

function wireAuthPortal() {
  const signupForm = document.getElementById('signup-form');
  const loginForm = document.getElementById('login-form');
  const authSubmitButton = document.getElementById('auth-submit-btn');
  const authTabs = document.querySelectorAll('input[name="auth-tab"]');
  const authTabLabels = document.querySelectorAll('.auth-tab-label');

  syncAuthPortalScrollState();

  authTabs.forEach((tab) => {
    tab.addEventListener('change', syncAuthPortalScrollState);
  });

  authTabLabels.forEach((label) => {
    label.addEventListener('click', () => {
      window.requestAnimationFrame(syncAuthPortalScrollState);
    });
  });

  signupForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    event.stopPropagation();
    submitAuthForm('signup');
  });

  loginForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    event.stopPropagation();
    submitAuthForm('login');
  });

  authSubmitButton?.addEventListener('click', (event) => {
    event.preventDefault();
    event.stopPropagation();
    const activeMode = document.getElementById('auth-login-tab')?.checked ? 'login' : 'signup';
    submitAuthForm(activeMode);
  });
}

function syncAuthPortalScrollState() {
  const isLoginActive = document.getElementById('auth-login-tab')?.checked;
  const activePanel = document.getElementById(isLoginActive ? 'login-form' : 'signup-form');
  const inactivePanel = document.getElementById(isLoginActive ? 'signup-form' : 'login-form');
  const authOverlay = document.getElementById('auth-portal-overlay');

  document.body?.style.setProperty('overflow-y', 'auto', 'important');

  if (authOverlay) {
    authOverlay.style.overflowY = 'auto';
  }

  inactivePanel?.classList.remove('auth-panel-active');

  if (activePanel) {
    activePanel.classList.add('auth-panel-active');
    activePanel.style.overflowY = 'visible';
  }
}

async function submitAuthForm(mode) {
  clearAuthError();
  setAuthLoadingState(true);

  const payload = mode === 'signup' ? buildSignupPayload() : buildLoginPayload();
  const endpoint = mode === 'signup' ? API_SIGNUP_ENDPOINT : API_LOGIN_ENDPOINT;

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json().catch(() => ({}));

    if (!response.ok || result?.status === 'error') {
      showAuthError(result?.message || `Authentication failed with HTTP ${response.status}.`);
      return;
    }

    handleAuthSuccess(result, payload, mode);
  } catch (error) {
    console.error('[SHONENFIT] Auth request failed:', error);
    showAuthError('Could not reach the auth server. Make sure Flask is running on http://127.0.0.1:5000.');
  } finally {
    setAuthLoadingState(false);
  }
}

function buildSignupPayload() {
  return {
    username: document.getElementById('signup-username')?.value.trim() || 'Recruit',
    password: document.getElementById('signup-password')?.value || '',
    age: document.getElementById('signup-age')?.value || DEFAULT_PROFILE_VALUES.age,
    weight: document.getElementById('signup-weight')?.value || DEFAULT_PROFILE_VALUES.weight,
    height: document.getElementById('signup-height')?.value || DEFAULT_PROFILE_VALUES.height,
  };
}

function buildLoginPayload() {
  return {
    username: document.getElementById('login-username')?.value.trim() || '',
    password: document.getElementById('login-password')?.value || '',
  };
}

function handleAuthSuccess(result = {}, submittedPayload = {}, mode = 'login') {
  appState.isAuthenticated = true;
  hideAuthPortal();
  showMainLandingPage();
  hidePathGate();

  const profileData = result.profile || result.user || result;
  const workoutData = normalizeWorkoutData(result.workout_data || profileData.workout_data);
  const hasSavedPathSelection = hasActivePathSelection(profileData);

  if (submittedPayload.age || profileData.age) {
        appState.userMetrics = {
            age: submittedPayload.age || profileData.age || null,
            height: submittedPayload.height || profileData.height || null,
            weight: submittedPayload.weight || profileData.weight || null,
            medicalHistory: profileData.medical_history || null,
            preferences: profileData.special_preferences || null,
            totalExp: profileData.total_exp || profileData.totalExp || profileData.new_exp || 0
        };
    } 

  if (!hasSavedPathSelection) {
    navigateView('universe-view');
    return;
  }

  if (workoutData) {
    appState.latestWorkoutData = workoutData;
    renderDashboardSummary(workoutData);
  }

  // Calculate full Shonen metrics using the loaded database EXP values
        const currentTotalExp = appState.userMetrics.totalExp || 0;
        const initialProgress = calculateGradeProgress(currentTotalExp);

        previousGrade = initialProgress.grade;
        applyRankBadgeState(initialProgress.grade); 
  renderDashboardStreak(result.current_streak !== undefined ? result : profileData);
  fetchWorkoutHistory();
  navigateView('dashboard-view');
}

function hasActivePathSelection(profileData = {}) {
  const selectedCharacter = appState.selectedCharacter
    || profileData.selected_character
    || profileData.selectedCharacter
    || profileData.character
    || '';
  const selectedUniverse = appState.selectedUniverse
    || profileData.selected_universe
    || profileData.selectedUniverse
    || profileData.universe
    || '';

  return Boolean(selectedCharacter || selectedUniverse);
}

function hidePathGate() {
  const pathGate = document.getElementById('path-gate');
  if (!pathGate) {
    return;
  }

  pathGate.classList.remove('active');
  pathGate.classList.remove('active-view');
  pathGate.classList.add('hidden');
  pathGate.style.display = 'none';
  pathGate.setAttribute('aria-hidden', 'true');
}

function showPathGate() {
  const pathGate = document.getElementById('path-gate');
  if (!pathGate) {
    return;
  }

  pathGate.classList.remove('hidden');
  pathGate.classList.add('active');
  pathGate.classList.add('active-view');
  pathGate.style.display = '';
  pathGate.setAttribute('aria-hidden', 'false');
}

function showMainLandingPage() {
  const authGate = document.getElementById('auth-gate');
  if (authGate) {
    authGate.style.display = 'none';
  }

  document.getElementById('auth-portal-overlay')?.classList.add('hidden');
  setMainAppVisibility(true);
  navigateView('home');
}

function showAuthPortal() {
  appState.isAuthenticated = false;
  setMainAppVisibility(false);
  hidePathGate();

  const authGate = document.getElementById('auth-gate');
  if (authGate) {
    authGate.style.display = '';
  }

  const dashboardView = document.getElementById('dashboard-view');
  if (dashboardView) {
    dashboardView.classList.add('hidden');
    dashboardView.style.display = 'none';
  }

  document.getElementById('auth-portal-overlay')?.classList.remove('hidden');
}

function hideAuthPortal() {
  const authGate = document.getElementById('auth-gate');
  if (authGate) {
    authGate.style.display = 'none';
  }

  document.getElementById('auth-portal-overlay')?.classList.add('hidden');
}

function setMainAppVisibility(isVisible) {
  document.querySelectorAll('.flow-view').forEach((view) => {
    view.style.display = isVisible ? '' : 'none';
    view.setAttribute('aria-hidden', String(!isVisible));
  });

  if (isVisible) {
    const hasActiveView = document.querySelector('.flow-view.active-view, .flow-view.active');
    if (!hasActiveView) {
      navigateView('dashboard-view');
    }
  }
}

function showAuthError(message) {
  const portalCard = document.querySelector('#auth-portal-overlay .auth-portal-card');
  if (!portalCard) {
    alert(message);
    return;
  }

  let errorBox = document.getElementById('auth-error-message');
  if (!errorBox) {
    errorBox = document.createElement('div');
    errorBox.id = 'auth-error-message';
    errorBox.className = 'auth-error-message';
    const submitButton = document.getElementById('auth-submit-btn');
    portalCard.insertBefore(errorBox, submitButton || null);
  }

  errorBox.hidden = false;
  errorBox.textContent = message;
}

function clearAuthError() {
  const errorBox = document.getElementById('auth-error-message');
  if (errorBox) {
    errorBox.textContent = '';
    errorBox.hidden = true;
  }
}

function setAuthLoadingState(isLoading) {
  const authSubmitButton = document.getElementById('auth-submit-btn');
  if (!authSubmitButton) {
    return;
  }

  authSubmitButton.disabled = isLoading;
  authSubmitButton.textContent = isLoading ? 'OPENING GATE...' : 'ENTER THE TRAINING GROUNDS';
}

// ============================================================================
// LIVE BACKEND PROFILE SUBMISSION
// ============================================================================

function installGlobalNavigationInterception() {
  window.addEventListener('click', (e) => {
    const target = e.target.closest('a') || e.target.closest('button');
    if (target && (target.getAttribute('href') === '#' || target.id === 'submit-metrics-btn')) {
      if (target.id === 'submit-metrics-btn') {
        e.preventDefault();
        e.stopPropagation();
        submitMetricsProfile();
      } else {
        e.preventDefault();
      }
    }
  }, { capture: true });
}

function wireMetricsSubmission() {
  const form = document.getElementById('metrics-form') || document.getElementById('vitals-form');
  const submitButton = document.getElementById('submit-metrics-btn');

  if (form?.tagName === 'FORM') {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      await submitMetricsProfile();
    });
  }

  if (submitButton) {
    submitButton.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();

      await submitMetricsProfile();
    });
  }
}

async function submitMetricsProfile() {
  if (appState.isSubmitting) {
    return;
  }

  appState.isSubmitting = true;
  const payload = buildProfilePayload();
  setSubmitLoadingState(true);

  try {
    const response = await fetch(API_PROFILE_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const result = await parseProfileResponse(response);

    if (!response.ok || result?.status !== 'success') {
      console.error('[SHONENFIT] Backend profile sync failed:', result);
      alert(`Database Sync Failed: ${result?.message || `HTTP ${response.status}`}`);
      return;
    }

    const workoutData = normalizeWorkoutData(result.workout_data);

    if (!workoutData) {
      console.error('[SHONENFIT] Backend response is missing a valid workout_data object:', result);
      alert('Workout generation returned an unexpected data shape. Check the Flask response payload in the console.');
      return;
    }

    appState.latestWorkoutData = workoutData;
    appState.userMetrics = {
      age: payload.age,
      height: payload.height,
      weight: payload.weight,
      medicalHistory: payload.medicalHistory,
      preferences: payload.specialPreferences,
    };
    appState.selectedDirection = payload.strategyGoal;

    const didRenderDashboard = renderDashboardSummary(workoutData);
    if (!didRenderDashboard) {
      console.error('[SHONENFIT] Dashboard render target was not available. View transition cancelled.');
      alert('Workout data was generated, but the dashboard container could not be found.');
      return;
    }

    previousGrade = result.current_grade || result.initial_grade || previousGrade;
    applyRankBadgeState(previousGrade);
    renderDashboardStreak(result);
    MapsToView('dashboard-view');
  } catch (error) {
    console.error('[SHONENFIT] Profile response processing failed:', error);
    alert('ShonenFit could not safely process the generated workout. Check the console for the exact response issue.');
  } finally {
    appState.isSubmitting = false;
    setSubmitLoadingState(false);
  }
}

async function parseProfileResponse(response) {
  try {
    return await response.json();
  } catch (error) {
    console.error('[SHONENFIT] Failed to parse Flask JSON response:', error);
    throw new Error('Invalid JSON response from Flask backend.');
  }
}

function normalizeWorkoutData(workoutData) {
  if (!workoutData || typeof workoutData !== 'object' || Array.isArray(workoutData)) {
    return null;
  }

  const routine = getRoutineArrayFromWorkoutData(workoutData);

  return {
    character_alignment: safeText(workoutData.character_alignment, appState.selectedCharacter || 'UNASSIGNED'),
    core_focus_directive: safeText(workoutData.core_focus_directive, 'Adaptive Training Protocol'),
    strategy_paradigm: safeText(workoutData.strategy_paradigm, appState.selectedDirection || 'train-like'),
    assigned_workout_routine: routine.map(normalizeExercise),
  };
}

function getRoutineArrayFromWorkoutData(workoutData) {
  const candidateKeys = [
    'assigned_workout_routine',
    'assignedWorkoutRoutine',
    'workout_routine',
    'routine',
    'exercises',
  ];

  for (const key of candidateKeys) {
    if (Array.isArray(workoutData[key])) {
      return workoutData[key];
    }
  }

  console.warn('[SHONENFIT] No routine array found on workout_data. Rendering dashboard with an empty routine.', workoutData);
  return [];
}

function normalizeExercise(exercise, index) {
  const source = exercise && typeof exercise === 'object' && !Array.isArray(exercise) ? exercise : {};

  return {
    name: safeText(source.name || source.exercise_name || source.title, `Training Movement ${index + 1}`),
    sets: safeText(source.sets, '4'),
    reps: safeText(source.reps || source.rep_bounds || source.duration, 'controlled reps'),
    coaching_cue: safeText(source.coaching_cue || source.cue || source.notes, 'Move with clean form and steady breathing.'),
  };
}

function safeText(value, fallback) {
  if (value === null || value === undefined) {
    return fallback;
  }

  const text = String(value).trim();
  return text || fallback;
}

function buildProfilePayload() {
  const strategyGoal = normalizeStrategyGoal(getCheckedValue('training-strategy')
    || getCheckedValue('direction')
    || DEFAULT_PROFILE_VALUES.strategyGoal);

  const payload = {
    selectedUniverse: appState.selectedUniverse || 'Demon Slayer',
    selectedCharacter: appState.selectedCharacter || 'Giyu Tomioka',
    age: getInputValue('user-age', 'age') || DEFAULT_PROFILE_VALUES.age,
    height: getInputValue('user-height', 'height') || DEFAULT_PROFILE_VALUES.height,
    weight: getInputValue('user-weight', 'weight') || DEFAULT_PROFILE_VALUES.weight,
    medicalHistory: getInputValue('user-history', 'medical') || DEFAULT_PROFILE_VALUES.medicalHistory,
    specialPreferences: getInputValue('user-prefs', 'preferences') || DEFAULT_PROFILE_VALUES.specialPreferences,
    strategyGoal,
  };

  Object.assign(userSessionProfile, payload);
  return payload;
}

function getInputValue(...ids) {
  for (const id of ids) {
    const element = document.getElementById(id);
    const value = element?.value?.trim();

    if (value) {
      return value;
    }
  }

  return '';
}

function getCheckedValue(name) {
  return document.querySelector(`input[name="${name}"]:checked`)?.value?.trim() || '';
}

function normalizeStrategyGoal(strategyGoal) {
  if (strategyGoal === 'training') {
    return 'train-like';
  }

  return strategyGoal;
}

function setSubmitLoadingState(isLoading) {
  const submitButton = document.getElementById('submit-metrics-btn');
  if (!submitButton) {
    return;
  }

  submitButton.disabled = isLoading;
  submitButton.textContent = isLoading ? 'SYNCING WITH ENGINE...' : 'GENERATE CUSTOM PATH';
}

// ============================================================================
// LIVE DASHBOARD RENDERING
// ============================================================================

function renderDashboardSummary(workoutData) {
  const safeWorkoutData = normalizeWorkoutData(workoutData);
  const summaryBox = document.getElementById('summary-box');
  if (!summaryBox || !safeWorkoutData) {
    return false;
  }

  summaryBox.innerHTML = '';

  const targetValue = safeWorkoutData.character_alignment;
  const strategyValue = safeWorkoutData.strategy_paradigm;
  const focusValue = safeWorkoutData.core_focus_directive;
  const routine = getAssignedWorkoutRoutine(safeWorkoutData);

  summaryBox.appendChild(createSummaryItem('Selected Target', 'summary-target', targetValue));
  summaryBox.appendChild(createSummaryItem('Strategy Selected', 'summary-strategy', formatStrategyLabel(strategyValue)));
  summaryBox.appendChild(createSummaryItem('Core Focus Directive', 'summary-focus', focusValue));

  const routineContainer = document.createElement('div');
  routineContainer.className = 'exercise-list-container';

  const routineList = document.createElement('ul');
  routineList.id = 'exercise-list';
  routineList.className = 'exercise-list';

  routine.forEach((exercise) => {
        const item = document.createElement('li');
        
        // 1. Extract the name safely whether it's an object or raw string
        const exerciseName = (typeof exercise === 'string') ? exercise : (exercise.name || '');
        
        // 2. Recovery check keywords
        // 2. Recovery check keywords (added 'recovery' and 'foam')
        const recoveryKeywords = ['stretching', 'drill', 'breathing', 'decompression', 'mobility', 'rest', 'recovery', 'foam']; 
        const isRecoveryMove = recoveryKeywords.some(keyword => exerciseName.toLowerCase().includes(keyword));
        
        // 3. Check if the backend name already has custom sets/reps inside parentheses
        const hasCustomFormatting = exerciseName.includes('(') || exerciseName.includes(':');

        // 4. Clean Render flow
        if (isRecoveryMove || hasCustomFormatting || typeof exercise === 'string') {
            // Let your custom layout strings pass through completely untouched
            item.textContent = exerciseName;
        } else if (exercise && exercise.name) {
            // Standard fallback view
            const sets = exercise.sets || 4;
            const reps = exercise.reps || '8 to 12 reps';
            item.textContent = `${exercise.name} - ${sets} sets x ${reps}`;
        } else {
            item.textContent = 'Unknown Exercise Directive';
        }
        
        routineList.appendChild(item);
    }); 
  routineContainer.appendChild(routineList);
  summaryBox.appendChild(routineContainer);
  return true;
}

function createSummaryItem(label, valueId, value) {
  const item = document.createElement('div');
  item.className = 'summary-item';

  const labelElement = document.createElement('span');
  labelElement.className = 'summary-label';
  labelElement.textContent = label;

  const valueElement = document.createElement('span');
  valueElement.className = 'summary-value';
  valueElement.id = valueId;
  valueElement.textContent = value;

  item.append(labelElement, valueElement);
  return item;
}

function renderDashboardStreak(data = {}) {
  const dashboardCard = document.querySelector('#dashboard-view .dashboard-card');
  if (!dashboardCard) {
    return;
  }

  let streakDisplay = document.getElementById('dashboard-streak-display');
  if (!streakDisplay) {
    streakDisplay = document.createElement('div');
    streakDisplay.id = 'dashboard-streak-display';

    const summaryBox = document.getElementById('summary-box');
    if (summaryBox) {
      dashboardCard.insertBefore(streakDisplay, summaryBox);
    } else {
      dashboardCard.appendChild(streakDisplay);
    }
  }

  const currentStreak = Number(data.current_streak || 0);

  if (currentStreak > 0) {
    streakDisplay.innerHTML = `
      <div class="streak-badge-card">
        <span class="streak-fire-icon">&#128293;</span>
        <span class="streak-count-text">${currentStreak}-Day Active Training Arc</span>
      </div>
    `;
    return;
  }

  streakDisplay.innerHTML = `
    <div class="streak-badge-card streak-badge-card--empty">
      <span class="streak-count-text">Begin a new training arc today to ignite your streak!</span>
    </div>
  `;
}

async function fetchWorkoutHistory() {
  const container = ensureHistoryLogContainer();
  if (!container) {
    return;
  }

  try {
    const response = await fetch(API_WORKOUT_HISTORY_ENDPOINT);
    const history = await response.json();

    if (!response.ok || !Array.isArray(history)) {
      console.error('[SHONENFIT] Workout history fetch failed:', history);
      renderWorkoutHistory([]);
      return;
    }

    renderWorkoutHistory(history);
  } catch (error) {
    console.error('[SHONENFIT] Workout history network error:', error);
    renderWorkoutHistory([]);
  }
}

function ensureHistoryLogContainer() {
  let container = document.getElementById('history-log-container');
  if (container) {
    return container;
  }

  const dashboardCard = document.querySelector('#dashboard-view .dashboard-card');
  if (!dashboardCard) {
    return null;
  }

  const historySection = document.createElement('div');
  historySection.className = 'history-log-section';

  const title = document.createElement('h3');
  title.className = 'history-log-title';
  title.textContent = 'Training Timeline';

  container = document.createElement('div');
  container.id = 'history-log-container';
  container.className = 'history-log-container';

  historySection.append(title, container);

  const dashboardActions = dashboardCard.querySelector('.dashboard-actions');
  dashboardCard.insertBefore(historySection, dashboardActions || null);

  return container;
}

function renderWorkoutHistory(history) {
  const container = ensureHistoryLogContainer();
  if (!container) {
    return;
  }

  container.innerHTML = '';

  if (!history.length) {
    const emptyState = document.createElement('p');
    emptyState.className = 'history-empty-state';
    emptyState.textContent = 'No completed training arcs logged yet.';
    container.appendChild(emptyState);
    return;
  }

  history.forEach((item) => {
    const historyCard = document.createElement('div');
    historyCard.className = 'history-item-card';

    const timestamp = item.timestamp ? new Date(item.timestamp) : null;
    const dateLabel = timestamp && !Number.isNaN(timestamp.getTime())
      ? timestamp.toLocaleDateString()
      : 'Recent';

    historyCard.innerHTML = `
      <div class="history-meta">
        <span class="history-badge">${String(item.character_id || 'ARC').toUpperCase()}</span>
        <span class="history-date">${dateLabel}</span>
      </div>
      <p class="history-text">Mastered the ${item.paradigm || 'training'} strategy path (${item.sets_completed || 0} sets logged) - <strong>+${item.exp_earned || 0} EXP</strong></p>
    `;

    container.appendChild(historyCard);
  });
}

function formatStrategyLabel(strategy) {
  const normalized = String(strategy).toLowerCase();

  if (normalized === 'physique') {
    return 'Physique Structural Optimization';
  }

  if (normalized === 'train-like' || normalized === 'training') {
    return 'Functional Performance & Training Protocol';
  }

  return strategy;
}

// ============================================================================
// ACTIVE WORKOUT ROUTING AND INJECTION
// ============================================================================

function wireWorkoutRouteButton() {
  const dashboardView = document.getElementById('dashboard-view');
  if (!dashboardView) {
    return;
  }

  const workoutButton = Array.from(dashboardView.querySelectorAll('button'))
    .find((button) => button.textContent.trim() === 'Access First Workout Routine');

  if (!workoutButton) {
    return;
  }

  workoutButton.removeAttribute('onclick');
  workoutButton.addEventListener('click', (event) => {
    event.preventDefault();
    accessWorkout();
  });
}

function accessWorkout() {
  if (!appState.latestWorkoutData) {
    alert('Generate your custom path first so the Flask engine can assign a live workout routine.');
    return;
  }

  updateWorkoutPath();
  populateWorkoutExercises();
  resetRestTimer();
  navigateView('workout-active-view');
}

function updateWorkoutPath() {
  const workoutPath = document.getElementById('workout-path');
  if (!workoutPath) {
    return;
  }

  const workoutData = appState.latestWorkoutData || {};
  const character = workoutData.character_alignment || appState.selectedCharacter || 'UNASSIGNED';
  const focus = workoutData.core_focus_directive || 'Live Training Protocol';
  workoutPath.textContent = `Path: ${character} - ${focus}`;
}

function populateWorkoutExercises() {
  const container = document.getElementById('exercise-cards-container');
  if (!container) {
    return;
  }

  const routine = getAssignedWorkoutRoutine();
  container.innerHTML = '';

  routine.forEach((exercise, index) => {
    const card = document.createElement('article');
    card.className = 'exercise-card';

    const title = document.createElement('h4');
    title.className = 'exercise-card-title';
    title.textContent = exercise.name || `Training Movement ${index + 1}`;

    const meta = document.createElement('p');
    meta.className = 'exercise-card-meta';
    meta.textContent = `${exercise.sets || 4} sets x ${exercise.reps || 'controlled reps'} - ${exercise.coaching_cue || 'Move with clean form and steady breathing.'}`;

    const setButtons = document.createElement('div');
    setButtons.className = 'set-buttons';
    const setCount = getExerciseSetCount(exercise);

    for (let setIndex = 1; setIndex <= setCount; setIndex += 1) {
      const setButton = document.createElement('button');
      setButton.type = 'button';
      setButton.className = 'set-button set-btn';
      setButton.textContent = `Set ${setIndex}`;
      setButton.dataset.exerciseIndex = String(index);
      setButton.dataset.set = String(setIndex);
      setButton.setAttribute('aria-pressed', 'false');
      setButtons.appendChild(setButton);
    }

    card.append(title, meta, setButtons);
    container.appendChild(card);
  });

  bindSetTrackingSelectors(container);
}

function getAssignedWorkoutRoutine(workoutData = appState.latestWorkoutData) {
  return Array.isArray(workoutData?.assigned_workout_routine)
    ? workoutData.assigned_workout_routine
    : [];
}

function getExerciseSetCount(exercise) {
  const parsedSets = Number.parseInt(exercise?.sets, 10);
  return Number.isFinite(parsedSets) && parsedSets > 0 ? parsedSets : 4;
}

function toggleSet(button) {
  const isActive = button.classList.toggle('active');
  button.classList.toggle('completed', isActive);
  button.setAttribute('aria-pressed', String(isActive));
}

function bindSetTrackingSelectors(scope = document) {
  const setBubbles = scope.querySelectorAll('.set-btn, .set-button, .exercise-card button');

  setBubbles.forEach((bubble) => {
    if (bubble.dataset.setTrackingBound === 'true') {
      return;
    }

    bubble.dataset.setTrackingBound = 'true';
    bubble.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      toggleSet(bubble);
    });
  });
}

function ensureWorkoutRuntimeStyles() {
  if (document.getElementById('workout-runtime-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'workout-runtime-styles';
  style.textContent = `
    #exercise-cards-container .set-button.active,
    #exercise-cards-container .set-button.completed,
    #exercise-cards-container .set-btn.active,
    #exercise-cards-container .set-btn.completed {
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      border-color: var(--accent-primary);
      color: var(--bg-primary);
      font-weight: 800;
      box-shadow: 0 0 20px rgba(255, 42, 81, 0.5);
    }

    .history-log-section {
      margin-top: 2rem;
    }

    .history-log-title {
      color: var(--text-primary);
      font-size: 1.1rem;
      letter-spacing: 0.5px;
      margin: 0 0 1rem;
      text-transform: uppercase;
    }

    .history-log-container {
      display: grid;
      gap: 0.875rem;
    }

    .history-item-card,
    .history-empty-state {
      background: rgba(18, 20, 28, 0.72);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
    }

    .history-meta {
      align-items: center;
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 0.65rem;
    }

    .history-badge {
      color: var(--accent-primary);
      font-size: 0.78rem;
      font-weight: 800;
      letter-spacing: 0.7px;
    }

    .history-date,
    .history-empty-state {
      color: var(--text-secondary);
      font-size: 0.85rem;
    }

    .history-text {
      color: var(--text-primary);
      line-height: 1.55;
      margin: 0;
    }

    #dashboard-streak-display {
      margin: 1.5rem 0 2rem;
    }

    .streak-badge-card {
      align-items: center;
      background: linear-gradient(135deg, rgba(255, 42, 81, 0.18), rgba(18, 20, 28, 0.92));
      border: 1px solid rgba(255, 42, 81, 0.48);
      border-radius: 8px;
      box-shadow: 0 0 24px rgba(255, 42, 81, 0.18);
      color: var(--text-primary);
      display: flex;
      gap: 0.85rem;
      justify-content: center;
      padding: 1rem 1.25rem;
      text-align: center;
    }

    .streak-badge-card--empty {
      background: rgba(18, 20, 28, 0.72);
      border-color: var(--border-color);
      box-shadow: none;
    }

    .streak-fire-icon {
      font-size: 1.35rem;
      line-height: 1;
    }

    .streak-count-text {
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: 0.4px;
      text-transform: uppercase;
    }
  `;
  document.head.appendChild(style);
}

// ============================================================================
// REST TIMER
// ============================================================================

function wireWorkoutControlButtons() {
  const timerButton = document.querySelector('#workout-active-view .timer-button');
  const completeButton = document.getElementById('complete-workout-btn')
    || Array.from(document.querySelectorAll('#workout-active-view button'))
      .find((button) => /COMPLETED TRAINING ARC/i.test(button.textContent));
  const backButton = Array.from(document.querySelectorAll('#workout-active-view button'))
    .find((button) => button.textContent.includes('Back to Dashboard'));

  if (timerButton) {
    timerButton.removeAttribute('onclick');
    timerButton.textContent = 'Start Rest / Resume Timer';
    timerButton.addEventListener('click', toggleRestTimer);
  }

  if (completeButton) {
    completeButton.type = 'button';
    completeButton.removeAttribute('onclick');
    completeButton.setAttribute('data-complete-workout', 'true');
  }

  if (backButton) {
    backButton.removeAttribute('onclick');
    backButton.addEventListener('click', (event) => {
      event.preventDefault();
      pauseRestTimer();
      navigateView('dashboard-view');
    });
  }
}

async function toggleRestTimer() {
  await unlockTimerAudioContext();

  if (timeRemaining <= 0) {
    timeRemaining = TIMER_TOTAL_SECONDS;
    renderTimer();
  }

  if (timerRunning) {
    pauseRestTimer();
    return;
  }

  timerRunning = true;
  updateTimerButton('PAUSE ENERGY FOCUS');

  timerInterval = window.setInterval(() => {
    timeRemaining = Math.max(0, timeRemaining - 1);
    renderTimer();

    if (timeRemaining === 0) {
      stopRestTimer();
      updateTimerButton('START REST');
      playTimerCompleteCue();
    }
  }, 1000);
}

async function unlockTimerAudioContext() {
  const AudioContextConstructor = window.AudioContext || window.webkitAudioContext;

  if (!audioContext && AudioContextConstructor) {
    audioContext = new AudioContextConstructor();
  }

  if (audioContext?.state === 'suspended') {
    await audioContext.resume();
  }
}

function pauseRestTimer() {
  stopRestTimer();

  if (timeRemaining > 0) {
    updateTimerButton(timeRemaining === TIMER_TOTAL_SECONDS ? 'Start Rest / Resume Timer' : 'Start Rest / Resume Timer');
  }
}

function stopRestTimer() {
  if (timerInterval) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }

  timerRunning = false;
}

function resetRestTimer() {
  stopRestTimer();
  timeRemaining = TIMER_TOTAL_SECONDS;
  renderTimer();
  updateTimerButton('Start Rest / Resume Timer');
}

function initializeTimerDisplay() {
  const fill = document.getElementById('timer-fill');
  if (fill) {
    fill.style.strokeDasharray = String(getTimerCircumference());
  }

  renderTimer();
  updateTimerButton('Start Rest / Resume Timer');
}

function renderTimer() {
  const timerClock = document.getElementById('timer-clock');
  const timerFill = document.getElementById('timer-fill');

  if (timerClock) {
    timerClock.textContent = formatTime(timeRemaining);
  }

  if (timerFill) {
    const circumference = getTimerCircumference();
    const progress = timeRemaining / TIMER_TOTAL_SECONDS;
    timerFill.style.strokeDashoffset = String(circumference - progress * circumference);
  }
}

function updateTimerButton(label) {
  const timerButton = document.querySelector('#workout-active-view .timer-button');
  if (!timerButton) {
    return;
  }

  timerButton.textContent = label;
  timerButton.classList.toggle('timer-active', timerRunning);
}

function getTimerCircumference() {
  return 2 * Math.PI * 45;
}

function prepareAudioContext() {
  if (audioContext) {
    return;
  }

  const AudioContextConstructor = window.AudioContext || window.webkitAudioContext;
  if (AudioContextConstructor) {
    audioContext = new AudioContextConstructor();
  }
}

function playTimerCompleteCue() {
  const audioCtx = audioContext;

  if (!audioCtx) {
    return;
  }

  if (audioCtx.state === 'suspended') {
    console.warn('[SHONENFIT] Timer audio context is suspended; beep skipped until the next user-initiated timer start.');
    return;
  }

  const oscillator = audioCtx.createOscillator();
  const gainNode = audioCtx.createGain();
  const now = audioCtx.currentTime;

  oscillator.type = 'square';
  oscillator.frequency.setValueAtTime(440, now);
  oscillator.frequency.setValueAtTime(880, now + 0.15);

  gainNode.gain.setValueAtTime(0.3, now);
  gainNode.gain.setValueAtTime(0.3, now + 0.4);
  gainNode.gain.exponentialRampToValueAtTime(0.0001, now + 0.45);

  oscillator.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.45);
}

function playAscensionChime() {
  unlockTimerAudioContext().then(() => {
    const audioCtx = audioContext;
    if (!audioCtx || audioCtx.state === 'suspended') {
      return;
    }

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    const now = audioCtx.currentTime;

    oscillator.type = 'square';
    oscillator.frequency.setValueAtTime(440, now);
    oscillator.frequency.setValueAtTime(880, now + 0.15);
    gainNode.gain.setValueAtTime(0.45, now);
    gainNode.gain.setValueAtTime(0.45, now + 0.4);
    gainNode.gain.exponentialRampToValueAtTime(0.0001, now + 0.5);

    oscillator.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    oscillator.start(now);
    oscillator.stop(now + 0.5);
  });
}

function normalizeGradeClass(grade) {
  const normalized = String(grade || 'Grade 4').toLowerCase().trim();
  if (normalized.includes('special')) {
    return 'special-grade';
  }

  const gradeMatch = normalized.match(/grade\s*(\d+)/);
  return gradeMatch ? `grade-${gradeMatch[1]}` : 'grade-4';
}

function applyRankBadgeState(grade) {
    const rankBadge = document.getElementById('rank-badge-display');
    if (!rankBadge) return;

    // 1. Clear old rank classes safely
    rankBadge.classList.remove('grade-4', 'grade-3', 'grade-2', 'grade-1', 'special-grade');
    
    // 2. Add the new class so the CSS can draw the text layout automatically
    const cleanGrade = grade.trim();
    const formattedClass = cleanGrade.toLowerCase().replace(' ', '-');
    rankBadge.classList.add(formattedClass);

    // 3. Update the descriptive milestone metrics text below the badge
    const statusNotice = document.querySelector('.status-notice');
    if (statusNotice && appState && appState.userMetrics) {
        // Fallback to 0 if the backend hasn't filled the property yet on rapid boot
        const currentExp = appState.userMetrics.totalExp || 0; 
        const metrics = calculateGradeProgress(currentExp);
        
        if (metrics.grade === "Special Grade") {
            statusNotice.textContent = `Maximum Rank achieved! Current EXP: ${currentExp}`;
        } else {
            statusNotice.textContent = `${metrics.currentExpInTier} EXP in tier. ${metrics.expNeededForNextTier} EXP to next grade (${metrics.progressPercentage}% complete).`;
        }
    }
} 

    // 3. Update the descriptive milestone metrics text below the badge
    const statusNotice = rankBadge.nextElementSibling || document.querySelector('.status-notice');
    if (statusNotice && appState.userMetrics.totalExp !== undefined) {
        const metrics = calculateGradeProgress(appState.userMetrics.totalExp);
        
        if (metrics.grade === "Special Grade") {
            statusNotice.textContent = `Maximum Rank achieved! Current EXP: ${appState.userMetrics.totalExp}`;
        } else {
            statusNotice.textContent = `${metrics.currentExpInTier} EXP in tier. ${metrics.expNeededForNextTier} EXP to next grade (${metrics.progressPercentage}% complete).`;
        }
    }


function wireAscensionOverlayControls() {
  const claimButton = document.getElementById('claim-new-power-btn');
  const overlay = document.getElementById('ascension-celebrate-overlay');

  if (!claimButton || !overlay) {
    return;
  }

  claimButton.addEventListener('click', () => {
    overlay.classList.add('hidden');

    if (!pendingAscensionState) {
      return;
    }

    const { completedSets, result } = pendingAscensionState;
    previousGrade = result.current_grade;
    updateDashboardExpBoost(completedSets, result);
    renderDashboardStreak(result);
    fetchWorkoutHistory();
    resetRestTimer();
    navigateView('dashboard-view');
    pendingAscensionState = null;
  });
}

function launchAscensionOverlay(newGrade, completedSets, result) {
  const overlay = document.getElementById('ascension-celebrate-overlay');
  const gradeEmblem = document.getElementById('ascension-grade-emblem');
  const copy = document.querySelector('#ascension-celebrate-overlay .ascension-copy');

  if (!overlay || !gradeEmblem) {
    return false;
  }

  pendingAscensionState = { completedSets, result };
  applyRankBadgeState(newGrade);

  gradeEmblem.className = `ascension-grade-emblem ${normalizeGradeClass(newGrade)}`;
  gradeEmblem.textContent = newGrade.toUpperCase();

  if (copy) {
        copy.textContent = `You have unlocked ${newGrade}. Claim your new power to return to the dashboard.`;
    } // <-- Enforces closure of the copy check

    playAscensionChime();
    overlay.classList.remove('hidden');
    return true;
} // <-- Enforces closure of launchAscensionOverlay 

// ============================================================================
// MISSION COMPLETION
// ============================================================================

function captureWorkoutCompletionContext() {
    const setButtons = document.querySelectorAll('#exercise-cards-container .set-btn');
    const completedSetButtons = Array.from(setButtons).filter(button => button.classList.contains('completed'));
    
    // 1. Map out the granular set information for the BALANCE database logger
    const granularSets = completedSetButtons.map(button => {
        // Traverse up to find the closest card container to grab the exercise title
        const cardElement = button.closest('.exercise-card') || button.closest('div');
        const titleElement = cardElement ? cardElement.querySelector('.exercise-title, h4, h3') : null;
        const exerciseName = titleElement ? titleElement.textContent.trim() : 'Unknown Exercise';

        return {
            exercise_name: exerciseName,
            set_index: parseInt(button.dataset.set || '1', 10),
            reps: 10, // Default baseline reps per set since we are using checkboxes
            weight: 0.0 // Default baseline weight load applied
        };
    });

    const totalSets = setButtons.length;

    const workoutContext = {
        character_id: getActiveCharacterId(),
        sets_completed: completedSetButtons.length,
        total_sets: totalSets,
        completed_at: new Date().toISOString(),
        sets: granularSets // Injecting the array for app.py
    };

    appState.latestWorkoutData = workoutContext;
    return workoutContext;
} 

function wireHonestyGateControls() {
  const yesButton = document.getElementById('honesty-yes-btn');
  const noButton = document.getElementById('honesty-no-btn');

  if (yesButton) {
    yesButton.addEventListener('click', async (event) => {
      event.preventDefault();
      event.stopPropagation();
      hideHonestyGate();
      await submitWorkoutCompletion(event);
    });
  }

  if (noButton) {
    noButton.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      hideHonestyGate();
      showRestDayMotivationBanner();
    });
  }
}

function showHonestyGate() {
    console.log('[SHONENFIT] Executing showHonestyGate now...');
    const modal = document.getElementById('honesty-gate-modal');
    const quotesSlot = document.getElementById('honesty-character-quote');

    if (!modal) {
        console.error('[SHONENFIT] HTML structural error: #honesty-gate-modal element does not exist in the DOM!');
        return;
    }

    if (quotesSlot && typeof getHonestyGateQuote === 'function') {
        try {
            quotesSlot.textContent = getHonestyGateQuote();
        } catch (error) {
            console.warn('[SHONENFIT] Failed to load character quote dynamically:', error);
            quotesSlot.textContent = "A true warrior records only facts.";
        }
    }

    if (modal.parentElement !== document.body) {
        document.body.appendChild(modal);
    }

    modal.classList.remove('hidden');
    modal.classList.add('is-active');
    console.log('[SHONENFIT] Clean state class .is-active applied.');
}

function hideHonestyGate() {
  const modal = document.getElementById('honesty-gate-modal');
  if (!modal) {
    return;
  }

  modal.classList.remove('is-active');
  modal.classList.add('hidden');
  modal.setAttribute('aria-hidden', 'true');
}

function getHonestyGateQuote() {
  const characterId = getActiveCharacterId().toLowerCase();
  const quoteMap = {
    toji: "Are you cutting corners? The human body doesn't lie. Did you earn this?",
    inosuke: "DON'T SLACK OFF! Pig rush requires raw sweat! Did you fight hard today?!",
    tengen: "Falsifying records isn't flamboyant at all. Speak the truth, did you complete the set?",
  };

  return quoteMap[characterId] || 'A true warrior records only earned victories. Did you complete the work?';
}

function showRestDayMotivationBanner() {
  let banner = document.getElementById('rest-day-motivation-banner');

  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'rest-day-motivation-banner';
    banner.setAttribute('role', 'status');
    banner.style.cssText = `
      position: fixed;
      left: 50%;
      bottom: 2rem;
      z-index: 10000;
      width: min(92vw, 560px);
      padding: 1rem 1.25rem;
      border: 1px solid rgba(94, 234, 212, 0.58);
      border-radius: 20px;
      background: linear-gradient(135deg, rgba(10, 18, 30, 0.96), rgba(15, 43, 54, 0.94));
      box-shadow: 0 0 34px rgba(45, 212, 191, 0.24), inset 0 0 24px rgba(255, 255, 255, 0.04);
      color: #ecfeff;
      font-weight: 800;
      letter-spacing: 0.02em;
      line-height: 1.5;
      text-align: center;
      transform: translate(-50%, 130%);
      opacity: 0;
      transition: transform 0.28s ease, opacity 0.28s ease;
    `;
    document.body.appendChild(banner);
  }

  banner.innerHTML = `
    <span style="display:block; color:#5eead4; font-size:0.82rem; margin-bottom:0.35rem; text-transform:uppercase;">Rest Day Logged Honestly</span>
    <span>Acknowledging a rest day takes real strength. Fall down seven times, stand up eight. Your training arc resumes tomorrow!</span>
  `;
  window.requestAnimationFrame(() => {
    banner.style.transform = 'translate(-50%, 0)';
    banner.style.opacity = '1';
  });
  window.setTimeout(() => {
    banner.style.transform = 'translate(-50%, 130%)';
    banner.style.opacity = '0';
  }, 6500);
}

async function submitWorkoutCompletion(event) { 
  event?.preventDefault();
  event?.stopPropagation();
  await unlockTimerAudioContext();

  const completionContext = captureWorkoutCompletionContext();
  const completedSets = Number(completionContext?.sets_completed || 0);
  const totalSets = Number(completionContext?.total_sets || 0);

  if (completedSets === 0) {
    alert('Focus, Hero! Log at least one completed set before claiming your EXP.');
    return;
  }

  const payload = {
            character_id: completionContext?.character_id || getActiveCharacterId(),
            sets_completed: completedSets,
            sets: completionContext?.sets || [] // ⚡ THIS IS STEP 2: Bridges the data straight to app.py!
        }; 

  try {
    const response = await fetch(API_WORKOUT_COMPLETE_ENDPOINT, {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok || result?.status !== 'success') {
      console.error('[SHONENFIT] Workout completion sync failed:', result);
      if (response.status === 400) {
        showDailyTrainingCapWarning(result?.message);
        return;
      }

      alert(`Workout completion failed: ${result?.message || `HTTP ${response.status}`}`);
      return;
    }

    // 1. Capture the new EXP from the backend and sync it into our global state
        if (result.new_exp !== undefined) {
            appState.userMetrics.totalExp = result.new_exp;
        }

        // 2. Feed the total EXP to our math module to get the current rank specs
        const progression = calculateGradeProgress(appState.userMetrics.totalExp);
        
        // 3. Fallback check for grades to handle the existing ascension overlays
        const newGrade = progression.grade || result.current_grade || previousGrade;

        if (newGrade !== previousGrade && launchAscensionOverlay(newGrade, completedSets, result)) {
            previousGrade = newGrade;
            return;
        }

        // 4. Fire existing updates
        updateDashboardExpBoost(completedSets, result);
        renderDashboardStreak(result);
        await fetchWorkoutHistory();

        // ⚡ HOOK INTERCEPT: Update dynamic fatigue balance widget on dashboard load
        renderFatigueMetrics(result); 
        // Refresh the rank visual elements and update current tier progress badges
        applyRankBadgeState(progression.grade); 

        // 5. Success cleanup and routing
        alert(`Training Complete! Checked off ${completedSets}/${totalSets} sets. Gained ${result.exp_gained || 250} EXP! Current Tier: ${progression.grade}`);
        previousGrade = newGrade;
        resetRestTimer();
        navigateView('dashboard-view'); 
  } catch (error) {
    console.error('[SHONENFIT] Workout completion network error:', error);
    alert('Could not sync workout completion with the local backend. Make sure app.py is running on http://127.0.0.1:5000.');
  }
}

function showDailyTrainingCapWarning(message) {
  const warningMessage = message || 'Daily training cap reached! Rest and recovery are mandatory parts of a Shonen training arc.';
  let warningCard = document.getElementById('daily-training-cap-warning');

  if (!warningCard) {
    warningCard = document.createElement('div');
    warningCard.id = 'daily-training-cap-warning';
    warningCard.setAttribute('role', 'alert');
    warningCard.style.cssText = `
      position: fixed;
      left: 50%;
      bottom: 2rem;
      z-index: 10000;
      width: min(92vw, 520px);
      padding: 1rem 1.25rem;
      border: 1px solid rgba(255, 59, 92, 0.72);
      border-radius: 18px;
      background: linear-gradient(135deg, rgba(18, 20, 30, 0.96), rgba(70, 10, 22, 0.94));
      box-shadow: 0 0 32px rgba(255, 34, 72, 0.32), inset 0 0 24px rgba(255, 255, 255, 0.04);
      color: #fff;
      font-weight: 800;
      letter-spacing: 0.02em;
      line-height: 1.45;
      text-align: center;
      transform: translate(-50%, 130%);
      opacity: 0;
      transition: transform 0.28s ease, opacity 0.28s ease;
    `;
    document.body.appendChild(warningCard);
  }

  warningCard.innerHTML = `
    <span style="display:block; color:#ff4668; font-size:0.82rem; margin-bottom:0.35rem; text-transform:uppercase;">Recovery Lock Active</span>
    <span>${warningMessage}</span>
  `;
  window.requestAnimationFrame(() => {
    warningCard.style.transform = 'translate(-50%, 0)';
    warningCard.style.opacity = '1';
  });
  window.setTimeout(() => {
    warningCard.style.transform = 'translate(-50%, 130%)';
    warningCard.style.opacity = '0';
  }, 5200);
}

function getActiveCharacterId() {
  const selectedName = appState.selectedCharacter;
  const characters = characterDatabase[appState.selectedUniverse] || [];
  const activeCharacter = characters.find((character) => character.name === selectedName);

  return activeCharacter?.id || selectedName || 'unassigned';
}

function updateDashboardExpBoost(completedSets, progressionData = {}) {
  const statusPill = document.querySelector('#dashboard-view .status-pill');
  const statusNotice = document.querySelector('#dashboard-view .status-notice');
  const summaryBox = document.getElementById('summary-box');
  let standingValue = document.getElementById('standing-value');
  let expValue = document.getElementById('exp-value');
  const currentGrade = progressionData.current_grade || 'Grade 4';
  const totalExp = Number.isFinite(Number(progressionData.total_exp)) ? Number(progressionData.total_exp) : 250;
  const newExp = Number.isFinite(Number(progressionData.new_exp)) ? Number(progressionData.new_exp) : 250;
  const xpToNextLevel = Number.isFinite(Number(progressionData.xp_to_next_level))
    ? Number(progressionData.xp_to_next_level)
    : Math.max(0, 1000 - (totalExp % 1000));

  if (statusPill) {
    statusPill.textContent = `${currentGrade.toUpperCase()} - ${totalExp} EXP`;
  }

  applyRankBadgeState(currentGrade);

  if (statusNotice) {
    statusNotice.textContent = `Training arc logged with ${completedSets} completed sets. ${newExp} EXP claimed. ${xpToNextLevel} EXP to next grade.`;
  }

  if (!standingValue && summaryBox) {
    summaryBox.appendChild(createSummaryItem('Current Standing', 'standing-value', `${currentGrade} - ${totalExp} total EXP`));
    standingValue = document.getElementById('standing-value');
  }

  if (standingValue) {
    standingValue.textContent = `${currentGrade} - ${totalExp} total EXP`;
  }

  if (!expValue && summaryBox) {
    summaryBox.appendChild(createSummaryItem('EXP Claimed', 'exp-value', `+${newExp} EXP / ${xpToNextLevel} to next grade`));
    expValue = document.getElementById('exp-value');
  }

  if (expValue) {
    expValue.textContent = `+${newExp} EXP / ${xpToNextLevel} to next grade`;
  }
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// ============================================================================
// GLOBAL EXPORTS FOR EXISTING INLINE MARKUP
// ============================================================================

window.navigateView = navigateView;
window.MapsToView = MapsToView;
window.selectUniverse = selectUniverse;
window.selectCharacter = selectCharacter;
window.accessWorkout = accessWorkout;
window.toggleSet = toggleSet;
window.toggleRestTimer = toggleRestTimer;

console.log('[SHONENFIT] Live backend application initialized'); 

function renderFatigueMetrics(result) {
    // Locate the container where dashboard metric widgets live
    const dashboardContainer = document.querySelector('#dashboard-view .view-container') || document.querySelector('.view-container');
    if (!dashboardContainer) return;

    // Check if an existing fatigue widget is present; clear it if so to avoid duplicates
    let fatigueCard = document.getElementById('shonenfit-fatigue-card');
    if (!fatigueCard) {
        fatigueCard = document.createElement('div');
        fatigueCard.id = 'shonenfit-fatigue-card';
        // Inserting it cleanly as the first overview metric element
        dashboardContainer.insertBefore(fatigueCard, dashboardContainer.firstChild);
    }

    // Safeguard values from the result object
    const ratio = result.fatigue_ratio !== undefined ? result.fatigue_ratio : 0.0;
    const status = result.fatigue_status || 'Fresh';
    const message = result.fatigue_message || 'Ready for the next training arc.';

    // Dynamic color styling based on the status score
    let neonColor = 'var(--accent-primary, #00ffcc)'; // Default teal
    if (status === 'Warning') neonColor = '#ffcc00';  // Alert yellow
    if (status === 'Danger') neonColor = '#ff3366';   // Danger red

    // Calculate target percentage ahead of time
    const targetPercentage = Math.min(ratio * 100, 100).toFixed(0);

    fatigueCard.innerHTML = `
        <div style="background: rgba(20, 20, 30, 0.85); border: 2px solid ${neonColor}; border-radius: 12px; padding: 16px; margin-bottom: 20px; box-shadow: 0 0 15px rgba(0, 255, 204, 0.25); color: #ffffff; font-family: inherit;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <h4 style="margin: 0; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.05em;">SYSTEM FATIGUE ANALYZER</h4>
                <span style="background: ${neonColor}; color: #000000; font-weight: 800; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; box-shadow: 0 0 10px ${neonColor};">
                    ${status}
                </span>
            </div>
            
            <p style="margin: 0 0 12px 0; font-size: 0.95rem; color: #b3b3cc; line-height: 1.4;">${message}</p>
            
            <div style="background: rgba(255, 255, 255, 0.1); border-radius: 6px; height: 10px; width: 100%; overflow: hidden; position: relative;">
                <!-- ⚡ ANIMATION INITIAL STATE: Started at 0% with custom curve transition -->
                <div id="fatigue-bar-filler" style="background: ${neonColor}; height: 100%; width: 0%; transition: width 1.2s cubic-bezier(0.25, 1, 0.5, 1);"></div>
            </div>
            
            <div style="text-align: right; margin-top: 6px; font-size: 0.8rem; color: #8888aa; font-weight: 600;">
                Calculated Strain Index: ${targetPercentage}%
            </div>
        </div>
    `;

    // ⚡ TRIGGER SURGE EFFECT: Let the DOM paint the 0% state, then slide it out to the target!
    setTimeout(() => {
        const fillerBar = document.getElementById('fatigue-bar-filler');
        if (fillerBar) {
            fillerBar.style.width = `${targetPercentage}%`;
        }
    }, 50);
} 