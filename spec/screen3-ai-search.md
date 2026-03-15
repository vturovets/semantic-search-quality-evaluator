# Screen 3 Specification — Release Decision / Statistical Validation

**Product:** AI Product Experiment Lab  
**Screen name:** Release Decision  
**Purpose:** Convert experiment metrics into a clear business recommendation using statistical evidence, so stakeholders can decide whether an AI feature variant is ready for release. This screen operationalizes the product promise of validating AI improvements with measurable confidence rather than intuition.

---

## 1. Screen goal

This screen is the **decision layer** of the product flow:

**capability → question → evidence → decision**

It should show how the platform turns raw experiment outcomes into a release recommendation for a product manager, AI lead, or engineering manager. The screen must feel like a modern SaaS decision dashboard, not a developer console. It should visually connect to Screen 2 by assuming the user has already reviewed experiment results and now wants to understand whether the observed improvement is statistically meaningful and safe to act on.

---

## 2. Primary user story

**As a product or AI decision-maker,**  
I want to see whether Variant B is statistically better than Variant A,  
so that I can confidently choose one of the following actions:

- release the new version

- keep testing

- reject the change

---

## 3. What Screen 3 represents in the architecture

This screen represents the final decision output of the **Hypothesis Testing Tool**, which sits on top of experiment metrics and produces statistically grounded conclusions. It is the business-facing realization of the product’s core concept: answering whether two systems or approaches are truly different.

**Conceptual mapping:**

- **Screen 1:** User query → LLM → product/search result

- **Screen 2:** Promptfoo + traces + dataset → experiment metrics

- **Screen 3:** Hypothesis Testing Tool → statistical conclusion → release decision

---

## 4. Core design principle

The screen must answer four questions, in this exact order:

1. **What was tested?**

2. **What evidence was observed?**

3. **Is the difference statistically significant?**

4. **What should the business do now?**

The page should feel concise, executive-friendly, and trustworthy.

---

## 5. Page layout

Use a **12-column responsive dashboard layout** with generous spacing, soft cards, muted borders, and a premium B2B SaaS look.

### Desktop layout

#### Top row

- Page title and experiment identity

- Status badge

- Primary recommendation badge

- Header actions

#### Middle row

- Left: statistical summary card

- Right: release recommendation card

#### Lower row

- Left: hypothesis definition + test inputs

- Right: results interpretation + confidence/explanation

#### Bottom row

- decision rationale timeline or steps

- optional comparison snapshot from Screen 2

- footer note / disclaimer

---

## 6. Main sections

### A. Header bar

Purpose: establish context immediately.

**Elements:**

- Page title: `Release Decision`

- Subtitle: `Statistical validation of experiment outcomes`

- Experiment name, for example: `Product Search Prompt Optimization`

- Variant label, for example: `Candidate: Prompt v2`

- Baseline label, for example: `Baseline: Prompt v1`

- Run date/time

- Dataset name

- Experiment status badge: `Completed`

- Decision badge:
  
  - `Safe to release`
  
  - `Needs more evidence`
  
  - `Do not release`

**Header actions (UI only, no backend implementation):**

- `Export Report`

- `Share`

- `Back to Experiment Dashboard`

---

### B. Recommendation card

This is the most prominent card on the screen.

**Purpose:** provide the business decision in one glance.

**Card content:**

- Label: `Recommendation`

- Large decision text:
  
  - `SAFE TO RELEASE`
  
  - or `KEEP TESTING`
  
  - or `DO NOT RELEASE`

- Support sentence:
  
  - Example: `Observed improvement is statistically significant at the selected confidence level.`

- Small impact summary:
  
  - Example: `Expected search success rate improvement: +5–7%`

- Confidence pill:
  
  - Example: `95% confidence`

- Optional small icon:
  
  - green check for release
  
  - amber pause for more testing
  
  - red stop for reject

This card should visually dominate the right side of the page.

---

### C. Statistical summary card

Purpose: show the essential quantitative result without requiring the user to interpret raw data.

