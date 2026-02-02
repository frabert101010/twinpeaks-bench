// TwinPeaks Bench - Question Explorer JavaScript

let questionsData = [];
let filteredQuestions = [];
let currentQuestionIndex = 0;

// Current filter state
let filters = {
    mode: 'all',
    model: 'all',
    difficulty: 'all',
    result: 'all'
};

// Load data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    populateModelFilter();
    applyFilters();
    renderQuestion();
    setupEventListeners();
});

// Load data from JSON
async function loadData() {
    try {
        const response = await fetch('data/detailed.json');
        questionsData = await response.json();
    } catch (error) {
        console.error('Error loading data:', error);
        showEmptyState('Failed to load questions data');
    }
}

// Populate model filter dropdown with available models
function populateModelFilter() {
    const modelFilter = document.getElementById('model-filter');
    const models = new Set();

    questionsData.forEach(q => {
        q.responses.forEach(r => models.add(r.model));
    });

    Array.from(models).sort().forEach(model => {
        const option = document.createElement('option');
        option.value = model;
        option.textContent = model;
        modelFilter.appendChild(option);
    });
}

// Apply all filters to questions
function applyFilters() {
    filteredQuestions = questionsData.filter(question => {
        // Filter by difficulty
        if (filters.difficulty !== 'all' && question.difficulty !== parseInt(filters.difficulty)) {
            return false;
        }

        // Filter by mode and model and result
        if (filters.mode !== 'all' || filters.model !== 'all' || filters.result !== 'all') {
            const relevantResponses = question.responses.filter(r => {
                if (filters.mode !== 'all' && r.mode !== filters.mode) return false;
                if (filters.model !== 'all' && r.model !== filters.model) return false;
                if (filters.result !== 'all') {
                    const isCorrect = r.is_correct === true || r.is_correct === 'True';
                    if (filters.result === 'correct' && !isCorrect) return false;
                    if (filters.result === 'incorrect' && isCorrect) return false;
                }
                return true;
            });

            // Only include question if it has matching responses
            if (relevantResponses.length === 0) return false;
        }

        return true;
    });

    // Reset to first question
    currentQuestionIndex = 0;
    updateNavigation();
}

// Render current question
function renderQuestion() {
    const display = document.getElementById('question-display');

    if (filteredQuestions.length === 0) {
        showEmptyState('No questions match your filters');
        return;
    }

    const question = filteredQuestions[currentQuestionIndex];

    // Build difficulty stars
    const stars = '⭐'.repeat(question.difficulty);

    // Build question header
    const headerHTML = `
        <div class="question-header">
            <div class="question-id">${question.question_id}</div>
            <div class="question-text">${question.question}</div>
            <div class="question-meta">
                <div class="meta-item">
                    <span class="difficulty-stars">${stars}</span>
                    <span>${getDifficultyLabel(question.difficulty)}</span>
                </div>
                <div class="meta-item">
                    <strong>Accuracy:</strong> ${question.accuracy.toFixed(1)}%
                </div>
            </div>
        </div>
    `;

    // Build expected answer
    const expectedHTML = `
        <div class="expected-answer">
            <div class="expected-answer-label">Expected Answer</div>
            <div class="expected-answer-text">${question.expected_answer}</div>
        </div>
    `;

    // Filter responses based on current filters
    let responses = question.responses;
    if (filters.mode !== 'all') {
        responses = responses.filter(r => r.mode === filters.mode);
    }
    if (filters.model !== 'all') {
        responses = responses.filter(r => r.model === filters.model);
    }
    if (filters.result !== 'all') {
        responses = responses.filter(r => {
            const isCorrect = r.is_correct === true || r.is_correct === 'True';
            return filters.result === 'correct' ? isCorrect : !isCorrect;
        });
    }

    // Build responses
    const responsesHTML = responses.length > 0 ? `
        <div class="responses-section">
            <h3 class="responses-header">Model Responses (${responses.length})</h3>
            ${responses.map((r, idx) => renderResponse(r, idx)).join('')}
        </div>
    ` : `
        <div class="responses-section">
            <h3 class="responses-header">Model Responses</h3>
            <div class="empty-state">
                <div class="empty-state-icon">🤷</div>
                <div class="empty-state-text">No responses match your filters</div>
            </div>
        </div>
    `;

    display.innerHTML = headerHTML + expectedHTML + responsesHTML;

    // Add event listeners for toggle buttons
    document.querySelectorAll('.response-toggle').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const responseId = e.target.dataset.response;
            toggleResponse(responseId);
        });
    });
}

