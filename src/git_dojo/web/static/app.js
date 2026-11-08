/**
 * Nexus Ops Cockpit — Interactive Frontend Application
 */

let state = {
  activeTab: "flight-deck",
  scenarios: [],
  activeScenarioId: null,
  prs: [],
  activePrId: null,
  health: null,
  escalations: [],
};

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  fetchScenarios();
  fetchPrs();
  fetchRepoStatus();
  fetchCommits();
  setInterval(fetchRepoStatus, 6000); // Poll status every 6s
});

// Tab Switcher
function initTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".view-panel").forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const tabId = btn.getAttribute("data-tab");
      const panel = document.getElementById(tabId);
      if (panel) panel.classList.add("active");
      state.activeTab = tabId;

      if (tabId === "code-commits") fetchCommits();
      if (tabId === "forensics-radar") fetchRepoStatus();
    });
  });
}

// ----------------------------------------------------------------------------
// 1. SCENARIOS (FLIGHT DECK)
// ----------------------------------------------------------------------------
async function fetchScenarios() {
  try {
    const res = await fetch("/api/scenarios");
    const data = await res.json();
    state.scenarios = data.scenarios;
    state.activeScenarioId = data.active_level;

    document.getElementById("nav-active-scenario").textContent = data.active_level || "None";
    document.getElementById("nav-progress-val").textContent = `${data.total_completed}/${data.total_levels} (${Math.round((data.total_completed/data.total_levels)*100)}%)`;

    renderScenariosGrid();
    renderActiveScenarioBanner();
  } catch (err) {
    console.error("Failed to fetch scenarios:", err);
  }
}

