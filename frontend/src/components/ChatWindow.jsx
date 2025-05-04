import React, { useState, useRef } from 'react';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Slide from '@mui/material/Slide';
import Fade from '@mui/material/Fade';
import SendIcon from '@mui/icons-material/Send';
import axios from 'axios';

export default function ChatWindow({ selectedSession }) {
  const [messages, setMessages] = useState([]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const lastMsgRef = useRef(null);
  const topRef = useRef(null);
  const PAGE_SIZE = 20;

  // Nachrichten laden, wenn Session wechselt
  React.useEffect(() => {
    if (selectedSession) {
      setMessages([]);
      setOffset(0);
      setHasMore(true);
      loadMessages(0, true);
    } else {
      setMessages([]);
      setOffset(0);
      setHasMore(false);
    }
    // eslint-disable-next-line
  }, [selectedSession]);

  const loadMessages = async (newOffset, replace = false) => {
    if (!selectedSession) return;
    const res = await axios.get(`/sessions/${selectedSession.id}/messages?limit=${PAGE_SIZE}&offset=${newOffset}`);
    if (res.data.length < PAGE_SIZE) setHasMore(false);
    setOffset(newOffset + res.data.length);
    setMessages((msgs) => replace ? res.data : [...res.data, ...msgs]);
  };

  // Infinite Scroll nach oben
  const handleScroll = (e) => {
    if (e.target.scrollTop < 100 && hasMore && !loading) {
      loadMessages(offset);
    }
  };

  const sendPrompt = async () => {
    if (!prompt.trim() || !selectedSession) return;
    setLoading(true);
    setError('');
    try {
      // User Message
      const userRes = await axios.post(`/sessions/${selectedSession.id}/message`, { sender: 'user', text: prompt });
      setMessages((msgs) => [...msgs, userRes.data]);
      setPrompt('');
      // Assistant Message (LLM)
      const llmRes = await axios.post('/chat', { prompt, model: 'llama2' });
      const assistantRes = await axios.post(`/sessions/${selectedSession.id}/message`, { sender: 'assistant', text: llmRes.data.response });
      setMessages((msgs) => [...msgs, assistantRes.data]);
      setTimeout(() => {
        lastMsgRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (e) {
      setError('Fehler beim Abrufen der Antwort.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Fade in>
      <Paper elevation={4} sx={{ p: 3, minHeight: 400, display: 'flex', flexDirection: 'column', background: 'linear-gradient(135deg, #e8f8f6 0%, #a2f5e2 100%)' }}>
        <Box flex={1} mb={2} onScroll={handleScroll} ref={topRef}
  sx={{
    overflowY: 'auto',
    minHeight: 300,
    maxHeight: 500,
    pr: 2,
    scrollbarWidth: 'thin', // für Firefox
    '&::-webkit-scrollbar': { width: '8px' }, // für Chrome
    '&::-webkit-scrollbar-thumb': { background: '#b2dfdb', borderRadius: 4 }
  }}
>

          {messages.map((msg, i) => (
            <Slide key={i} direction="up" in mountOnEnter unmountOnExit>
              <Box ref={i === messages.length - 1 ? lastMsgRef : null} mb={2} display="flex" justifyContent={msg.sender === 'user' ? 'flex-end' : 'flex-start'}>
                <Paper sx={{ p: 2, bgcolor: msg.sender === 'user' ? '#bee3f8' : '#fbd38d', borderRadius: 3, maxWidth: 380 }}>
                  <Typography variant="body1">{msg.text}</Typography>
                  <Typography variant="caption" color="text.secondary">{msg.sender} • {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : ''}</Typography>
                </Paper>
              </Box>
            </Slide>
          ))}
          <div ref={lastMsgRef} />
        </Box>
        <Box display="flex" alignItems="center" gap={2}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Nachricht eingeben..."
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') sendPrompt(); }}
            disabled={loading || !selectedSession}
          />
          <Button variant="contained" color="primary" endIcon={<SendIcon />} onClick={sendPrompt} disabled={loading || !selectedSession}>
            Senden
          </Button>
        </Box>
        {error && <Typography color="error" mt={2}>{error}</Typography>}
        {loading && <CircularProgress sx={{ mt: 2 }} />}
      </Paper>
    </Fade>
  );
}

