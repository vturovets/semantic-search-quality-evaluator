// Search-related type definitions

export interface SearchScenario {
  id: string;
  query: string;
  interpretedFilters: {
    summary: string;
    confidence: 'High' | 'Medium' | 'Low';
    structuredOutput: Record<string, any>;
    filters: FilterItem[];
  };
  results: ProductResult[];
  executionMetrics: {
    latency: number;
    tokens: number;
    traceId: string;
    status: 'Completed' | 'Processing' | 'Failed';
  };
  traceSteps: TraceStep[];
}

export interface ProductResult {
  id: string;
  name: string;
  description: string;
  price: number;
  currency: string;
  tags: string[];
  imageUrl?: string;
  isBestMatch?: boolean;
}

export interface FilterItem {
  label: string;
  value: string;
}

export interface TraceStep {
  id: string;
  step: string;
  status: 'completed' | 'processing' | 'pending';
  timestamp: string;
  details?: string;
}

// Legacy interface for backward compatibility with existing components
export interface LegacySearchScenario {
  id?: string;
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
    priceValue?: number;
    currency?: string;
    tags: string[];
    badge?: string;
    image: string;
  }[];
  metrics: {
    latencyMs: number;
    wordCount: number;
    traceId: string;
    status: string;
  };
  // Alias for executionMetrics to match test expectations
  executionMetrics?: {
    latency: number;
    wordCount: number;
    traceId: string;
    status: string;
  };
  interpretedFilters?: {
    summary: string;
    confidence: 'High' | 'Medium' | 'Low';
    structuredOutput: Record<string, any>;
    filters: FilterItem[];
  };
}