function renderScenariosGrid() {
  const container = document.getElementById("scenarios-list");
  container.innerHTML = "";

  state.scenarios.forEach((sc) => {
    const card = document.createElement("div");
    card.className = `scenario-card ${sc.id === state.activeScenarioId ? "active-scenario" : ""}`;

    const badgeClass = sc.completed ? "badge-completed" : "badge-pending";
    const statusText = sc.completed ? "COMPLETED" : "NOT STARTED";

    card.innerHTML = `
      <div>
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
          <span style="font-size:12px; color:var(--text-secondary); font-weight:600;">LEVEL ${String(sc.number).padStart(2, '0')} • ${sc.category}</span>
          <span class="scenario-badge ${badgeClass}">${statusText}</span>
        </div>
        <h4 style="color:var(--text-white); margin-bottom:8px; font-size:15px;">${sc.title}</h4>
        <p style="font-size:12px; color:var(--text-secondary); margin-bottom:12px;">${sc.description.substring(0, 140)}...</p>
        <div style="font-size:11px; color:var(--text-secondary); margin-bottom:16px;">
          <span>⏱ Diff: <strong>${sc.difficulty}</strong></span> | <span>Est: ${sc.estimated_time}</span>
          ${sc.best_recovery_time ? `| <span>Best: <strong>${sc.best_recovery_time}s</strong></span>` : ''}
        </div>
      </div>
      <div style="display:flex; gap:8px;">
        <button class="btn btn-primary" style="flex:1" onclick="launchScenario('${sc.id}')">Launch</button>
        <button class="btn" onclick="showScenarioModal('${sc.id}')">Details</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderActiveScenarioBanner() {
  const container = document.getElementById("active-scenario-detail");
  if (!state.activeScenarioId) {
    container.innerHTML = `<p>No scenario currently active. Select any of the 30 challenges below to deploy its failure state into your playground repository.</p>`;
    return;
  }
  const sc = state.scenarios.find((s) => s.id === state.activeScenarioId);
  if (!sc) return;

  container.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
      <div>
        <h3 style="color:var(--accent-blue); margin-bottom:4px;">Level ${sc.number}: ${sc.title}</h3>
        <p style="margin-bottom:8px;"><strong>Scenario:</strong> ${sc.description}</p>
        <p style="margin-bottom:4px; font-size:12px;"><strong>Expected Invariant:</strong> ${sc.expected_outcome}</p>
      </div>
      <button class="btn" onclick="revealHint('${sc.id}')">💡 Get Hint</button>
    </div>
  `;
}

async function launchScenario(levelId) {
  try {
    const res = await fetch(`/api/scenarios/${levelId}/launch`, { method: "POST" });
    const data = await res.json();
    alert(`[✓] ${data.message}\n\nWorking repository: .git_dojo/playground/nexus-platform`);
    fetchScenarios();
    fetchRepoStatus();
  } catch (err) {
    alert("Failed to launch scenario: " + err);
  }
}

async function verifyActiveScenario() {
  if (!state.activeScenarioId) {
    alert("No active scenario loaded.");
    return;
  }
  const banner = document.getElementById("verification-banner");
  banner.style.display = "block";
  banner.innerHTML = `<div style="padding:12px; background:var(--bg-tertiary); border-radius:6px;">[*] Running automated verification test suite...</div>`;

  try {
    const res = await fetch(`/api/scenarios/${state.activeScenarioId}/verify`, { method: "POST" });
    const data = await res.json();

    if (data.success) {
      banner.innerHTML = `
        <div style="padding:12px; background:#23863633; border:1px solid #238636; border-radius:6px; color:#3fb950;">
          <strong>✔ VERIFICATION PASSED!</strong><br>${data.message}
        </div>
      `;
    } else {
      banner.innerHTML = `
        <div style="padding:12px; background:#da363333; border:1px solid #da3633; border-radius:6px; color:#f85149;">
          <strong>✗ VERIFICATION FAILED</strong><br>${data.message}
        </div>
      `;
    }
    fetchScenarios();
  } catch (err) {
    banner.innerHTML = `<div style="color:red">Verification error: ${err}</div>`;
  }
}

async function resetActiveScenario() {
  if (!state.activeScenarioId) return;
  if (!confirm("Are you sure you want to reset this scenario? Working tree changes will be wiped.")) return;

  try {
    const res = await fetch(`/api/scenarios/${state.activeScenarioId}/reset`, { method: "POST" });
    const data = await res.json();
    alert(data.message);
    fetchScenarios();
    fetchRepoStatus();
  } catch (err) {
    alert("Reset failed: " + err);
  }
}

function revealHint(levelId) {
  const sc = state.scenarios.find((s) => s.id === levelId);
  if (sc && sc.hints.length) {
    alert("💡 HINTS:\n\n" + sc.hints.map((h, i) => `${i+1}. ${h}`).join("\n\n"));
  }
}

function showScenarioModal(levelId) {
  const sc = state.scenarios.find((s) => s.id === levelId);
  if (!sc) return;
  alert(`LEVEL ${sc.number}: ${sc.title}\n\n${sc.description}\n\nExpected Outcome:\n${sc.expected_outcome}`);
}

// ----------------------------------------------------------------------------
// 2. PULL REQUESTS SIMULATION (NEXUSHUB)
// ----------------------------------------------------------------------------
async function fetchPrs() {
  try {
    const res = await fetch("/api/prs");
    const data = await res.json();
    state.prs = data.prs;
    document.getElementById("badge-pr-count").textContent = data.prs.filter(p => p.state === "open").length;
    renderPrList();
  } catch (err) {
    console.error("Failed to fetch PRs:", err);
  }
}

function renderPrList() {
  const container = document.getElementById("pr-items-container");
  container.innerHTML = "";

  state.prs.forEach((pr) => {
    const item = document.createElement("div");
    item.className = "pr-item";
    item.onclick = () => openPrDetail(pr.id);

    const iconColor = pr.has_conflicts ? "conflict" : "";
    const conflictBadge = pr.has_conflicts ? `<span style="background:#da363326; color:#f85149; border:1px solid #da3633; padding:2px 6px; border-radius:10px; font-size:11px; margin-left:8px;">Has Conflicts</span>` : "";

    item.innerHTML = `
      <div class="pr-icon ${iconColor}">🔀</div>
      <div style="flex:1;">
        <div class="pr-title">
          ${pr.title}
          ${conflictBadge}
        </div>
        <div class="pr-meta">
          #${pr.id} opened by <strong>${pr.author_name}</strong> (${pr.team_id}) • Branch: <code>${pr.branch}</code> → <code>${pr.base_branch}</code> • ${pr.comments.length} comments
        </div>
      </div>
      <div>
        <span class="badge" style="background:${pr.ci_status === 'success' ? '#23863626' : '#da363326'}; color:${pr.ci_status === 'success' ? '#3fb950' : '#f85149'};">
          CI: ${pr.ci_status.toUpperCase()}
        </span>
      </div>
    `;
    container.appendChild(item);
  });
}

function openPrDetail(prId) {
  state.activePrId = prId;
  const pr = state.prs.find((p) => p.id === prId);
  if (!pr) return;

  document.getElementById("pr-list-view").style.display = "none";
  document.getElementById("pr-detail-view").style.display = "block";

  const content = document.getElementById("pr-detail-content");

  const conflictAlert = pr.has_conflicts ? `
    <div class="conflict-alert">
      <strong>⚠️ Merge Conflict Detected:</strong> This branch has conflicts with '${pr.base_branch}' in <code>${pr.conflicted_files.join(', ')}</code>.
      Resolve conflicts in your terminal or via rebase before merging.
    </div>
  ` : "";

  content.innerHTML = `
    <div class="card" style="margin-bottom:16px;">
      <div class="card-header">
        <div>
          <h2>${pr.title} <span style="color:var(--text-secondary)">#${pr.id}</span></h2>
          <div style="font-size:12px; color:var(--text-secondary); margin-top:4px;">
            <span class="badge" style="background:#1f6feb26; color:var(--accent-blue)">OPEN</span>
            ${pr.author_name} wants to merge ${pr.commits_count} commits into <code>${pr.base_branch}</code> from <code>${pr.branch}</code>
          </div>
        </div>
      </div>
      <div class="card-body">
        ${conflictAlert}
        <p style="margin-bottom:16px;">${pr.description}</p>
        <h4 style="margin-bottom:8px;">Files Changed (${pr.files_changed.length})</h4>
        <ul style="margin-left:20px; font-family:var(--font-mono); font-size:13px; margin-bottom:20px;">
          ${pr.files_changed.map(f => `<li>${f}</li>`).join('')}
        </ul>

        <!-- MERGE ACTION BOX -->
        <div style="background:var(--bg-tertiary); padding:16px; border-radius:6px; border:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
          <div>
            <strong>Merge status:</strong>
            ${pr.has_conflicts ? '<span style="color:#f85149">Blocked by merge conflicts</span>' : '<span style="color:#3fb950">Ready to merge</span>'}
          </div>
          <div style="display:flex; gap:8px;">
            <select id="merge-strategy-select" style="background:var(--bg-secondary); color:white; border:1px solid var(--border-color); border-radius:4px; padding:6px;">
              <option value="merge">Create a merge commit (--no-ff)</option>
              <option value="squash">Squash and merge</option>
              <option value="rebase">Rebase and merge</option>
            </select>
            <button class="btn btn-primary" onclick="mergeActivePr()">Merge Pull Request</button>
          </div>
        </div>
      </div>
    </div>

    <!-- CODE REVIEW & COMMENTS -->
    <h3 style="margin-bottom:16px;">Review Discussions</h3>
    <div id="pr-comments-list">
      ${pr.comments.map(c => `
        <div class="comment-box">
          <div class="comment-head">
            <div>
              <strong>${c.author}</strong> (${c.team} - ${c.role}) ${c.file_path ? `on <code>${c.file_path}:${c.line_number}</code>` : ''}
            </div>
            <div style="color:var(--text-secondary)">${c.timestamp}</div>
          </div>
          <div class="comment-body">
            ${c.comment}
            ${c.is_blocking ? '<div style="color:#f85149; font-weight:600; margin-top:8px;">❌ Requested changes (blocking)</div>' : ''}
          </div>
        </div>
      `).join('')}
    </div>

    <!-- ADD REVIEW FORM -->
    <div class="card" style="margin-top:24px;">
      <div class="card-header">Leave a Code Review</div>
      <div class="card-body">
        <textarea id="review-comment-input" rows="3" placeholder="Leave review feedback or approval notes..." style="width:100%; background:var(--bg-tertiary); color:white; border:1px solid var(--border-color); border-radius:4px; padding:8px; margin-bottom:12px;"></textarea>
        <div style="display:flex; justify-content:flex-end; gap:8px;">
          <button class="btn" onclick="submitReview('comment')">Comment</button>
          <button class="btn btn-danger" onclick="submitReview('request_changes')">Request Changes</button>
          <button class="btn btn-primary" onclick="submitReview('approve')">Approve PR</button>
        </div>
      </div>
    </div>
  `;
}

function backToPrList() {
  document.getElementById("pr-detail-view").style.display = "none";
  document.getElementById("pr-list-view").style.display = "block";
  fetchPrs();
}

async function submitReview(action) {
  const text = document.getElementById("review-comment-input").value.trim();
  if (!text) {
    alert("Please enter a review comment.");
    return;
  }

  try {
    const res = await fetch(`/api/prs/${state.activePrId}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        author: "Staff Principal Engineer (You)",
        role: "Lead Maintainer",
        comment: text,
        action: action,
      })
    });
    const data = await res.json();
    if (data.success) {
      alert(`[✓] Review submitted with action: ${action.toUpperCase()}`);
      openPrDetail(state.activePrId);
      fetchPrs();
    }
  } catch (err) {
    alert("Failed to submit review: " + err);
  }
}

async function mergeActivePr() {
  const strat = document.getElementById("merge-strategy-select").value;
  try {
    const res = await fetch(`/api/prs/${state.activePrId}/merge`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ strategy: strat })
    });
    const data = await res.json();
    if (data.success) {
      alert(`[✓] ${data.message}`);
      backToPrList();
    } else {
      alert(`[✗] ${data.error}`);
    }
  } catch (err) {
    alert("Merge error: " + err);
  }
}

// ----------------------------------------------------------------------------
// 3. CODE & COMMITS
// ----------------------------------------------------------------------------
async function fetchCommits() {
  try {
    const res = await fetch("/api/repo/commits");
    const data = await res.json();
    const list = document.getElementById("commits-list");
    list.innerHTML = "";

    if (!data.commits.length) {
      list.innerHTML = `<p style="color:var(--text-secondary)">No commits found in current playground repository.</p>`;
      return;
    }

    data.commits.forEach((c) => {
      const row = document.createElement("div");
      row.style.padding = "8px 0";
      row.style.borderBottom = "1px solid var(--border-color)";
      row.style.display = "flex";
      row.style.justifyContent = "space-between";
      row.innerHTML = `
        <div>
          <strong>${c.message}</strong>
          <div style="font-size:12px; color:var(--text-secondary);">
            ${c.author_name} &lt;${c.author_email}&gt; • ${c.time_ago}
          </div>
        </div>
        <div style="font-family:var(--font-mono); font-size:12px; color:var(--accent-blue)">
          ${c.sha.substring(0, 8)}
        </div>
      `;
      list.appendChild(row);
    });
  } catch (err) {
    console.error("Failed to fetch commits:", err);
  }
}

async function simulateSync(action) {
  try {
    const res = await fetch("/api/repo/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: action })
    });
    const data = await res.json();
    if (data.success) {
      alert(`[✓] git ${action} executed successfully!\n${data.stdout}`);
    } else {
      alert(`[✗] git ${action} rejected:\n${data.stderr || data.stdout}`);
    }
    fetchCommits();
    fetchRepoStatus();
  } catch (err) {
    alert("Sync error: " + err);
  }
}

// ----------------------------------------------------------------------------
// 4. FORENSIC RADAR
// ----------------------------------------------------------------------------
async function fetchRepoStatus() {
  try {
    const res = await fetch("/api/repo/status");
    const data = await res.json();
    state.health = data;

    // Header updates
    document.getElementById("nav-health-score").textContent = `${data.health_score}% (${data.health_status})`;
    document.getElementById("code-current-branch").textContent = data.current_branch || (data.is_detached ? "DETACHED HEAD" : "main");

    // Radar view updates
    document.getElementById("radar-score").textContent = `${data.health_score} / 100`;
    document.getElementById("radar-status").textContent = data.health_status;
    document.getElementById("radar-status").style.color = data.health_score >= 90 ? "var(--accent-green)" : (data.health_score >= 70 ? "var(--accent-yellow)" : "var(--accent-red)");

    const anom = document.getElementById("radar-anomalies");
    anom.innerHTML = `
      <ul style="list-style:none;">
        <li style="padding:6px 0;"><strong>Active Conflicts:</strong> ${data.has_conflicts ? `<span style="color:#f85149">YES (${data.conflicted_files.join(', ')})</span>` : '<span style="color:#3fb950">None</span>'}</li>
        <li style="padding:6px 0;"><strong>Uncommitted Changes:</strong> ${data.uncommitted_count} files</li>
        <li style="padding:6px 0;"><strong>Dangling / Lost Commits:</strong> ${data.dangling_commits.length} detected</li>
        <li style="padding:6px 0;"><strong>Secret Leak Alerts:</strong> ${data.suspicious_findings.length ? `<span style="color:#f85149">${data.suspicious_findings.join(', ')}</span>` : '<span style="color:#3fb950">Clean</span>'}</li>
      </ul>
    `;
  } catch (err) {
    console.error("Failed to fetch repo status:", err);
  }
}

function fetchForensics() {
  fetchRepoStatus();
  alert("Radar telemetry refreshed!");
}

// ----------------------------------------------------------------------------
// 5. EMERGENCY ESCALATION WAR ROOM
// ----------------------------------------------------------------------------
function openEscalationModal() {
  document.getElementById("escalation-modal").style.display = "flex";
}

function closeEscalationModal() {
  document.getElementById("escalation-modal").style.display = "none";
}

async function submitEscalation() {
  const sev = document.getElementById("esc-sev").value;
  const title = document.getElementById("esc-title").value;
  const impact = document.getElementById("esc-impact").value;
  const notes = document.getElementById("esc-notes").value;

  try {
    const res = await fetch("/api/escalate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        severity: sev,
        title: title,
        impact: impact,
        notes: notes,
      })
    });
    const data = await res.json();
    closeEscalationModal();

    const container = document.getElementById("escalation-log-container");
    container.innerHTML = `
      <div style="background:#da36331a; border:1px solid #da3633; padding:16px; border-radius:6px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
          <strong style="color:#f85149;">🚨 ACTIVE ${data.severity} DISPATCH BROADCAST</strong>
          <span style="font-size:12px; color:var(--text-secondary);">${data.timestamp}</span>
        </div>
        <pre style="background:black; color:#39d353; padding:12px; border-radius:4px;">${data.broadcast_message}</pre>
        <button class="btn btn-primary" style="margin-top:12px;" onclick="copyEscalationBroadcast()">Copy Alert Broadcast to Clipboard</button>
      </div>
    `;

    // Switch to War Room tab
    document.querySelector('.tab-btn[data-tab="incident-warroom"]').click();
  } catch (err) {
    alert("Escalation failed: " + err);
  }
}

function copyEscalationBroadcast() {
  const pre = document.querySelector("#escalation-log-container pre");
  if (pre) {
    navigator.clipboard.writeText(pre.innerText);
    alert("[✓] Escalation broadcast copied to clipboard!");
  }
}
