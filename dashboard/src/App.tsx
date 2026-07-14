import Dashboard from './components/Dashboard';
import { useSettings } from './settings/store';

export default function App() {
  const { currency } = useSettings();
  return <Dashboard currency={currency} />;
}
