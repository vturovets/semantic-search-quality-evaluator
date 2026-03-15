# Screen 2 Specification

# AI Experiment Dashboard

## Screen Purpose

This screen demonstrates that the product can **evaluate AI system performance using structured experiments**.

It should look like a **professional AI experimentation platform**, not a prototype.

The screen answers the question:

> “Did the new AI version actually improve the product?”

Stakeholders should immediately understand:

- experiments exist

- multiple AI versions can be compared

- metrics are calculated

- improvement is visible

This screen visually sits **between Screen 1 and Screen 3**.

```
Screen 1 → AI feature
Screen 2 → AI evaluation
Screen 3 → statistical decision
```

# Layout Structure

Use a **3-section SaaS dashboard layout**.

```
-----------------------------------------------------------
Top Header
-----------------------------------------------------------

Experiment Info Panel

-----------------------------------------------------------

Results Comparison Table

-----------------------------------------------------------

Improvement Summary + Status

-----------------------------------------------------------
```

# Top Header

### Title

```
AI Experiment Dashboard
```

Subtitle

```
Evaluate AI feature performance using controlled experiments
```

Right-side Controls

Buttons:

```
[ New Experiment ]   [ Export Results ]
```

For prototype purposes these buttons **do nothing**.

# Experiment Info Panel

Place directly below header.

Use **card layout**.

### Card Title

```
Experiment: Product Search Prompt Optimization
```

### Fields

Display as **2-column grid**.

| Field           | Value                        |
| --------------- | ---------------------------- |
| Dataset         | Product Search Queries       |
| Dataset size    | 200 queries                  |
| Baseline model  | Prompt v1                    |
| Candidate model | Prompt v2                    |
| Experiment run  | 12 March 2026                |
| Data source     | Promptfoo evaluation dataset |

UI example

```
----------------------------------------------------
Experiment: Product Search Prompt Optimization
----------------------------------------------------

Dataset            Product Search Queries
Dataset size       200 queries
Baseline model     Prompt v1
Candidate model    Prompt v2
Experiment run     12 Mar 2026
Data source        Promptfoo evaluation dataset
----------------------------------------------------
```

# Results Comparison Table

This is the **main visual element** of Screen 2.

It compares **AI versions across evaluation metrics**.

### Table Columns

```
Metric
Prompt v1 (Baseline)
Prompt v2 (Candidate)
Difference
```

Example Data

| Metric          | Prompt v1 | Prompt v2 | Difference |
| --------------- | --------- | --------- | ---------- |
| Accuracy        | 82%       | 88%       | +6%        |
| Consistency     | 79%       | 83%       | +4%        |
| Average Latency | 780 ms    | 710 ms    | −70 ms     |
| Failure Rate    | 11%       | 7%        | −4%        |

### UI Behavior

Positive improvements:

```
green
```

Negative:

```
red
```

Latency improvement also **green** if lower.

Example Layout

```
-----------------------------------------------------------
Metric             Prompt v1     Prompt v2     Difference
-----------------------------------------------------------
Accuracy           82%           88%           +6%
Consistency        79%           83%           +4%
Avg Latency        780 ms        710 ms        -70 ms
Failure Rate       11%           7%            -4%
-----------------------------------------------------------
```

# Visualization Panel

Below the table add **small charts**.

Use **two horizontal charts**.

## Chart 1

Title

```
Accuracy Comparison
```

Bar chart:

```
Prompt v1 |█████████████████ 82%
Prompt v2 |██████████████████████ 88%
```

## Chart 2

Title

```
Latency Comparison
```

Bar chart:

```
Prompt v1 |██████████████ 780ms
Prompt v2 |████████████ 710ms
```

Charts are purely **visual**.

# Improvement Summary Panel

Add a **highlight card** below charts.

### Title

```
Experiment Summary
```

Content

```
Accuracy improvement
+6%

Latency improvement
-70 ms

Consistency improvement
+4%
```

### Visual

Use **three metric cards**.

Example:

```
+6%
Accuracy Improvement

-70 ms
Latency Reduction

+4%
Consistency Improvement
```

# Experiment Status

Display a **status badge**.

Example:

```
Status: COMPLETED
```

Color:

```
blue
```

Location: right side of the summary section.

# Decision Navigation

Add **CTA button** that leads to Screen 3.

Button text:

```
Run Statistical Validation
```

Optional subtext:

```
Verify if improvement is statistically significant
```

Mock Data (for Prototype)

Use static JSON data.

```json
experiment = {
 name: "Product Search Prompt Optimization",
 dataset_size: 200,
 baseline: "Prompt v1",
 candidate: "Prompt v2",
 metrics: [
  { metric:"Accuracy", v1:82, v2:88, diff:"+6%" },
  { metric:"Consistency", v1:79, v2:83, diff:"+4%" },
  { metric:"Latency", v1:"780 ms", v2:"710 ms", diff:"-70 ms" },
  { metric:"Failure Rate", v1:"11%", v2:"7%", diff:"-4%" }
 ]
}
```

# UI Design Style

Use a **modern SaaS analytics look**.

Recommended stack:

```
React
Next.js
Tailwind
shadcn/ui
Recharts (for charts)
```

Color palette:

```
Primary: #2563EB
Success: #22C55E
Warning: #F59E0B
Danger: #EF4444
```

# UX Goal

After viewing Screen 2, stakeholders should conclude:

```
The system can measure AI improvements objectively.
```


