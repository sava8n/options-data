import { useIVSurface } from './hooks/useIVSurface';
import Dashboard from './components/Dashboard';

const CURRENCY = 'BTC';

export default function App() {
  const query = useIVSurface(CURRENCY);
  return <Dashboard currency={CURRENCY} query={query} />;
}
