import type { Topic } from '@/data/topics';

export function ConversationPanel({ topic }: { topic: Topic }) {
  return (
    <section className="flex-1 space-y-4">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-muted">{topic.category}</p>
        <h3 className="text-2xl font-semibold">{topic.title}</h3>
        <p className="text-muted">{topic.description}</p>
      </div>

      <div className="card-shadow rounded-2xl border border-border bg-white p-5 space-y-4">
        <div className="space-y-3 rounded-xl bg-blue-50 p-4">
          <span className="inline-flex w-fit rounded-full bg-white px-3 py-1 text-xs font-semibold text-accent">Hey there!</span>
          <p className="text-sm text-primary">{topic.intro}</p>
          <p className="text-muted">Does that sound good?</p>
        </div>

        <div className="inline-flex rounded-full bg-primary px-4 py-2 text-white">Hello</div>

        <p className="text-primary">{topic.question}</p>

        <div className="flex flex-col gap-3 sm:flex-row">
          <label className="sr-only" htmlFor="response">
            Your response
          </label>
          <textarea
            id="response"
            className="w-full flex-1 rounded-xl border border-border bg-surface px-4 py-3 text-sm text-primary outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            rows={3}
            placeholder="Share your thoughts..."
          />
          <button
            type="button"
            className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent text-white transition hover:-translate-y-0.5 input-shadow"
            aria-label="Send response"
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" aria-hidden>
              <path d="M3 11.5 21 3l-8.5 18-2.5-7-7-2.5Z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
            </svg>
          </button>
        </div>

        <p className="text-xs text-muted">
          Share as much or as little as you like—your perspective helps us learn.
        </p>
      </div>
    </section>
  );
}
