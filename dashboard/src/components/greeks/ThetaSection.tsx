import GreekSection from './GreekSection';

export default function ThetaSection({ currency }: { currency: string }) {
  return (
    <GreekSection
      greek="theta"
      label="THETA"
      color="#ff6b6b"
      currency={currency}
      valueFmt={(v) => v.toFixed(2)}
    />
  );
}
