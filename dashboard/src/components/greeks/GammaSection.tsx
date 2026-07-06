import GreekSection from './GreekSection';

export default function GammaSection({ currency }: { currency: string }) {
  return (
    <GreekSection
      greek="gamma"
      label="GAMMA"
      color="#33ff66"
      currency={currency}
      valueFmt={(v) => v.toFixed(6)}
    />
  );
}
