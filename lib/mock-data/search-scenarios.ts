// Search query and result data

import { LegacySearchScenario } from '../types/search';

export const searchScenarios: Record<string, LegacySearchScenario> = {
  "Find cheap winter running shoes": {
    id: "search-winter-running-shoes",
    query: "Find cheap winter running shoes",
    interpretation: {
      filters: [
        { label: "Category", value: "Shoes" },
        { label: "Type", value: "Running" },
        { label: "Season", value: "Winter" },
        { label: "Price", value: "Low" },
        { label: "Feature", value: "Waterproof" }
      ],
      summary: "Budget-oriented winter running footwear with weather protection.",
      confidence: "High",
      structuredOutput: {
        "category": "shoes",
        "type": "running",
        "season": "winter",
        "price": "low",
        "feature": "waterproof"
      }
    },
    interpretedFilters: {
      filters: [
        { label: "Category", value: "Shoes" },
        { label: "Type", value: "Running" },
        { label: "Season", value: "Winter" },
        { label: "Price", value: "Low" },
        { label: "Feature", value: "Waterproof" }
      ],
      summary: "Budget-oriented winter running footwear with weather protection.",
      confidence: "High",
      structuredOutput: {
        "category": "shoes",
        "type": "running",
        "season": "winter",
        "price": "low",
        "feature": "waterproof"
      }
    },
    results: [
      {
        id: "1",
        name: "Waterproof Winter Running Shoes",
        description: "Lightweight insulated runner for cold-weather training",
        price: "€79",
        priceValue: 79,
        currency: "EUR",
        tags: ["Winter", "Waterproof", "Running"],
        badge: "Best match",
        image: "/placeholder-shoe-1.jpg"
      },
      {
        id: "2",
        name: "Budget Trail Running Shoes",
        description: "Durable all-weather model for mixed terrain",
        price: "€64",
        priceValue: 64,
        currency: "EUR",
        tags: ["Trail", "Budget", "Grip"],
        image: "/placeholder-shoe-2.jpg"
      },
      {
        id: "3",
        name: "Lightweight Winter Trainers",
        description: "Daily-use cold-season trainer with comfort lining",
        price: "€69",
        priceValue: 69,
        currency: "EUR",
        tags: ["Winter", "Lightweight", "Everyday"],
        image: "/placeholder-shoe-3.jpg"
      }
    ],
    metrics: {
      latencyMs: 740,
      wordCount: 920,
      traceId: "92AF14",
      status: "Completed"
    },
    executionMetrics: {
      latency: 740,
      wordCount: 920,
      traceId: "92AF14",
      status: "Completed"
    }
  },
  "sandals for hot weather": {
    id: "search-hot-weather-sandals",
    query: "sandals for hot weather",
    interpretation: {
      filters: [
        { label: "Category", value: "Sandals" },
        { label: "Season", value: "Summer" },
        { label: "Climate", value: "Hot" },
        { label: "Breathability", value: "High" }
      ],
      summary: "Breathable summer sandals optimized for hot weather comfort.",
      confidence: "High",
      structuredOutput: {
        "category": "sandals",
        "season": "summer",
        "climate": "hot",
        "breathability": "high"
      }
    },
    interpretedFilters: {
      filters: [
        { label: "Category", value: "Sandals" },
        { label: "Season", value: "Summer" },
        { label: "Climate", value: "Hot" },
        { label: "Breathability", value: "High" }
      ],
      summary: "Breathable summer sandals optimized for hot weather comfort.",
      confidence: "High",
      structuredOutput: {
        "category": "sandals",
        "season": "summer",
        "climate": "hot",
        "breathability": "high"
      }
    },
    results: [
      {
        id: "4",
        name: "Breathable Sport Sandals",
        description: "Ultra-ventilated design for maximum airflow",
        price: "€45",
        priceValue: 45,
        currency: "EUR",
        tags: ["Summer", "Breathable", "Sport"],
        badge: "Best match",
        image: "/placeholder-sandal-1.jpg"
      },
      {
        id: "5",
        name: "Lightweight Beach Sandals",
        description: "Quick-dry material perfect for hot climates",
        price: "€32",
        priceValue: 32,
        currency: "EUR",
        tags: ["Beach", "Quick-dry", "Lightweight"],
        image: "/placeholder-sandal-2.jpg"
      }
    ],
    metrics: {
      latencyMs: 680,
      wordCount: 850,
      traceId: "8B2C91",
      status: "Completed"
    },
    executionMetrics: {
      latency: 680,
      wordCount: 850,
      traceId: "8B2C91",
      status: "Completed"
    }
  },
  "kids shoes under €50": {
    id: "search-kids-shoes-budget",
    query: "kids shoes under €50",
    interpretation: {
      filters: [
        { label: "Category", value: "Shoes" },
        { label: "Age Group", value: "Kids" },
        { label: "Price", value: "Under €50" },
        { label: "Durability", value: "High" }
      ],
      summary: "Affordable children's footwear with durability focus.",
      confidence: "High",
      structuredOutput: {
        "category": "shoes",
        "age_group": "kids",
        "price_max": "50",
        "durability": "high"
      }
    },
    interpretedFilters: {
      filters: [
        { label: "Category", value: "Shoes" },
        { label: "Age Group", value: "Kids" },
        { label: "Price", value: "Under €50" },
        { label: "Durability", value: "High" }
      ],
      summary: "Affordable children's footwear with durability focus.",
      confidence: "High",
      structuredOutput: {
        "category": "shoes",
        "age_group": "kids",
        "price_max": "50",
        "durability": "high"
      }
    },
    results: [
      {
        id: "6",
        name: "Durable Kids Sneakers",
        description: "Reinforced design for active children",
        price: "€42",
        priceValue: 42,
        currency: "EUR",
        tags: ["Kids", "Durable", "Active"],
        badge: "Best match",
        image: "/placeholder-kids-1.jpg"
      },
      {
        id: "7",
        name: "Comfortable School Shoes",
        description: "All-day comfort for growing feet",
        price: "€38",
        priceValue: 38,
        currency: "EUR",
        tags: ["School", "Comfort", "Growing"],
        image: "/placeholder-kids-2.jpg"
      }
    ],
    metrics: {
      latencyMs: 620,
      wordCount: 780,
      traceId: "C4F8A2",
      status: "Completed"
    },
    executionMetrics: {
      latency: 620,
      wordCount: 780,
      traceId: "C4F8A2",
      status: "Completed"
    }
  },
  "waterproof trail shoes": {
    id: "search-waterproof-trail",
    query: "waterproof trail shoes",
    interpretation: {
      filters: [
        { label: "Category", value: "Shoes" },
        { label: "Type", value: "Trail" },
        { label: "Feature", value: "Waterproof" },
        { label: "Terrain", value: "Off-road" }
      ],
      summary: "Weather-resistant trail footwear for outdoor adventures.",
      confidence: "High",
      structuredOutput: {
        "category": "shoes",
        "type": "trail",
        "feature": "waterproof",
        "terrain": "off-road"
      }
    },
    interpretedFilters: {
      filters: [
        { label: "Category", value: "Shoes" },
        { label: "Type", value: "Trail" },
        { label: "Feature", value: "Waterproof" },
        { label: "Terrain", value: "Off-road" }
      ],
      summary: "Weather-resistant trail footwear for outdoor adventures.",
      confidence: "High",
      structuredOutput: {
        "category": "shoes",
        "type": "trail",
        "feature": "waterproof",
        "terrain": "off-road"
      }
    },
    results: [
      {
        id: "8",
        name: "All-Weather Trail Runners",
        description: "Waterproof membrane with superior grip",
        price: "€95",
        priceValue: 95,
        currency: "EUR",
        tags: ["Trail", "Waterproof", "Grip"],
        badge: "Best match",
        image: "/placeholder-trail-1.jpg"
      },
      {
        id: "9",
        name: "Hiking Trail Shoes",
        description: "Rugged construction for challenging terrain",
        price: "€87",
        priceValue: 87,
        currency: "EUR",
        tags: ["Hiking", "Rugged", "Terrain"],
        image: "/placeholder-trail-2.jpg"
      }
    ],
    metrics: {
      latencyMs: 820,
      wordCount: 1050,
      traceId: "D7E3B9",
      status: "Completed"
    },
    executionMetrics: {
      latency: 820,
      wordCount: 1050,
      traceId: "D7E3B9",
      status: "Completed"
    }
  }
};

export const defaultSearchQuery = "Find cheap winter running shoes";
export const samplePrompts = Object.keys(searchScenarios);