import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2de3c4', // mintgrün
      contrastText: '#212121',
    },
    secondary: {
      main: '#a2f5e2', // helleres Mint
      contrastText: '#212121',
    },
    background: {
      default: '#e8f8f6',
      paper: '#ffffff',
    },
    text: {
      primary: '#212121',
      secondary: '#3a3a3a',
    },
  },
  typography: {
    fontFamily: 'Inter, Roboto, Arial, sans-serif',
    fontWeightRegular: 400,
    fontWeightBold: 600,
    h5: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 14,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          boxShadow: 'none',
          transition: 'all 0.2s',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          transition: 'box-shadow 0.3s',
        },
      },
    },
  },
});

export default theme;
