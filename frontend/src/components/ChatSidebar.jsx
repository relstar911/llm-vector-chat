import React, { useEffect, useState } from "react";
import { Drawer, List, ListItem, ListItemText, Divider, Box, Typography, Button, IconButton, Snackbar } from "@mui/material";
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import UndoIcon from '@mui/icons-material/Undo';
import axios from "axios";

import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Checkbox from '@mui/material/Checkbox';
import FormControlLabel from '@mui/material/FormControlLabel';

export default function ChatSidebar({ onSelectSession, selectedSessionId }) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteSessionId, setDeleteSessionId] = useState(null);
  const [removeVectors, setRemoveVectors] = useState(true);

  const handleDeleteSession = (sessionId) => {
    setDeleteSessionId(sessionId);
    setRemoveVectors(true);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteSession = async () => {
    if (deleteSessionId) {
      // Vor dem Löschen Session-Daten sichern
      const sessionToDelete = sessions.find(s => s.id === deleteSessionId);
      let messages = [];
      try {
        const res = await axios.get(`/sessions/${deleteSessionId}/messages?limit=1000&offset=0`);
        messages = res.data;
      } catch {}
      setUndoData({ session: sessionToDelete, messages, removeVectors });
      await axios.delete(`/sessions/${deleteSessionId}?remove_vectors=${removeVectors}`);
      fetchSessions();
      if (selectedSessionId === deleteSessionId) {
        onSelectSession(null);
      }
      setDeleteSessionId(null);
      setDeleteDialogOpen(false);
      setSnackbarOpen(true);
    }
  };

  const handleUndo = async () => {
    if (!undoData) return;
    // Serialisiere Daten für Restore sauber
    const session = {
      id: String(undoData.session.id),
      title: undoData.session.title || null,
      created_at: undoData.session.created_at || null
    };
    const messages = (undoData.messages || []).map(msg => ({
      id: String(msg.id),
      sender: msg.sender,
      text: msg.text,
      timestamp: msg.timestamp || null
    }));
    const payload = {
      session,
      messages,
      restore_vectors: !undoData.removeVectors
    };
    console.log("Restore-Request", JSON.stringify(payload, null, 2));
    try {
      await axios.post('/sessions/restore', payload);
      fetchSessions();
      setSnackbarOpen(false);
      setUndoData(null);
    } catch (err) {
      setSnackbarOpen(false);
      setUndoData(null);
      alert('Fehler beim Wiederherstellen der Session: ' + (err?.response?.data?.error || err.message));
    }
  };



  const handleCancelDelete = () => {
    setDeleteDialogOpen(false);
    setDeleteSessionId(null);
  };
  const [sessions, setSessions] = useState([]);

  const fetchSessions = () => {
    axios.get("/sessions").then(res => {
      setSessions(res.data);
    });
  };

  // Undo Snackbar State
  const [undoData, setUndoData] = useState(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleNewSession = async () => {
    const res = await axios.post('/sessions', { title: null });
    fetchSessions();
    onSelectSession(res.data);
  };

  // Sessions können optional später gelöscht werden
  // Undo-Logik kann nachgerüstet werden, wenn gewünscht

  return (
    <Drawer variant="permanent" anchor="left" sx={{ width: 320, flexShrink: 0, [`& .MuiDrawer-paper`]: { width: 320, boxSizing: 'border-box', background: '#e8f9f3' } }}>
      <Box sx={{ p: 2, bgcolor: '#b2f5ea', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: '#222' }}>Chats</Typography>
        <Button startIcon={<AddIcon />} variant="contained" color="primary" size="small" onClick={handleNewSession} sx={{ borderRadius: 2, fontWeight: 600 }}>Neu</Button>
      </Box>
      <Divider />
      <List>
        {sessions.length === 0 && (
          <ListItem>
            <ListItemText primary="Keine Sessions vorhanden" />
          </ListItem>
        )}
        {sessions.map(session => (
          <ListItem
            button
            key={session.id}
            selected={session.id === selectedSessionId}
            onClick={() => onSelectSession(session)}
            secondaryAction={
              <IconButton edge="end" aria-label="delete" onClick={e => { e.stopPropagation(); handleDeleteSession(session.id); }}>
                <DeleteIcon />
              </IconButton>
            }
          >
            <ListItemText
              primary={session.title ? session.title : `Session ${session.id.slice(0, 6)}`}
              secondary={session.created_at ? new Date(session.created_at).toLocaleString() : ""}
            />
          </ListItem>
        ))}
      </List>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
        message={
          <span>
            Session gelöscht
            <Button color="secondary" size="small" onClick={handleUndo} startIcon={<UndoIcon />}>Undo</Button>
          </span>
        }
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
      <Dialog open={deleteDialogOpen} onClose={handleCancelDelete}>
        <DialogTitle>Session löschen</DialogTitle>
        <DialogContent>
          <Typography>Möchtest du diese Session wirklich löschen?</Typography>
          <FormControlLabel
            control={<Checkbox checked={removeVectors} onChange={e => setRemoveVectors(e.target.checked)} />}
            label="Auch aus der Vektor-Datenbank entfernen"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete}>Abbrechen</Button>
          <Button onClick={confirmDeleteSession} color="error" variant="contained">Löschen</Button>
        </DialogActions>
      </Dialog>
    </Drawer>
  );
}
