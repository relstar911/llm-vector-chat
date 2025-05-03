import React, { useState } from 'react';
import Container from '@mui/material/Container';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import ChatWindow from './components/ChatWindow';
import QueryPanel from './components/QueryPanel';
import ChatSidebar from './components/ChatSidebar';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import LogoDevIcon from '@mui/icons-material/LogoDev';

export default function App() {
  const [tab, setTab] = useState(0);
  const [selectedSession, setSelectedSession] = useState(null);

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#f9fdfc' }}>
      {tab === 0 && (
        <ChatSidebar
          onSelectSession={setSelectedSession}
          selectedSessionId={selectedSession?.id || null}
        />
      )}
      <Container maxWidth="md" sx={{ py: 5, flex: 1 }}>
        <Box display="flex" alignItems="center" mb={3} gap={2}>
          <LogoDevIcon color="primary" sx={{ fontSize: 40 }} />
          <Typography variant="h5" fontWeight={700} color="primary.main">
            LLM Chat Vector App
          </Typography>
        </Box>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }}>
          <Tab label="Chat" />
          <Tab label="Suche" />
        </Tabs>
        {tab === 0 && <ChatWindow selectedSession={selectedSession} />}
        {tab === 1 && <QueryPanel />}
      </Container>
    </Box>
  );
}
