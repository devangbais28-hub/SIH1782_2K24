document.addEventListener('DOMContentLoaded', () => {
  const verifyForm = document.getElementById('verifyForm');
  const submitForm = document.getElementById('submitForm');

  // Verify Form Handler
  if (verifyForm) {
    verifyForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const title = document.getElementById('title').value.trim();
      const domain = document.getElementById('domain').value.trim();
      const language = document.getElementById('language').value.trim();
      const description = document.getElementById('description').value.trim();

      if (!title) return;

      setLoading(true);

      try {
        const response = await fetch('/api/verify', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title,
            domain,
            language,
            description: description || null
          })
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Verification failed');
        }

        const data = await response.json();
        renderResults(data);
      } catch (err) {
        alert(`Error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    });
  }

  // Submit Form Handler
  if (submitForm) {
    submitForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const title = document.getElementById('subTitle').value.trim();
      const domain = document.getElementById('subDomain').value.trim();
      const language = document.getElementById('subLanguage').value.trim();
      const contact_info = document.getElementById('subContact').value.trim();
      const description = document.getElementById('subDescription').value.trim();

      if (!title) return;

      try {
        const response = await fetch('/api/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title,
            domain,
            language,
            contact_info: contact_info || null,
            description: description || null
          })
        });

        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || 'Submission failed');
        }

        const data = await response.json();
        renderSubmissionResult(data);
      } catch (err) {
        alert(`Submission Error: ${err.message}`);
      }
    });
  }
});

function setLoading(isLoading) {
  const btnSpinner = document.getElementById('btnSpinner');
  const btnText = document.getElementById('btnText');
  const verifyBtn = document.getElementById('verifyBtn');

  if (!verifyBtn) return;

  if (isLoading) {
    verifyBtn.disabled = true;
    btnSpinner.classList.remove('hidden');
    btnText.textContent = 'Screening Title...';
  } else {
    verifyBtn.disabled = false;
    btnSpinner.classList.add('hidden');
    btnText.textContent = 'Screen Publication Title';
  }
}

function renderResults(data) {
  const placeholder = document.getElementById('resultsPlaceholder');
  const content = document.getElementById('resultsContent');
  const decisionCard = document.getElementById('decisionCard');
  const decisionBadge = document.getElementById('decisionBadge');
  const finalScore = document.getElementById('finalScore');
  const explanationText = document.getElementById('explanationText');
  const semanticScore = document.getElementById('semanticScore');
  const lexicalScore = document.getElementById('lexicalScore');
  const phoneticScore = document.getElementById('phoneticScore');
  const reasonsList = document.getElementById('reasonsList');
  const matchesList = document.getElementById('matchesList');

  placeholder.classList.add('hidden');
  content.classList.remove('hidden');

  decisionBadge.textContent = data.decision;
  finalScore.textContent = data.final_score.toFixed(2);
  explanationText.textContent = data.explanation;

  semanticScore.textContent = data.score_breakdown.semantic_score.toFixed(2);
  lexicalScore.textContent = data.score_breakdown.lexical_score.toFixed(2);
  phoneticScore.textContent = data.score_breakdown.phonetic_score !== null ? data.score_breakdown.phonetic_score.toFixed(2) : 'N/A';

  // Badge Styling based on Risk / Decision
  decisionCard.className = 'rounded-2xl p-6 border shadow-xl transition-all ';
  if (data.decision === 'POTENTIAL_CONFLICT') {
    decisionCard.classList.add('bg-rose-950/30', 'border-rose-500/40');
    decisionBadge.className = 'text-xl font-extrabold tracking-tight mt-0.5 text-rose-400';
  } else if (data.decision === 'REVIEW_REQUIRED') {
    decisionCard.classList.add('bg-amber-950/30', 'border-amber-500/40');
    decisionBadge.className = 'text-xl font-extrabold tracking-tight mt-0.5 text-amber-400';
  } else {
    decisionCard.classList.add('bg-emerald-950/30', 'border-emerald-500/40');
    decisionBadge.className = 'text-xl font-extrabold tracking-tight mt-0.5 text-emerald-400';
  }

  // Render Reasons
  reasonsList.innerHTML = '';
  data.reasons.forEach(reason => {
    const li = document.createElement('li');
    li.className = 'flex items-center space-x-2 text-slate-300';
    li.innerHTML = `
      <svg class="w-4 h-4 text-indigo-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
      <span>${reason}</span>
    `;
    reasonsList.appendChild(li);
  });

  // Render Matches
  matchesList.innerHTML = '';
  data.top_matches.forEach(match => {
    const div = document.createElement('div');
    div.className = 'p-3.5 rounded-xl bg-slate-900/80 border border-slate-700/60 flex items-center justify-between text-xs hover:border-slate-600 transition';
    div.innerHTML = `
      <div class="space-y-1 max-w-[75%]">
        <div class="font-bold text-white text-sm">${match.title}</div>
        <div class="flex items-center space-x-2 text-slate-400 text-[11px]">
          <span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">${match.domain}</span>
          <span>${match.language}</span>
        </div>
      </div>
      <div class="text-right font-mono">
        <div class="text-sm font-extrabold text-indigo-300">${match.final_score.toFixed(2)}</div>
        <div class="text-[10px] text-slate-500">score</div>
      </div>
    `;
    matchesList.appendChild(div);
  });
}

function renderSubmissionResult(data) {
  const container = document.getElementById('submissionOutcome');
  const statusBadge = document.getElementById('subStatusBadge');
  const subId = document.getElementById('subId');
  const subDecision = document.getElementById('subDecision');
  const subExplanation = document.getElementById('subExplanation');

  container.classList.remove('hidden');
  subId.textContent = `#${data.submission_id}`;
  subDecision.textContent = data.verification_result.decision;
  subExplanation.textContent = data.verification_result.explanation;

  statusBadge.textContent = data.record_status;
  if (data.record_status === 'approved') {
    statusBadge.className = 'text-xs px-3 py-1 rounded-full font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
  } else if (data.record_status === 'pending') {
    statusBadge.className = 'text-xs px-3 py-1 rounded-full font-bold uppercase bg-amber-500/20 text-amber-400 border border-amber-500/30';
  } else {
    statusBadge.className = 'text-xs px-3 py-1 rounded-full font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30';
  }
}
