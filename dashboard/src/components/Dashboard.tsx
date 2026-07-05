import Header from './Header';
import StatusBar from './StatusBar';
import IVSurfaceSection from './iv/IVSurfaceSection';
import IVCurvesSection from './iv/IVCurvesSection';
import TermStructureSection from './iv/TermStructureSection';
import GreeksSection from './greeks/GreeksSection';
import OIByExpirationSection from './oi/OIByExpirationSection';
import OIByStrikeSection from './oi/OIByStrikeSection';

export default function Dashboard({ currency }: { currency: string }) {
  return (
    <div className="dashboard">
      <Header currency={currency} />

      <GreeksSection currency={currency} />

      <OIByStrikeSection currency={currency} />

      <OIByExpirationSection currency={currency} />

      <div className="panels">
        <IVSurfaceSection currency={currency} />
        <IVCurvesSection currency={currency} />
        <TermStructureSection currency={currency} />
      </div>

      <StatusBar currency={currency} />
    </div>
  );
}
