// Design system values

import { UIConstants } from '../types/shared';

export const uiConstants: UIConstants = {
  maxContentWidth: '1280px',
  breakpoints: {
    mobile: '640px',
    tablet: '768px',
    desktop: '1024px'
  },
  colors: {
    primary: '#3B82F6', // blue-500
    success: '#10B981', // emerald-500
    warning: '#F59E0B', // amber-500
    danger: '#EF4444'   // red-500
  },
  spacing: {
    section: '2rem',    // 32px
    card: '1.5rem',     // 24px
    element: '1rem'     // 16px
  }
};

// Tailwind CSS class mappings for consistency
export const designTokens = {
  // Layout
  maxWidth: 'max-w-7xl', // 1280px
  container: 'mx-auto px-4 sm:px-6 lg:px-8',
  
  // Cards
  card: 'bg-white rounded-2xl shadow-sm border border-gray-200',
  cardHover: 'hover:shadow-md transition-shadow duration-200',
  
  // Buttons
  buttonPrimary: 'px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium',
  buttonSecondary: 'px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 font-medium text-gray-700',
  
  // Status colors
  statusSuccess: 'bg-green-100 text-green-800',
  statusWarning: 'bg-yellow-100 text-yellow-800',
  statusDanger: 'bg-red-100 text-red-800',
  statusInfo: 'bg-blue-100 text-blue-800',
  
  // Typography
  headingLarge: 'text-3xl font-bold text-gray-900',
  headingMedium: 'text-xl font-semibold text-gray-900',
  headingSmall: 'text-lg font-semibold text-gray-900',
  bodyText: 'text-gray-600',
  captionText: 'text-sm text-gray-500'
};