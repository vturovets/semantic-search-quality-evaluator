# Screen 1 Specification

## Name

**AI Product Search**

## Purpose

This first screen must demonstrate the product’s **AI feature in action**: a user enters a natural-language query, the UI shows how the request is interpreted into structured filters, displays product results, and surfaces lightweight execution evidence such as latency, tokens, and trace ID. This aligns with the original UX concept for Screen 1 and supports the broader positioning of the product as an AI reliability / evaluation platform rather than a raw technical demo.

## Primary user impression

The screen should immediately communicate:

- this is a **real AI-powered product experience**

- the system can turn **plain English into structured intent**

- the experience is **observable and measurable**

- this is a **professional SaaS product**, not a CLI wrapper or developer-only demo

---

# 1. High-level UX goal

The screen should answer this stakeholder question:

> “Can I see how the AI feature works from user query to interpretable result?”

It should visually move through this sequence:

1. user enters natural language request

2. AI interprets the request

3. system returns relevant results

4. evidence panel shows operational metrics

This directly reflects the architecture and demo logic in the uploaded notes: user query → LLM / interpretation → product results, with observability around the pipeline.

---

# 2. Screen type

**Single-page application screen** with a **desktop-first SaaS layout**.

This is **not** a marketing landing page.  
This is the first page inside the product demo / prototype.

---

# 3. Layout structure

## Overall layout

Use a **12-column desktop grid** with generous whitespace.

### Top-level regions

1. **Top navigation/header**

2. **Hero/title block**

3. **Search interaction panel**

4. **AI interpretation panel**

5. **Search results panel**

6. **Execution metrics panel**

7. **Optional footer note / next-step CTA**

### Desktop arrangement

- Header across full width

- Main content in two columns:
  
  - **Left column (7/12):** search panel + results
  
  - **Right column (5/12):** interpreted filters + execution metrics

- Max content width: about **1280px**

- Page background: very light neutral gray

- Content cards: white with soft shadow and rounded corners

---

# 4. Visual style

## Style direction

A **modern B2B SaaS analytics/product UI**.  
The feel should combine:

- AI assistant

- product search

- experiment platform

## Mood

- trustworthy

- clean

- evidence-driven

- slightly premium

- business-friendly

## Recommended visual traits

- rounded cards (`rounded-2xl`)

- subtle shadows

- restrained color palette

- strong typography hierarchy

- soft blue or indigo accent for AI-related elements

- green for “healthy / valid / ready”

- amber only for secondary warnings

- avoid dark cyberpunk styling

## Suggested typography hierarchy

- Page title: large, bold

- Section headings: medium bold

- Card labels: smaller uppercase or semibold

- Supporting text: neutral gray

# 5. Header specification

## Header content

Left:

- product name: **AI Product Experiment Lab**

Center or right:

- nav items:
  
  - Search
  
  - Experiments
  
  - Release Validation

- “Search” is active

Far right:

- ghost button: **View Demo Flow**

- circular avatar placeholder or initials badge

## Header behavior

- sticky on scroll for desktop

- thin bottom border

- white background with slight blur effect

---

# 6. Hero/title block

## Content

**Title:**  
AI Product Search

**Subtitle:**  
Search using natural language and see how AI interprets intent, returns results, and exposes execution evidence.

## Supporting badges

Show 3 small badges under the subtitle:

- Natural Language Search

- Interpreted Filters

- Observable Execution

These badges reflect the core value proposition: measurable AI behavior, observability, and interpretability.

---

# 7. Search interaction panel

## Card title

**Search using natural language**

## Input area

A large prominent search bar with:

- placeholder: **Find cheap winter running shoes**

- search icon on the left

- “Run Search” button on the right

### Below the search box

Show 4 pill-style sample prompts:

- cheap winter running shoes

- sandals for hot weather

- kids shoes under €50

- waterproof trail shoes

Clicking a prompt fills the search box and updates the rest of the screen with mock data.

## Interaction model

No real backend.  
This is a pure frontend prototype with local mock objects.

When the user clicks **Run Search**:

- show a subtle loading shimmer for 700–1200 ms

- then render the interpretation, results, and metrics for the selected mock query

## Empty state

Default state should already be prefilled with:  
**Find cheap winter running shoes**

This is consistent with the original concept example and architecture notes.

---

# 8. Interpretation panel

## Card title

**Interpreted filters**

## Purpose

This panel is critical. It proves that the AI converted natural language into structured intent.

## Display format

Use visually distinct chips or key-value rows.

### Example for default query

- Category: Shoes

- Type: Running

- Season: Winter

- Price: Low

- Feature: Waterproof

Show them as polished badges in a grouped layout.

## Secondary line

Below the chips, show a short sentence:

**AI interpretation summary:**  
Budget-oriented winter running footwear with weather protection.

## Confidence indicator

Add a small non-technical confidence pill:

- Interpretation confidence: **High**

This is only visual and uses mock data.

## Expandable detail

Add a collapsed link:  
**View structured output**

When expanded, show a tiny code-style JSON preview:

```json
{
  "category": "shoes",
  "type": "running",
  "season": "winter",
  "price": "low",
  "feature": "waterproof"
}
```

