import { useIVSurface } from './hooks/useIVSurface';
import { useIVCurves } from './hooks/useIVCurves';
import Dashboard from './components/Dashboard';

const CURRENCY = 'BTC';

export default function App() {
  const IVSurfaceQuery = useIVSurface(CURRENCY);
  const IVCurvesQuery = useIVCurves(CURRENCY);
  return <Dashboard currency={CURRENCY} IVSurfaceQuery={IVSurfaceQuery} IVCurvesQuery={IVCurvesQuery} />;
}
