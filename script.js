/* ============================================================================
   SHONENFIT - Application Logic
   ============================================================================ */

// ============================================================================
// STATE MANAGEMENT
// ============================================================================

const API_PROFILE_ENDPOINT = 'http://127.0.0.1:5000/api/profile';
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
  'Jujutsu Kaisen': [
    { id: 1, name: 'Yuji Itadori', focus: 'All-around Strength', tier: 'Special Grade' },
    { id: 2, name: 'Megumi Fushiguro', focus: 'Tactical Power', tier: 'Grade 1' },
    { id: 3, name: 'Nobara Kugisaki', focus: 'Explosive Speed', tier: 'Grade 1' },
    { id: 4, name: 'Gojo Satoru', focus: 'Peak Performance', tier: 'Special Grade' },
  ],
  'Demon Slayer': [
    { id: 5, name: 'Tanjiro Kamado', focus: 'Endurance Build', tier: 'Hashira' },
    { id: 6, name: 'Inosuke Hashibira', focus: 'Explosive Power', tier: 'Hashira' },
    { id: 7, name: 'Zenitsu Agatsuma', focus: 'Speed & Reflexes', tier: 'Hashira' },
    { id: 8, name: 'Giyu Tomioka', focus: 'Composed Strength', tier: 'Hashira' },
  ],
  'My Hero Academia': [
    { id: 9, name: 'Izuku Midoriya', focus: 'Power Control', tier: 'Pro Hero' },
    { id: 10, name: 'Bakugo Katsuki', focus: 'Aggressive Dominance', tier: 'Pro Hero' },
    { id: 11, name: 'Todoroki Shoto', focus: 'Balanced Mastery', tier: 'Pro Hero' },
    { id: 12, name: 'All Might', focus: 'Peak Heroism', tier: 'Legend' },
  ],
};

// ============================================================================
// BOOTSTRAP
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  installGlobalNavigationInterception();
  wireMetricsSubmission();
  wireWorkoutRouteButton();
  wireWorkoutControlButtons();
  ensureWorkoutRuntimeStyles();
  initializeTimerDisplay();
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
  appState.selectedUniverse = universeName;
  populateCharacterPool(universeName);
  navigateView('character-view');
}

function populateCharacterPool(universeName) {
  const pool = document.getElementById('character-pool');
  const characters = characterDatabase[universeName] || [];

  if (!pool) {
    return;
  }

  pool.innerHTML = '';

  characters.forEach((character) => {
    const card = document.createElement('div');
    card.className = 'character-card';
    card.innerHTML = `
      <h4 style="color: var(--text-primary); margin: 0 0 0.5rem 0;">${character.name}</h4>
      <p style="color: var(--accent-primary); font-weight: 700; font-size: 0.9rem; margin: 0 0 0.5rem 0;">${character.tier}</p>
      <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">${character.focus}</p>
    `;
    card.addEventListener('click', () => selectCharacter(character.name, universeName));
    pool.appendChild(card);
  });
}

function selectCharacter(characterName, universeName) {
  appState.selectedCharacter = characterName;
  appState.selectedUniverse = universeName || appState.selectedUniverse;
  navigateView('form-view');
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
      setButton.className = 'set-button';
      setButton.textContent = `Set ${setIndex}`;
      setButton.dataset.exerciseIndex = String(index);
      setButton.dataset.set = String(setIndex);
      setButton.setAttribute('aria-pressed', 'false');
      setButton.addEventListener('click', () => toggleSet(setButton));
      setButtons.appendChild(setButton);
    }

    card.append(title, meta, setButtons);
    container.appendChild(card);
  });
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

function ensureWorkoutRuntimeStyles() {
  if (document.getElementById('workout-runtime-styles')) {
    return;
  }

  const style = document.createElement('style');
  style.id = 'workout-runtime-styles';
  style.textContent = `
    #exercise-cards-container .set-button.active {
      background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
      border-color: var(--accent-primary);
      color: var(--bg-primary);
      font-weight: 800;
      box-shadow: 0 0 20px rgba(255, 42, 81, 0.5);
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

function toggleRestTimer() {
  prepareAudioContext();

  if (timeRemaining <= 0) {
    resetRestTimer();
  }

  if (timerRunning) {
    pauseRestTimer();
    return;
  }

  timerRunning = true;
  updateTimerButton('Pause Rest Timer');

  timerInterval = window.setInterval(() => {
    timeRemaining = Math.max(0, timeRemaining - 1);
    renderTimer();

    if (timeRemaining === 0) {
      pauseRestTimer();
      updateTimerButton('Rest Complete / Restart Timer');
      playTimerCompleteCue();
    }
  }, 1000);
}

function pauseRestTimer() {
  if (timerInterval) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }

  timerRunning = false;

  if (timeRemaining > 0) {
    updateTimerButton(timeRemaining === TIMER_TOTAL_SECONDS ? 'Start Rest / Resume Timer' : 'Resume Timer');
  }
}

function resetRestTimer() {
  pauseRestTimer();
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
  if (!audioContext) {
    return;
  }

  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }

  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  const now = audioContext.currentTime;

  oscillator.type = 'sine';
  oscillator.frequency.setValueAtTime(660, now);
  oscillator.frequency.setValueAtTime(880, now + 0.16);

  gain.gain.setValueAtTime(0.0001, now);
  gain.gain.exponentialRampToValueAtTime(0.22, now + 0.02);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.42);

  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  oscillator.start(now);
  oscillator.stop(now + 0.45);
}

// ============================================================================
// MISSION COMPLETION
// ============================================================================

function completeWorkout(event) {
  event?.preventDefault();

  const completedSets = document.querySelectorAll('#exercise-cards-container .set-button.active').length;
  const totalSets = document.querySelectorAll('#exercise-cards-container .set-button').length;
  const completedExercises = Array.from(document.querySelectorAll('#exercise-cards-container .exercise-card'))
    .filter((card) => card.querySelectorAll('.set-button.active').length === 4).length;
  const totalExercises = document.querySelectorAll('#exercise-cards-container .exercise-card').length;
  const workoutData = appState.latestWorkoutData || {};
  const metrics = appState.userMetrics;
  const elapsedRestSeconds = TIMER_TOTAL_SECONDS - timeRemaining;
  const restLabel = elapsedRestSeconds > 0 ? formatTime(elapsedRestSeconds) : 'No rest timer used';

  const summary = [
    `Training arc complete for ${workoutData.character_alignment || appState.selectedCharacter || 'Unassigned Warrior'}.`,
    '',
    `Focus: ${workoutData.core_focus_directive || 'Live Training Protocol'}`,
    `Strategy: ${formatStrategyLabel(workoutData.strategy_paradigm || appState.selectedDirection || 'train-like')}`,
    `Exercises Completed: ${completedExercises}/${totalExercises}`,
    `Sets Logged: ${completedSets}/${totalSets}`,
    `Rest Timer Logged: ${restLabel}`,
    `Biometrics: ${metrics.age || '--'} yrs, ${metrics.height || '--'} cm, ${metrics.weight || '--'} kg`,
    '',
    'Claim 250 EXP and return to dashboard?',
  ].join('\n');

  window.confirm(summary);
  resetRestTimer();
  navigateView('dashboard-view');
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
