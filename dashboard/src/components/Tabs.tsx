export type TabId = 'positioning' | 'volatility' | 'chain';

const TABS: { id: TabId; label: string }[] = [
  { id: 'positioning', label: 'POSITIONING' },
  { id: 'volatility', label: 'VOLATILITY' },
  { id: 'chain', label: 'CHAIN' },
];

interface Props {
  active: TabId;
  onSelect: (tab: TabId) => void;
}

export default function Tabs({ active, onSelect }: Props) {
  return (
    <nav className="tabs">
      {TABS.map(({ id, label }) => (
        <button
          key={id}
          type="button"
          className={`tabs__tab${id === active ? ' tabs__tab--active' : ''}`}
          onClick={() => onSelect(id)}
        >
          {label}
        </button>
      ))}
    </nav>
  );
}
