/* ============================================================================
   SHONENFIT - Application Logic
   ============================================================================ */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const API_PROFILE_ENDPOINT = 'http://127.0.0.1:5000/api/profile';
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

const appState = {
  selectedUniverse: null,
  selectedCharacter: null,
  selectedDirection: null,
  latestWorkoutData: null,
  isSubmitting: false,
  userMetrics: {
    age: null,
    height: null,
    weight: null,
    medicalHistory: null,
    preferences: null,
  },
};

const userSessionProfile = appState;
window.userSessionProfile = userSessionProfile;

let timerRunning = false;
let timerInterval = null;
let timeRemaining = TIMER_TOTAL_SECONDS;
let audioContext = null;

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

// ============================================================================
// BOOTSTRAP
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  installGlobalNavigationInterception();
  applyUniverseCardGraphics();
  wireMetricsSubmission();
  wireWorkoutRouteButton();
  wireWorkoutControlButtons();
  ensureWorkoutRuntimeStyles();
  bindSetTrackingSelectors();
  initializeTimerDisplay();
  fetchWorkoutHistory();
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
  navigateView('form-view');
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
    renderDashboardStreak(result);
    if (!didRenderDashboard) {
      console.error('[SHONENFIT] Dashboard render target was not available. View transition cancelled.');
      alert('Workout data was generated, but the dashboard container could not be found.');
      return;
    }

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
    item.textContent = `${exercise.name} - ${exercise.sets || 4} sets x ${exercise.reps || 'controlled reps'}`;
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

    for (let setIndex = 1; setIndex <= 4; setIndex += 1) {
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
  const completeButton = Array.from(document.querySelectorAll('#workout-active-view button'))
    .find((button) => button.textContent.trim() === 'COMPLETED TRAINING ARC (CLAIM EXP)');
  const backButton = Array.from(document.querySelectorAll('#workout-active-view button'))
    .find((button) => button.textContent.includes('Back to Dashboard'));

  if (timerButton) {
    timerButton.removeAttribute('onclick');
    timerButton.textContent = 'Start Rest / Resume Timer';
    timerButton.addEventListener('click', toggleRestTimer);
  }

  if (completeButton) {
    completeButton.removeAttribute('onclick');
    completeButton.addEventListener('click', completeWorkout);
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

// ============================================================================
// MISSION COMPLETION
// ============================================================================

async function completeWorkout(event) {
  event?.preventDefault();
  event?.stopPropagation();

  const completedSets = document.querySelectorAll(
    '#exercise-cards-container .set-btn.active, #exercise-cards-container .set-button.active, #exercise-cards-container .set-btn.completed, #exercise-cards-container .set-button.completed',
  ).length;

  if (completedSets === 0) {
    alert('Focus, Hero! Log at least one completed set before claiming your EXP.');
    return;
  }

  const payload = {
    character_id: getActiveCharacterId(),
    sets_completed: completedSets,
  };

  try {
    const response = await fetch(API_WORKOUT_COMPLETE_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok || result?.status !== 'success') {
      console.error('[SHONENFIT] Workout completion sync failed:', result);
      alert(`Workout completion failed: ${result?.message || `HTTP ${response.status}`}`);
      return;
    }

    updateDashboardExpBoost(completedSets, result);
    renderDashboardStreak(result);
    await fetchWorkoutHistory();
    alert(`Training Complete! Checked off ${completedSets} sets. ${result.new_exp} EXP claimed toward Grade 3 Ascension.`);
    resetRestTimer();
    navigateView('dashboard-view');
  } catch (error) {
    console.error('[SHONENFIT] Workout completion network error:', error);
    alert('Could not sync workout completion with the local backend. Make sure app.py is running on http://127.0.0.1:5000.');
  }
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
window.completeWorkout = completeWorkout;

console.log('[SHONENFIT] Live backend application initialized');
