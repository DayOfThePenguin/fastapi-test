import theme from './theme';
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core';
import PrimarySearchAppBar from './components/PrimarySearchAppBar';
import GraphView from './components/GraphView';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <PrimarySearchAppBar />
      <GraphView />
    </ThemeProvider>
  );
}

export default App;
