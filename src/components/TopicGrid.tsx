import type { Topic } from '@/data/topics';
import { TopicCard } from './TopicCard';

export function TopicGrid({ topics, activeId, onSelect }: { topics: Topic[]; activeId: string; onSelect: (id: string) => void }) {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {topics.map((topic) => (
        <TopicCard key={topic.id} topic={topic} active={activeId === topic.id} onSelect={() => onSelect(topic.id)} />
      ))}
    </div>
  );
}
