'use client';

import { useState } from 'react';

import { ConversationPanel } from '@/components/ConversationPanel';
import { CreateGroupModal } from '@/components/CreateGroupModal';
import { Hero } from '@/components/Hero';
import { TopicGrid } from '@/components/TopicGrid';
import { AuthPanel } from '@/components/AuthPanel';
import { topics as defaultTopics, type Topic } from '@/data/topics';

export default function HomePage() {
  const [selectedTopic, setSelectedTopic] = useState<Topic>(defaultTopics[0]);
  const [showGroupModal, setShowGroupModal] = useState(false);

  return (
    <div className="min-h-screen bg-surface">
      <Hero onCreateGroup={() => setShowGroupModal(true)} />

      <main className="mx-auto flex max-w-6xl flex-col gap-6 px-6 py-10 lg:flex-row">
        <section className="w-full max-w-md space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold">Topics</h2>
            <span className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-accent">{defaultTopics.length} options</span>
          </div>
          <TopicGrid topics={defaultTopics} activeId={selectedTopic.id} onSelect={(id) => setSelectedTopic(defaultTopics.find((topic) => topic.id === id) ?? defaultTopics[0])} />
          <AuthPanel />
        </section>

        <ConversationPanel topic={selectedTopic} />
      </main>

      <CreateGroupModal open={showGroupModal} onClose={() => setShowGroupModal(false)} />
    </div>
  );
}