// Render a single response
function renderResponse(response, index) {
    const isCorrect = response.is_correct === true || response.is_correct === 'True';
    const correctClass = isCorrect ? 'correct' : 'incorrect';
    const resultEmoji = isCorrect ? '✅' : '❌';

    const responseId = `response-${index}`;
    const shortText = response.answer.length > 200
        ? response.answer.substring(0, 200) + '...'
        : response.answer;

    return `
        <div class="response-card ${correctClass}">
            <div class="response-header">
                <div class="response-model">
                    <span class="model-label">${response.model}</span>
                    <span class="mode-badge">${response.mode}</span>
                </div>
                <div class="response-result">${resultEmoji}</div>
            </div>

            <div class="response-text" id="${responseId}">
                ${shortText}
            </div>

            ${response.answer.length > 200 ? `
                <button class="response-toggle" data-response="${responseId}">
                    Show full answer
                </button>
            ` : ''}

            ${response.judge_reasoning ? `
                <div class="response-meta">
                    <div class="response-meta-item">
                        <strong>Judge:</strong> ${response.judge_reasoning}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// Toggle full response text
function toggleResponse(responseId) {
    const element = document.getElementById(responseId);
    const btn = document.querySelector(`[data-response="${responseId}"]`);
    const question = filteredQuestions[currentQuestionIndex];

    // Find the response
    const index = parseInt(responseId.split('-')[1]);
    let responses = question.responses;
    if (filters.mode !== 'all') responses = responses.filter(r => r.mode === filters.mode);
    if (filters.model !== 'all') responses = responses.filter(r => r.model === filters.model);
    if (filters.result !== 'all') {
        responses = responses.filter(r => {
            const isCorrect = r.is_correct === true || r.is_correct === 'True';
            return filters.result === 'correct' ? isCorrect : !isCorrect;
        });
    }
    const response = responses[index];

    if (btn.textContent === 'Show full answer') {
        element.textContent = response.answer;
        btn.textContent = 'Show less';
    } else {
        const shortText = response.answer.substring(0, 200) + '...';
        element.textContent = shortText;
        btn.textContent = 'Show full answer';
    }
}

// Show empty state
function showEmptyState(message) {
    const display = document.getElementById('question-display');
    display.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">🔍</div>
            <div class="empty-state-text">${message}</div>
        </div>
    `;
}

// Get difficulty label
function getDifficultyLabel(difficulty) {
    const labels = {
        1: 'Very Easy',
        2: 'Easy',
        3: 'Medium',
        4: 'Hard',
        5: 'Very Hard'
    };
    return labels[difficulty] || 'Unknown';
}

// Update navigation buttons and counter
function updateNavigation() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const counter = document.getElementById('question-counter');

    prevBtn.disabled = currentQuestionIndex === 0;
    nextBtn.disabled = currentQuestionIndex === filteredQuestions.length - 1;

    if (filteredQuestions.length > 0) {
        counter.textContent = `Question ${currentQuestionIndex + 1} of ${filteredQuestions.length}`;
    } else {
        counter.textContent = 'No questions found';
    }
}

// Navigate to previous question
function previousQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        renderQuestion();
        updateNavigation();
    }
}

// Navigate to next question
function nextQuestion() {
    if (currentQuestionIndex < filteredQuestions.length - 1) {
        currentQuestionIndex++;
        renderQuestion();
        updateNavigation();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation buttons
    document.getElementById('prev-btn').addEventListener('click', previousQuestion);
    document.getElementById('next-btn').addEventListener('click', nextQuestion);

    // Filter changes
    document.getElementById('mode-filter').addEventListener('change', (e) => {
        filters.mode = e.target.value;
        applyFilters();
        renderQuestion();
    });

    document.getElementById('model-filter').addEventListener('change', (e) => {
        filters.model = e.target.value;
        applyFilters();
        renderQuestion();
    });

    document.getElementById('difficulty-filter').addEventListener('change', (e) => {
        filters.difficulty = e.target.value;
        applyFilters();
        renderQuestion();
    });

    document.getElementById('result-filter').addEventListener('change', (e) => {
        filters.result = e.target.value;
        applyFilters();
        renderQuestion();
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') previousQuestion();
        if (e.key === 'ArrowRight') nextQuestion();
    });
}
