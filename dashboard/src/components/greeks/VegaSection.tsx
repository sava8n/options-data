import GreekSection from './GreekSection';

export default function VegaSection({ currency }: { currency: string }) {
  return (
    <GreekSection
      greek="vega"
      label="VEGA"
      color="#ffb000"
      currency={currency}
      valueFmt={(v) => v.toFixed(2)}
    />
  );
}
