export function Hero({ onCreateGroup }: { onCreateGroup: () => void }) {
  return (
    <header className="hero-gradient text-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-16 lg:flex-row lg:items-center lg:py-20">
        <div className="flex-1 space-y-4">
          <p className="text-sm uppercase tracking-[0.2em] text-sky-100">AI interviewer</p>
          <h1 className="text-4xl font-semibold leading-tight md:text-5xl">Choose a topic and share your thoughts</h1>
          <p className="max-w-2xl text-lg text-sky-100">
            Pick a conversation to explore. Each topic guides you through a short, friendly interview designed to capture your
            perspective.
          </p>
          <div className="flex flex-wrap gap-3">
            <button className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-primary shadow" type="button">
              Watch a demo
            </button>
            <button
              className="rounded-full border border-white/20 px-5 py-3 text-sm font-semibold text-white transition hover:border-white/40"
              type="button"
              onClick={onCreateGroup}
            >
              Create Group
            </button>
          </div>
        </div>
        <div className="w-full max-w-md rounded-2xl bg-white/5 p-6 shadow-xl ring-1 ring-white/10">
          <div className="space-y-3">
            <p className="text-sm text-sky-100">Featured question</p>
            <h2 className="text-xl font-semibold">When did you last feel inspired by a game or athlete?</h2>
            <p className="text-sky-100">
              Explore your connection to sports, competition, and memorable moments that shaped how you experience games.
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}
