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
  name: string;
  url: string;
  language: string;
  region: string;
  state: string;
}

interface Article {
  id: number;
  title: string;
  link: string;
  summary: string;
  published: string;
  feed: Feed;
}

const RSSFeedDashboard: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:8000/api/articles');
      setArticles(response.data || []);
    } catch (err) {
      setError('Failed to fetch RSS articles. Please try again later.');
      console.error('Error fetching articles:', err);
      setArticles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const downloadExcel = () => {
    if (!articles.length) return;
    
    const exportData = articles.map(article => ({
      Title: article.title,
      Source: article.feed.name,
      URL: article.link,
      Summary: article.summary,
      Published: new Date(article.published).toLocaleDateString(),
      Language: article.feed.language,
      Region: article.feed.region,
      State: article.feed.state
    }));
    
    const worksheet = XLSX.utils.json_to_sheet(exportData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'RSS Articles');
    XLSX.writeFile(workbook, 'rss_articles.xlsx');
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
            onClick={fetchArticles}
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
            disabled={loading || !articles.length}
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
      ) : articles.length > 0 ? (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Published Date</TableCell>
                <TableCell>Summary</TableCell>
                <TableCell>Link</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {articles.map((article) => (
                <TableRow key={article.id}>
                  <TableCell>{article.title}</TableCell>
                  <TableCell>{article.feed.name}</TableCell>
                  <TableCell>
                    {new Date(article.published).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="description">
                    {article.summary.length > 100
                      ? `${article.summary.substring(0, 100)}...`
                      : article.summary
                    }
                  </TableCell>
                  <TableCell>
                    <Button href={article.link} target="_blank" rel="noopener noreferrer">
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
          No RSS articles available. Try refreshing the page.
        </Alert>
      )}
    </Box>
  );
};

export default RSSFeedDashboard; 