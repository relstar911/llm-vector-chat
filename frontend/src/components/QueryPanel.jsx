import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Slide from '@mui/material/Slide';
import Slider from '@mui/material/Slider';
import axios from 'axios';

export default function QueryPanel() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [threshold, setThreshold] = useState(0.5);

  const search = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await axios.post('/query', { query, score_threshold: threshold });
      setResults(res.data.results || []);
    } catch (e) {
      setError('Fehler bei der Suche.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={4} sx={{ p: 3, minHeight: 300, background: 'linear-gradient(135deg, #e8f8f6 0%, #a2f5e2 100%)' }}>
      <Box mb={2}>
        <Typography gutterBottom sx={{ fontWeight: 500 }}>
          Ähnlichkeitsschwelle: {Math.round(threshold * 100)}%
        </Typography>
        <Slider
          value={threshold}
          min={0}
          max={1}
          step={0.01}
          onChange={(_, v) => setThreshold(v)}
          valueLabelDisplay="auto"
          sx={{ color: 'primary.main', mb: 1 }}
        />
      </Box>
      <Box display="flex" gap={1} mb={2}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Suche nach ähnlichen Chats..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') search(); }}
          sx={{ bgcolor: 'white', borderRadius: 2 }}
          InputProps={{ style: { fontSize: 18 } }}
        />
        <Button onClick={search} variant="contained" color="primary" sx={{ minWidth: 48, minHeight: 48, borderRadius: 2, boxShadow: 3 }} disabled={loading || !query.trim()}>
          Suchen
        </Button>
      </Box>
      {error && <Typography color="error" mb={1}>{error}</Typography>}
      {loading && <Box display="flex" justifyContent="center" mt={2}><CircularProgress color="primary" /></Box>}
      <Box mt={2}>
        {results.length === 0 && !loading && (
          <Typography sx={{ opacity: 0.7, textAlign: 'center', mt: 3 }}>
            Keine ähnlichen Chats gefunden.
          </Typography>
        )}
        {results.map((res, i) => (
          <Slide key={i} direction="up" in mountOnEnter unmountOnExit>
            <Paper sx={{ p: 2, mb: 2, bgcolor: 'secondary.main', color: 'secondary.contrastText', borderRadius: 3, boxShadow: 2 }}>
              <Typography variant="subtitle2" sx={{ opacity: 0.7 }}>Prompt:</Typography>
              <Typography>{res.prompt}</Typography>
              <Typography variant="subtitle2" sx={{ opacity: 0.7, mt: 1 }}>Antwort:</Typography>
              <Typography>{res.response}</Typography>
              <Typography variant="caption" sx={{ opacity: 0.7, mt: 1 }}>
                Ähnlichkeit: {(res.score * 100).toFixed(1)}%
              </Typography>
            </Paper>
          </Slide>
        ))}
      </Box>
    </Paper>
  );
}
