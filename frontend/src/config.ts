// API Configuration
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Refresh interval for fetching feeds (in milliseconds)
export const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// Available feed filters
export const FILTERS = {
  languages: ['en', 'hi', 'ta', 'mr'],
  regions: ['India'],
  states: [
    'All',
    'Tamil Nadu',
    'Uttar Pradesh',
    'Madhya Pradesh',
    'Kerala',
    'Maharashtra'
  ]
};

// Feed display configuration
export const FEED_CONFIG = {
  itemsPerPage: 10,
  maxDescriptionLength: 200
};

// Date format configuration
export const DATE_FORMAT = 'MMM DD, YYYY HH:mm';

// Error messages
export const ERROR_MESSAGES = {
  fetchError: 'Failed to fetch RSS feeds. Please try again later.',
  filterError: 'Error applying filters. Please try again.',
  networkError: 'Network error. Please check your internet connection.'
}; 