import type { Topic } from '@/data/topics';
import clsx from 'clsx';

export function TopicCard({ topic, active, onSelect }: { topic: Topic; active: boolean; onSelect: () => void }) {
  return (
    <article
      className={clsx(
        'cursor-pointer rounded-xl border border-border bg-white px-4 py-3 transition hover:-translate-y-0.5 hover:border-accent/50 hover:shadow-sm',
        active && 'border-accent/70 bg-blue-50'
      )}
      onClick={onSelect}
      data-topic-id={topic.id}
    >
      <h3 className="text-lg font-semibold">{topic.title}</h3>
      <p className="text-sm text-muted">{topic.category}</p>
    </article>
  );
}
