# Complyable

**A local-first GDPR document redaction tool for German recruiting agencies.**

[Complyable](https://www.complyable.de) is a portfolio project I built over three months as a solo technical founder. It started as a real product attempt and ended as one of the most educational experiences of my career. This README documents not just what I built, but how I thought about it, what broke, and what I learned along the way.

---

## The Problem

German recruiting agencies handle thousands of CVs. Under GDPR, personally identifiable information (PII) — names, addresses, phone numbers, email addresses — must be handled with strict controls. Beyond PII, German equal opportunity law discourages gender-coded language in job titles (e.g. *Kaufmann/Kauffrau*) to prevent bias in hiring decisions.

Most existing tools either live in the cloud (which creates its own compliance exposure) or require expensive enterprise contracts. Small and mid-sized agencies were underserved.

**The core insight:** The compliance argument is strongest when data never leaves the customer's machine. A local-first architecture isn't just a technical choice — it's the product's value proposition.

---

## What It Does

[Complyable](https://www.complyable.de) processes CV documents through a three-tier NLP pipeline and presents findings in a review interface where users can toggle redactions before generating a certified, audit-trailed output.

```
Input (PDF/DOCX) → Parser → Tier 1 (Regex) → Tier 2 (spaCy NER) → Tier 3 (Gender) → Review UI → Redacted Output + Certificate
```

**Tier 1 — Regex:** Emails, phone numbers, postal codes, URLs, social media handles, dates.

**Tier 2 — spaCy NER:** German named entity recognition for persons, locations, and organisations using `de_core_news_md`. Beam parsing for confidence scoring.

**Tier 3 — Gender neutralization:** Dictionary lookup and linguistic flagging of gendered job titles. Replacements are suggested (e.g. *Kaufmann* → *kfm. Fachkraft*), flags are surfaced for human review.

All three tiers run independently on the original normalized text — they don't modify each other's input. Findings are written to SQLite with full audit trails. The UI allows per-finding toggle of redaction status before certificate generation.

---

## Architecture

```
complyable/
├── ui/
│   ├── main.py          # Streamlit entry point and navigation
│   ├── pipeline.py      # Three-tier NLP pipeline
│   ├── workflow.py      # Pipeline orchestration and locking
│   ├── database.py      # SQLite schema and query layer
│   ├── logic.py         # Business logic and state management
│   ├── styles.py        # CSS injection and theming
│   └── overlay/         # JS/CSS document highlight component
├── data/
│   ├── vault/           # SQLite database (persisted via volume mount)
│   ├── input/           # Drop zone for incoming documents
│   ├── output/          # Redacted PDFs and certificates
│   └── refs/            # Gender neutralization dictionary
├── assets/
│   ├── fonts/           # ArialUnicode for PDF generation
│   └── streamlit_config.toml
├── Dockerfile
├── requirements.txt
└── installer/
    ├── setup.iss        # Inno Setup configuration
    └── install.ps1      # Windows installation script
```

**Key architectural decisions:**

- **Local-first container:** Everything runs inside a Podman container on the customer's machine. No network calls, no telemetry, no cloud dependency.
- **Stateless container, stateful host:** The container itself is ephemeral. Data persists via volume mounts to the host filesystem, surviving container restarts and image updates.
- **Independent pipeline tiers:** Each tier receives the original normalized text, not the output of the previous tier. This prevents compounding errors and makes each tier independently testable.
- **Single SQLite database:** All pipeline findings, document metadata, audit events, and user decisions live in one file. Simple, portable, no infrastructure.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit 1.55 |
| NLP | spaCy 3.8.7 + de_core_news_md |
| Document parsing | Docling 2.15.1 |
| PDF generation | fpdf2 |
| Database | SQLite via Python stdlib |
| ML runtime | PyTorch 2.7.1 (CPU-only) |
| Containerization | Podman / Docker |
| Windows installer | Inno Setup 6 + PowerShell |
| CI/CD | GitHub Actions |

---

## The Challenges

This section is the honest part.

### Container image size

The first working image was **7.24GB**. That's a 45-minute pull on a typical connection — completely unacceptable for a customer install.

The root cause was PyTorch. Docling depends on torch, and pip was silently resolving the full CUDA build (GPU support) even though the target machines are standard laptops with no GPU. CUDA packages alone accounted for roughly 4GB.

The fix required understanding pip's dependency resolution order. Simply specifying `torch==x.x.x+cpu` in requirements.txt wasn't enough — Docling's own dependency declaration would override it during resolution. The solution was to pre-install CPU-only torch in a separate Dockerfile layer *before* requirements.txt, then write a pip constraints file (`PIP_CONSTRAINT`) that prevented any subsequent package from upgrading or replacing it:

```dockerfile
RUN pip install --no-cache-dir torch==2.7.1+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

RUN printf "torch==2.7.1+cpu\ndocling-core==2.14.0\n" > /constraints.txt
ENV PIP_CONSTRAINT=/constraints.txt

RUN pip install --no-cache-dir -r requirements.txt
```

Final image size: **2.01GB** — a 72% reduction. Pull time on Windows: approximately 5 minutes.

### Docling dependency cascade

After the image reduction, the app worked on Mac but failed on Windows with:

```
ModuleNotFoundError: Could not import module 'AutoProcessor'
```

Tracing the stack: Docling's newer releases added an ASR pipeline and Granite Vision model that imported `AutoProcessor` from transformers at module load time — before any pipeline options were applied. This meant the import failed even though we were never using those features.

The fix was pinning `docling-core` to `2.14.0` — the last version before the chart extraction and ASR pipeline were introduced. This required understanding that `docling` and `docling-core` version independently, and that pip could upgrade `docling-core` to a breaking version even when `docling` itself was pinned.

### torchvision version mismatch

With CPU-only torch installed, `torchvision` resolved to a version compiled against a different torch build, producing:

```
RuntimeError: operator torchvision::nms does not exist
```

The solution was to also pin `torchvision` to its CPU-only build in the constraints file, matching the exact torch version.

### Windows networking — gvproxy

Running the container on Windows via Podman requires `gvproxy` to bridge the WSL2 VM network to the Windows host. On some machines it failed to start automatically, preventing the browser from reaching the app.

This surfaced a broader lesson: Podman on Windows is significantly more fragile than on Mac/Linux. Every layer of the Windows stack (WSL2, Hyper-V, Podman machine, gvproxy, Windows Firewall) is a potential failure point. The installer had to handle each one defensively.

### Streamlit CSS limitations

Streamlit doesn't expose a clean theming API for most UI elements. Customizing beyond the basic `config.toml` options requires injecting CSS that targets Streamlit's internal generated class names — which change between versions.

The sidebar collapse/expand toggle was the most painful example. Hiding the Streamlit toolbar (to remove the deploy/rerun buttons from the production UI) also hid the sidebar toggle, because they share the same DOM container. The workaround was to hide individual toolbar children rather than the container itself, using `:not()` selectors — which worked inconsistently across Streamlit versions.

For the production build, the sidebar toggle is fixed (non-collapsible) until a cleaner solution is found.

### Document layout parsing

The first parser attempt used PyMuPDF for its small footprint. It failed immediately on German CVs — block-based text extraction reads across two-column layouts instead of down each column, scrambling the logical reading order.

Docling was chosen because it performs layout analysis before text extraction, understanding reading order in multi-column documents. The tradeoff is the large dependency footprint (torch), but the accuracy difference on real CVs was not replicable with lighter parsers.

---

## What I Learned

**Dependency management at scale is non-trivial.** pip's resolution algorithm optimizes for the latest compatible versions, not for your assumptions about what "compatible" means. Explicit pinning of the full dependency tree — not just your direct dependencies — is necessary for reproducible builds.

**Container size is a product decision, not just a technical one.** A 7GB image is a broken install experience. Optimizing it to 2GB required understanding the entire dependency graph, not just the application code.

**Local-first architecture requires rethinking the deployment model.** When there's no server to update, every customer machine is its own production environment. Containerization solves the "works on my machine" problem but introduces its own lifecycle management challenges.

**Windows is a different world.** Everything that works seamlessly on Mac/Linux requires explicit handling on Windows — path separators, execution policies, networking bridges, UAC elevation, scheduled tasks for post-reboot resume. Building a reliable Windows installer is a project in itself.

**Streamlit is a rapid prototyping tool, not a production UI framework.** It's excellent for getting something in front of users quickly, but fighting its CSS model and single-threaded execution model for production use is costly. A proper frontend (Tauri + React, or a native framework) would be the right V2 direction.

**The compliance argument is only as strong as the architecture supports it.** Privacy-first isn't a marketing claim — it has to be enforced at the infrastructure level. Every technical decision (local container, volume-mounted data, no external API calls) was made in service of that claim.

---

## Running Locally

**Prerequisites:** Podman or Docker, WSL2 (Windows only)

```bash
# Pull the image
podman pull ghcr.io/doctype-melvin/complyable:latest

# Run with persistent data
podman run -d \
  --name complyable-app \
  -p 8501:8501 \
  -v ./data/vault:/app/data/vault \
  -v ./data/output:/app/data/output \
  -v ./data/input:/app/data/input \
  ghcr.io/doctype-melvin/complyable:latest

# Open in browser
open http://localhost:8501
```

---

## Status

Complyable is a **portfolio project**. Development is paused after determining that market conditions (tool fatigue, budget constraints in German SMEs) made the path to paying customers longer than originally estimated.

The technical foundation is solid and the core pipeline works end to end. The codebase represents three months of solo full-stack development across NLP, containerization, UI, and Windows deployment — documented here as an honest record of what that process actually looks like.

---

## Author

**Melvin** — Analytics Engineer & Solutions Developer  
Hamburg, Germany  
[LinkedIn](https://www.linkedin.com/in/speckamp040/)

---

*Built with Python, spaCy, Docling, Streamlit, and a lot of patience.*