**Fields:**

- Metric under evaluation, for example:
  
  - `Accuracy`
  
  - `Success rate`
  
  - `P95 latency`

- Baseline value

- Candidate value

- Absolute difference

- Relative improvement

- p-value

- Confidence level

- Result text:
  
  - `Statistically significant`
  
  - or `Not statistically significant`

**Example content:**

- Metric: `Accuracy`

- Prompt v1: `82%`

- Prompt v2: `88%`

- Improvement: `+6.0%`

- p-value: `0.018`

- Confidence level: `95%`

- Result: `Statistically significant`

This card should be compact and highly legible.

---

### D. Hypothesis definition card

Purpose: explain the logic behind the statistical conclusion in plain language.

**Fields:**

- `Null hypothesis`

- `Alternative hypothesis`

- `Test type`

- `Decision threshold`

**Example copy:**

- Null hypothesis: `Prompt v2 is not better than Prompt v1`

- Alternative hypothesis: `Prompt v2 performs better than Prompt v1`

- Test type: `One-sided statistical comparison`

- Significance threshold: `α = 0.05`

This section is important for trust and credibility because the product’s differentiator is statistical rigor, not just dashboards.

---

### E. Test inputs card

Purpose: show the scope of evidence behind the decision.

**Fields:**

- Dataset size

- Number of evaluated queries / requests

- Selected metric

- Variant pair

- Evaluation source tags

- Optional note about method

**Example values:**

- Dataset size: `200 queries`

- Method: `Binomial accuracy comparison`

- Evidence sources:
  
  - `Promptfoo evaluation`
  
  - `Langfuse traces`
  
  - `Hypothesis Testing Tool`

This section grounds the decision in the broader product architecture.

---

### F. Interpretation panel

Purpose: translate statistical output into business language.

**Suggested structure:**

#### Interpretation

`The candidate version demonstrates a measurable improvement over the baseline. Based on the selected confidence threshold, the observed gain is unlikely to be random variation.`

#### Business implication

`This variant is suitable for release into production or the next rollout stage.`

#### Risk note

`Continue monitoring latency and consistency after release.`

This card should be written in simple, stakeholder-friendly language.

---

### G. Decision rationale strip

A horizontal 4-step visual strip or mini timeline.

**Steps:**

1. `Experiment completed`

2. `Metrics compared`

3. `Hypothesis test passed`

4. `Release recommendation generated`

Each step can have a small icon and a short status label.  
This helps communicate process maturity and supports the “platform” feel.

---

### H. Optional comparison snapshot

A smaller supporting card that reminds the user of the key experiment metrics from Screen 2.

**Example mini-table:**

| Metric      | Baseline | Candidate |
| ----------- | -------- | --------- |
| Accuracy    | 82%      | 88%       |
| Consistency | 79%      | 83%       |
| Avg latency | 780 ms   | 710 ms    |

This card provides continuity across screens and reinforces that Screen 3 is built on measurable experiment results.

---

## 7. Suggested page content for the high-fidelity prototype

Use the following realistic demo content in the UI:

### Header

- Title: `Release Decision`

- Subtitle: `Statistical validation of AI experiment outcomes`

- Experiment: `Product Search Prompt Optimization`

- Candidate: `Prompt v2`

- Baseline: `Prompt v1`

- Status: `Completed`

### Recommendation card

- Recommendation: `SAFE TO RELEASE`

- Support text: `Observed improvement is statistically significant at 95% confidence.`

- Expected impact: `Search success rate +5–7%`

### Statistical summary

- Metric: `Accuracy`

- Prompt v1: `82%`

- Prompt v2: `88%`

- Improvement: `+6.0%`

- p-value: `0.018`

- Confidence level: `95%`

- Result: `Reject null hypothesis`

### Hypothesis block

- Null hypothesis: `Prompt v2 is NOT better than Prompt v1`

- Alternative hypothesis: `Prompt v2 is better than Prompt v1`

- Test type: `One-sided test`

- Alpha: `0.05`

