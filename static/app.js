const form = document.querySelector("#generate-form");
const button = document.querySelector("#submit-button");
const statusBar = document.querySelector("#status-bar");
const statusText = document.querySelector("#status-text");
const emptyState = document.querySelector("#empty-state");
const progressSection = document.querySelector("#progress-section");
const progressFill = document.querySelector("#progress-fill");
const progressPct = document.querySelector("#progress-pct");
const progressLabel = document.querySelector("#progress-label");
const resultArea = document.querySelector("#result-area");
const image = document.querySelector("#generated-image");
const pdfMeta = document.querySelector("#pdf-meta");
const fileInput = document.querySelector("#pdf");
const fileName = document.querySelector("#file-name");
const fileIcon = document.querySelector("#file-icon");
const teachingSummary = document.querySelector("#teaching-summary");
const researchReport = document.querySelector("#research-report");
const rawOutput = document.querySelector("#raw-output");

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (!file) {
    fileName.textContent = "";
    fileName.style.display = "none";
    fileIcon.textContent = "PDF";
    return;
  }

  fileName.textContent = file.name;
  fileName.style.display = "block";
  fileIcon.textContent = "OK";
});

document.querySelectorAll("[data-tab]").forEach((tab) => {
  tab.addEventListener("click", () => switchTab(tab.dataset.tab));
});

document.querySelectorAll("[data-view]").forEach((pill) => {
  pill.addEventListener("click", () => switchTab(pill.dataset.view));
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const formData = new FormData(form);
  setLoading(true);
  setStatus("Processing PDF, agents, and image generation...", "active");
  showProgress();
  setProgress(18, "Ingesting PDF...", 0);

  const progressTimer = startProgressAnimation();

  try {
    const response = await fetch("/api/generate", {
      method: "POST",
      body: formData,
    });
    const payload = await response.json();

    if (!response.ok) {
      throw new Error(payload.error || "Generation failed.");
    }

    clearInterval(progressTimer);
    setProgress(100, "Done.", 4);
    renderResult(payload);
    setStatus("Done.", "done");
  } catch (error) {
    clearInterval(progressTimer);
    setStatus(error.message, "error");
  } finally {
    setLoading(false);
    setTimeout(() => progressSection.classList.remove("visible"), 600);
  }
});

function renderResult(payload) {
  image.src = payload.image_data_url;
  teachingSummary.innerHTML = renderMarkdown(payload.teaching_summary);
  researchReport.innerHTML = renderMarkdown(payload.research_report);
  rawOutput.innerHTML = renderMarkdown(
    `# Teaching Summary\n${payload.teaching_summary}\n\n# Research Notes\n${payload.research_report}`
  );

  if (payload.pdf) {
    pdfMeta.textContent = `${payload.pdf.filename} (${payload.pdf.page_count} pages)`;
  } else {
    pdfMeta.textContent = "Generated without PDF upload";
  }

  emptyState.style.display = "none";
  resultArea.classList.add("visible");
  switchTab("teaching");
}

function switchTab(id) {
  document.querySelectorAll(".tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.tab === id);
  });
  document.querySelectorAll(".pill").forEach((pill) => {
    pill.classList.toggle("active", pill.dataset.view === id);
  });
  document.querySelectorAll(".tab-content").forEach((content) => {
    content.classList.toggle("active", content.id === `tab-${id}`);
  });
}

function setLoading(isLoading) {
  button.disabled = isLoading;
  button.textContent = isLoading ? "Generating..." : "Generate Summary";
}

function setStatus(message, state = "active") {
  statusBar.className = `status-bar ${state}`;
  statusText.textContent = message;
}

function showProgress() {
  emptyState.style.display = "none";
  progressSection.classList.add("visible");
}

function setProgress(percent, label, activeStep) {
  progressFill.style.width = `${percent}%`;
  progressPct.textContent = `${percent}%`;
  progressLabel.textContent = label;

  ["step-1", "step-2", "step-3", "step-4"].forEach((id, index) => {
    const step = document.querySelector(`#${id}`);
    step.className = "step-chip";
    if (index < activeStep) step.classList.add("done");
    if (index === activeStep) step.classList.add("active");
  });
}

function startProgressAnimation() {
  const stages = [
    [34, "Retrieving PDF context...", 1],
    [56, "Running researcher agent...", 2],
    [78, "Writing summary and image prompt...", 3],
    [92, "Generating image...", 3],
  ];
  let index = 0;
  return setInterval(() => {
    if (index < stages.length) {
      setProgress(...stages[index]);
      index += 1;
    }
  }, 1600);
}

function renderMarkdown(value) {
  const escaped = escapeHtml(value || "");
  return escaped
    .replace(/^### (.*)$/gm, "<strong>$1</strong>")
    .replace(/^## (.*)$/gm, "<strong>$1</strong>")
    .replace(/^# (.*)$/gm, "<strong>$1</strong>")
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br>");
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[char];
  });
}
