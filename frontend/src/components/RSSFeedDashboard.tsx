import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import RefreshIcon from '@mui/icons-material/Refresh';
import axios from 'axios';
import * as XLSX from 'xlsx';

interface Feed {
  id: number;
  title: string;
  description: string;
  link: string;
  published_date: string;
  source: string;
  language: string;
  region: string;
  state: string;
  content: string;
  author: string;
  image_urls: string[];
  keywords: string[];
  summary: string;
  extraction_success: boolean;
}

const RSSFeedDashboard: React.FC = () => {
  const [feeds, setFeeds] = useState<Feed[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchFeeds = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/feeds/');
      setFeeds(response.data || []);
    } catch (err) {
      setError('Failed to fetch RSS feeds. Please try again later.');
      console.error('Error fetching feeds:', err);
      setFeeds([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeeds();
  }, []);

  const downloadExcel = () => {
    if (!feeds.length) return;
    
    const exportData = feeds.map(feed => ({
      Title: feed.title,
      Source: feed.source,
      URL: feed.link,
      Summary: feed.summary || feed.description,
      Published: new Date(feed.published_date).toLocaleDateString(),
      Language: feed.language,
      Region: feed.region,
      State: feed.state,
      Author: feed.author,
      Keywords: feed.keywords?.join(', ') || ''
    }));
    
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'RSS Feeds');
    XLSX.writeFile(workbook, 'rss_feeds.xlsx');
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          RSS Feed Dashboard
        </Typography>
        <Box>
          <Button
            startIcon={<RefreshIcon />}
            onClick={fetchFeeds}
            sx={{ mr: 2 }}
            variant="contained"
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            onClick={downloadExcel}
            variant="contained"
            color="secondary"
            disabled={loading || !feeds.length}
          >
            Download Excel
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : feeds.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Published Date</TableCell>
                <TableCell>Summary</TableCell>
                <TableCell>Language</TableCell>
                <TableCell>State</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {feeds.map((feed) => (
                <TableRow key={feed.id}>
                  <TableCell>{feed.title}</TableCell>
                  <TableCell>{feed.source}</TableCell>
                  <TableCell>
                    {feed.published_date ? new Date(feed.published_date).toLocaleDateString() : 'N/A'}
                  </TableCell>
                  <TableCell>
                    {(feed.summary || feed.description || '').length > 100
                      ? `${(feed.summary || feed.description || '').substring(0, 100)}...`
                      : (feed.summary || feed.description || 'No summary available')
                    }
                  </TableCell>
                  <TableCell>{feed.language}</TableCell>
                  <TableCell>{feed.state}</TableCell>
                  <TableCell>
                    <Button href={feed.link} target="_blank" rel="noopener noreferrer">
                      Visit
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      ) : (
        <Alert severity="info" sx={{ mb: 3 }}>
          No RSS feeds available. Try refreshing the page.
        </Alert>
      )}
    </Box>
  );
};

export default RSSFeedDashboard; 