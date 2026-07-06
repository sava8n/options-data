import GreekSection from './GreekSection';

export default function DeltaSection({ currency }: { currency: string }) {
  return (
    <GreekSection
      greek="delta"
      label="DELTA"
      color="#4aa3ff"
      currency={currency}
      valueFmt={(v) => v.toFixed(3)}
    />
  );
}