This matches the documented idea that the LLM output becomes structured filters that are then used for product retrieval.

# 9. Results panel

## Card title

**Results**

## Result card format

Render **3 product cards** in a vertical stack.

Each result card contains:

- product image placeholder

- product name

- short descriptor

- price

- tags

- CTA button: **View Product**

### Default mock products

1. **Waterproof Winter Running Shoes**  
   Lightweight insulated runner for cold-weather training  
   **€79**  
   Tags: Winter, Waterproof, Running

2. **Budget Trail Running Shoes**  
   Durable all-weather model for mixed terrain  
   **€64**  
   Tags: Trail, Budget, Grip

3. **Lightweight Winter Trainers**  
   Daily-use cold-season trainer with comfort lining  
   **€69**  
   Tags: Winter, Lightweight, Everyday

## Visual logic

The first result should look slightly emphasized:

- thin accent border

- “Best match” badge

## Result card interactions

Hover state:

- mild elevation

- image zoom of 2–3%

- CTA becomes more prominent

No actual navigation needed; buttons can be inert or open a dummy product drawer in the prototype.

---

# 10. Execution metrics panel

## Card title

**Execution metrics**

## Purpose

This card gives engineers and technically minded stakeholders enough evidence to understand that this is an AI system with observable runtime behavior, while still keeping the interface business-friendly. That intent is explicitly mentioned in the UI concept and observability notes.

## Metrics to show

Use 3 to 4 compact stat blocks:

- **Latency**  
  740 ms

- **LLM tokens**  
  920

- **Trace ID**  
  92AF14

- **Search status**  
  Completed

## Optional microcopy

Below the stats:

This view exposes lightweight runtime evidence for AI-driven search execution.

## Trace action

A tertiary button or text link:  
**Open trace details**

In prototype mode it can open a side drawer with mock trace info:

- input received

- interpretation completed

- results returned

---

# 11. Right-column composition

The right column should stack:

1. Interpreted filters

2. Execution metrics

This creates the visual narrative:

- the **left side** shows the customer-facing outcome

- the **right side** shows the machine-facing evidence

That split supports both product/business and engineering audiences, exactly as described in the concept.

---

# 12. Footer CTA / next step

At the bottom of the main area, add a horizontal CTA strip:

**Next: Evaluate prompt versions and compare outcomes**  
Button: **Go to Experiment Dashboard**

This provides continuity into Screen 2, where the concept moves from feature demonstration into experiment evaluation.

---

# 13. Mock data model for frontend prototype

Use local static data only.

## Suggested mock query object

```typescript
type SearchScenario = {
  query: string;
  interpretation: {
    filters: { label: string; value: string }[];
    summary: string;
    confidence: "High" | "Medium" | "Low";
    structuredOutput: Record<string, string>;
  };
  results: {
    id: string;
    name: string;
    description: string;
    price: string;
    tags: string[];
    badge?: string;
    image: string;
  }[];
  metrics: {
    latencyMs: number;
    tokens: number;
    traceId: string;
    status: string;
  };
};
```

## Required default scenario

`Find cheap winter running shoes`

## Additional static scenarios

- sandals for hot weather

- kids shoes under €50

- waterproof trail shoes

# 4. Recommended component breakdown

Kiro/Codex should split the page into reusable components:

- `AppHeader`

- `PageHero`

- `SearchBarCard`

- `SamplePromptChips`

- `InterpretedFiltersCard`

- `StructuredOutputAccordion`

- `SearchResultsCard`

- `ProductResultItem`

- `ExecutionMetricsCard`

- `NextStepBanner`

This aligns with the “high-fidelity frontend only” requirement and keeps implementation modular.

---

# 15. Interaction states to implement

## Search bar

- default

- hover

- focused

- loading

## Filter chips

- default static chips

- optional hover tooltip

## Product cards

- default

- hover

## Metrics panel

- default

- trace drawer open

## General page states

- preloaded default state

- loading state after clicking Run Search

- no-results state for one optional scenario

### Optional no-results state

Add one hidden scenario where no exact products match.  
Show:

- message: **No exact matches found**

- suggested related filters

- still show interpreted filters and execution metrics

This makes the screen feel more realistic.

---

# 16. Responsive behavior

## Desktop

Two-column layout as described.

## Tablet

- stack hero and search full width

- results first

- interpretation second

- metrics third

## Mobile

- single column

- sticky search CTA

- metric blocks become 2x2 grid

Even though the prototype is desktop-first, responsive polish will make it look production-grade.

---

# 17. Accessibility / UX requirements

- all interactive elements keyboard accessible

- visible focus states

- sufficient contrast

- buttons minimum 44px height

- semantic headings

- aria labels for search input and buttons

---

# 18. What must be visible above the fold

On desktop, the first viewport should show:

- header

- screen title/subtitle

- search box

- at least the top of interpreted filters and first result

The user should understand the value proposition in under 5 seconds.

---

# 19. What this screen is proving

This screen is not just “search UI.”  
It proves the first layer of your standalone product strategy:

- **AI capability demonstration**

- **observable AI execution**

- **business-friendly evidence presentation**

That is consistent with your broader concept of combining consulting rigor with productized tooling around reliability, metrics, and statistical validation.