### Test inputs

- Dataset size: `200 queries`

- Evaluation mode: `Offline experiment`

- Source signals:
  
  - `Promptfoo`
  
  - `Langfuse`
  
  - `Hypothesis Testing Tool`

### Interpretation

`The observed improvement is large enough and statistically credible enough to support release. Post-release monitoring is still recommended.`

This content aligns directly with the earlier UI concept and business concept.

---

## 8. Visual style guidance

The screen should feel like a polished B2B analytics product.

### Style direction

- clean white or light-gray background

- rounded cards

- subtle shadows

- premium spacing

- restrained color palette

- strong typography hierarchy

### Typography

- Page title: large and bold

- Recommendation outcome: very large, visually dominant

- Section labels: small uppercase or semibold

- Supporting text: short, readable, business-oriented

### Color semantics

- Green: safe to release

- Amber: inconclusive / needs more evidence

- Red: do not release

- Blue or neutral tones for data cards and metadata

### Icons

Use minimal icons:

- beaker / experiment

- sigma / stats

- shield / confidence

- rocket / release decision

Do not overload the screen with technical imagery.

---

## 9. Component list for frontend development

Use reusable UI components.

### Required components

- Page container

- Header bar

- Status badge

- Decision badge

- KPI/stat cards

- Recommendation hero card

- Hypothesis definition card

- Small comparison table

- Step progress strip

- Secondary action buttons

- Tooltip or info icon for terms like `p-value`, `confidence level`, `null hypothesis`

### Optional enhancements

- tiny sparkline next to candidate vs baseline

- small confidence gauge

- pill tags for evidence sources

- hover states with concise definitions

---

## 10. Interaction behavior

Frontend-only, no backend logic required.

### Static interactions to support in prototype

- Hover on statistical terms shows explanatory tooltip

- Hover on recommendation card slightly elevates card

- Clicking `Back to Experiment Dashboard` navigates to Screen 2 prototype

- Clicking `Export Report` opens a mock dropdown or modal

- Clicking evidence source tags can show a small side drawer or tooltip summary

### Do not implement

- real calculations

- API integrations

- authentication

- persistence

- live chart updates

---

## 11. Responsive behavior

### Desktop

- two-column emphasis

- recommendation card and statistical summary above the fold

### Tablet

- cards stack in logical order

- recommendation remains first visible after header

### Mobile

Order sections as:

1. Header

2. Recommendation

3. Statistical summary

4. Hypothesis

5. Test inputs

6. Interpretation

7. Comparison snapshot

The recommendation must remain immediately visible on smaller screens.

---

## 12. UX writing guidance

Tone should be:

- professional

- concise

- trustworthy

- decision-oriented

Avoid:

- raw statistical jargon without explanation

- engineering-heavy logs

- long paragraphs

- ambiguous phrases like `maybe better`

Prefer:

- `statistically significant`

- `not enough evidence`

- `recommended for release`

- `continue testing`

---

## 13. Why this screen matters in the product narrative

This screen is critical because it expresses the unique market positioning of the product: not merely running AI experiments, but helping organizations make **statistically validated product decisions**. That is the core bridge between consulting methodology and scalable software productization.

It also reinforces the overall product story:

- Screen 1 proves the AI feature works

- Screen 2 proves it can be measured

- Screen 3 proves the business can decide with confidence

---

## 14. Handoff note for Kiro

Build **Screen 3** as a high-fidelity frontend dashboard page named **Release Decision** for the product **AI Product Experiment Lab**.

The page should:

- present a completed AI experiment

- show statistical evidence comparing a candidate variant vs baseline

- explain null hypothesis and significance result

- surface a strong business recommendation such as `SAFE TO RELEASE`

- look like a polished SaaS analytics platform

- use static demo data only

- contain no backend functionality

Use a component-based React-style structure with modern dashboard aesthetics, responsive layout, and production-quality visual hierarchy. Base the content and logic on the product idea of combining AI evaluation with hypothesis testing for release decisions.


