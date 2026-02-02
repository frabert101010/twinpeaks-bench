// TwinPeaks Bench - Question Explorer JavaScript

let questionsData = [];
let currentMode = 'NO SEARCH';
let models = [];

// Load data when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    extractModels();
    renderTable();
    setupEventListeners();
});

// Load data from JSON
async function loadData() {
    try {
        const response = await fetch('data/detailed.json');
        questionsData = await response.json();
        console.log('Loaded questions:', questionsData.length);
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Extract unique models from data
function extractModels() {
    const modelSet = new Set();
    questionsData.forEach(q => {
        q.responses.forEach(r => {
            if (r.mode === currentMode) {
                modelSet.add(r.model);
            }
        });
    });
    models = Array.from(modelSet).sort();
    console.log('Models:', models);
}

// Render the results table
function renderTable() {
    const table = document.getElementById('results-table');
    table.innerHTML = '';

    // Create header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');

    // Question column
    const questionHeader = document.createElement('th');
    questionHeader.textContent = 'Question';
    headerRow.appendChild(questionHeader);

    // Model columns
    models.forEach(model => {
        const th = document.createElement('th');
        th.textContent = model;
        headerRow.appendChild(th);
    });

    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create body
    const tbody = document.createElement('tbody');

    questionsData.forEach(question => {
        const row = document.createElement('tr');

        // Question cell
        const questionCell = document.createElement('td');
        questionCell.innerHTML = `
            <span class="question-id">${question.id}</span>
            <span class="question-text-cell">${question.question}</span>
        `;
        row.appendChild(questionCell);

        // Model cells
        models.forEach(model => {
            const cell = document.createElement('td');
            const trialsContainer = document.createElement('div');
            trialsContainer.className = 'trials-container';

            // Get responses for this model and mode
            const responses = question.responses.filter(r =>
                r.model === model && r.mode === currentMode
            ).sort((a, b) => a.trial - b.trial);

            // Create boxes for each trial (should be 3)
            responses.forEach(response => {
                const box = document.createElement('div');
                box.className = 'trial-box';
                box.classList.add(response.score === 1 ? 'correct' : 'incorrect');
                box.title = `Trial ${response.trial} - Click to view`;
                box.addEventListener('click', () => showModal(question, response));
                trialsContainer.appendChild(box);
            });

            cell.appendChild(trialsContainer);
            row.appendChild(cell);
        });

        tbody.appendChild(row);
    });

    table.appendChild(tbody);
}

// Show modal with response details
function showModal(question, response) {
    const modal = document.getElementById('response-modal');
    const modalBody = document.getElementById('modal-body');

    const isCorrect = response.score === 1;
    const resultClass = isCorrect ? 'correct' : 'incorrect';
    const resultText = isCorrect ? '✅ Correct' : '❌ Incorrect';

    modalBody.innerHTML = `
        <div class="modal-header">
            <div class="modal-model">
                ${response.model}
                <span class="modal-result ${resultClass}">${resultText}</span>
            </div>
            <div class="modal-question">${question.question}</div>
            <div class="modal-meta">
                ${response.mode} • Trial ${response.trial} • ${question.id}
            </div>
        </div>

        <div class="modal-section">
            <div class="modal-section-title">Expected Answer</div>
            <div class="modal-expected">${question.expected_answer}</div>
        </div>

        <div class="modal-section">
            <div class="modal-section-title">Model's Response</div>
            <div class="modal-response ${resultClass}">${response.response}</div>
        </div>

        ${response.reasoning ? `
            <div class="modal-section">
                <div class="modal-section-title">Judge Reasoning</div>
                <div class="modal-reasoning">${response.reasoning}</div>
            </div>
        ` : ''}
    `;

    modal.classList.add('show');
}

// Setup event listeners
function setupEventListeners() {
    // Mode toggle
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            extractModels();
            renderTable();
        });
    });

    // Modal close
    const modal = document.getElementById('response-modal');
    const closeBtn = document.querySelector('.modal-close');

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            modal.classList.remove('show');
        }
    });
}
