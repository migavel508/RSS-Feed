# RSS Feed Frontend

This is the frontend application for the RSS Feed aggregator. It provides a user interface to view and filter RSS feeds from various news sources.

## Features

- View RSS feeds in a clean, modern interface
- Filter feeds by:
  - Language
  - Region
  - State
  - Source
- Real-time updates
- Responsive design for mobile and desktop

## Configuration

### API Configuration

The backend API endpoint is configured in `src/config.ts`. By default, it points to `http://localhost:8000`.

To change the API endpoint:
1. Create a `.env` file in the root directory
2. Add the following line:
   ```
   REACT_APP_API_URL=your_api_url
   ```

### Sample Output

The RSS Feed Dashboard displays feeds in the following format:

```typescript
interface Feed {
  id: string;
  title: string;
  description: string;
  link: string;
  published_date: string;
  source: string;
  language: string;
  region: string;
  state: string;
}
```

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`

Launches the test runner in the interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

## Project Structure

```
src/
  ├── components/           # React components
  │   └── RSSFeedDashboard.tsx  # Main dashboard component
  ├── App.tsx              # Root component
  ├── index.tsx           # Entry point
  └── config.ts           # Configuration file
```

## Adding New Features

To add new features to the dashboard:

1. Create a new component in `src/components/`
2. Import and use it in `RSSFeedDashboard.tsx`
3. Add any new API calls in the appropriate component

## Development

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

Make sure the backend server is running before starting the frontend application.
