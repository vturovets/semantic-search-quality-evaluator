
# AI Product Experiment Lab

A frontend prototype demonstrating AI-powered product search with statistical validation and observability features.

## Overview

This is a SaaS-style UI prototype built with React, Next.js, and Tailwind CSS that showcases:

- **Natural Language Search**: Users can search for products using plain English
- **AI Interpretation**: Shows how AI converts natural language into structured filters
- **Observable Execution**: Displays runtime metrics like latency, tokens, and trace IDs
- **Professional SaaS Design**: Clean, modern interface inspired by Stripe, Linear, and Vercel

## Features

### Screen 1: AI Product Search
- Natural language search interface
- Real-time AI interpretation of user queries
- Mock product results with detailed information
- Execution metrics panel showing performance data
- Interactive sample prompts for quick testing
- Expandable structured output and trace details

### Screen 2: AI Experiment Dashboard
- Experiment overview with baseline vs candidate comparison
- Detailed metrics comparison table with improvement indicators
- Visual progress bars for accuracy and latency comparisons
- Experiment status tracking and metadata display
- Professional SaaS-style analytics interface

### Screen 3: Release Decision (Statistical Validation)
- Statistical significance testing with p-values and confidence levels
- Clear business recommendations (Safe to Release, Keep Testing, Do Not Release)
- Hypothesis testing framework with null/alternative hypotheses
- Test inputs and evidence source tracking
- Business-friendly interpretation of statistical results
- Decision process visualization and risk assessment

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **UI**: React 18 with TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Font**: Inter (Google Fonts)

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Mock Data

The prototype includes 4 sample search scenarios:
- "Find cheap winter running shoes" (default)
- "sandals for hot weather"
- "kids shoes under €50"
- "waterproof trail shoes"

Each scenario includes:
- Interpreted filters and AI confidence levels
- Relevant product results with pricing and tags
- Realistic execution metrics (latency, tokens, trace IDs)

## Design System

- **Colors**: Blue accents for AI features, green for success states
- **Layout**: 12-column grid with generous whitespace
- **Cards**: Rounded corners with soft shadows
- **Typography**: Inter font with clear hierarchy
- **Interactive States**: Hover effects and focus states throughout

## Architecture

This is a frontend-only prototype with no backend dependencies. All data is mocked locally to demonstrate the user experience and interface design.

The design supports the broader AI Product Experiment Lab concept of combining:
- AI capability demonstration
- Statistical validation tools
- Observability and monitoring
- Professional SaaS presentation

## Future Screens

This prototype now implements all 3 screens of the AI Product Experiment Lab concept:
1. **AI Product Search** ✅ - User experience demonstration
2. **AI Experiment Dashboard** ✅ - A/B testing and evaluation metrics  
3. **Release Decision** ✅ - Statistical validation and deployment recommendations

## Navigation

The prototype includes a complete navigation flow:
- Start at the **Search** page to see AI-powered product search in action
- Navigate to **Experiments** to view A/B testing results and metrics
- Proceed to **Release Validation** to see statistical significance testing and business recommendations

Each screen builds upon the previous one, demonstrating a complete AI product development and validation workflow.
