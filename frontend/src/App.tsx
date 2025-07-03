import React from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import RSSFeedDashboard from './components/RSSFeedDashboard';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <RSSFeedDashboard />
      </Container>
    </ThemeProvider>
  );
}

export default App;
