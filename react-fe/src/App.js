import theme from './theme';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core';
import PrimarySearchAppBar from './components/PrimarySearchAppBar';
import GraphView from './components/GraphView';
import LoadingAlert from './components/LoadingAlert';

import './App.css';

function App() {
  return (
    <div className="fill-window">
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <PrimarySearchAppBar />

        <GraphView />
        <LoadingAlert />
      </ThemeProvider>
    </div>
  );
}

export default App;
