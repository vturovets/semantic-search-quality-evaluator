# AI Product Experiment Lab: 3-screen UX concept

Product name: AI Product Experiment Lab

Tagline:

> *Validate AI product features with statistical confidence.

Goal - to make the product look like a real AI product experimentation platform rather than a technical prototype.

The stack behind the scenes:

- Medusa (product catalog)

- LLM search

- Langfuse (observability)

- Promptfoo (testing)

- Hypothesis Testing Tool

The UX principal: capability -> question -> evidence -> decision

## Screen 1 — AI Product Search (User Experience)

This screen demonstrates the **AI feature itself**.

Purpose:  Show that the product supports **natural language search**.

UI Layout 

```
--------------------------------------------------
AI Product Search
--------------------------------------------------

Search using natural language

[ Find cheap winter running shoes          🔍 ]

Interpreted filters
Category: shoes
Type: running
Season: winter
Price: low

Results
--------------------------------------------
1. Waterproof Winter Running Shoes
2. Budget Trail Running Shoes
3. Lightweight Winter Trainers
--------------------------------------------

Execution metrics
Latency: 740 ms
LLM tokens: 920
Trace ID: 92AF14
--------------------------------------------------
```

### What stakeholders see

Product managers understand:

- natural language search

- filter interpretation

- search results

Engineers see:

- latency

- trace id (Langfuse)

## Screen 2 — AI Experiment Dashboard

Purpose: Show **AI evaluation experiments**.

UI Layout

```
--------------------------------------------------
AI Experiment Dashboard
--------------------------------------------------

Experiment: Product Search Prompt Optimization

Dataset
200 queries

Models tested
Prompt v1
Prompt v2

Results
--------------------------------------------
Metric             Prompt v1    Prompt v2
--------------------------------------------
Accuracy           82%          88%
Consistency        79%          83%
Avg latency        780 ms       710 ms
--------------------------------------------

Improvement
+6% accuracy

Experiment status
Completed
--------------------------------------------------
```

### Data source

- Promptfoo

- Langfuse traces

- evaluation dataset

## Screen 3 — Release Decision

This screen contains **statistical validation**.

Purpose: Turn AI metrics into **product decisions**.

UA layout

```
--------------------------------------------------
AI Release Validation
--------------------------------------------------

Feature tested
AI Search Prompt v2

Statistical Evaluation

Null hypothesis
Prompt v2 is NOT better than Prompt v1

Dataset size
200 queries

Hypothesis test result
p-value = 0.018

Confidence level
95%

Conclusion
Reject null hypothesis

--------------------------------------------------

Recommendation

SAFE TO RELEASE

Expected product impact
Search success rate +5–7%
--------------------------------------------------
```

It shows that your system provides **decision support**.

How the Screens Map to the Architecture

```
Screen 1
User query → LLM → Medusa

Screen 2
Promptfoo → evaluation dataset → metrics

Screen 3
Hypothesis Testing Tool → statistical decision
```

Observability:

```
Langfuse traces everything
```

Recommended Technology for the UI

```
React
Next.js
Vercel AI SDK
Tailwind UI
```

This produces a **clean SaaS-like interface**.

# Optional Screen (Later)

If you expand the demo, add:

**Screen 4 — Observability**

Langfuse traces:

- prompts

- responses

- latency

- tokens

This appeals to **engineering teams**.
