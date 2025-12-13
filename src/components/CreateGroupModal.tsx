'use client';

import { useEffect, useState } from 'react';

const personas = [
  'Friendly guide',
  'Direct coach',
  'Curious researcher',
  'Concise note-taker',
];

type GroupPayload = {
  name: string;
  persona: string;
  members: string[];
};

export function CreateGroupModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [form, setForm] = useState<GroupPayload>({
    name: '',
    persona: personas[0],
    members: [''],
  });
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open) return;
    setForm({ name: '', persona: personas[0], members: [''] });
    setMessage(null);
  }, [open]);

  const updateMember = (index: number, value: string) => {
    setForm((current) => {
      const nextMembers = [...current.members];
      nextMembers[index] = value;
      return { ...current, members: nextMembers };
    });
  };

  const addMember = () => setForm((current) => ({ ...current, members: [...current.members, ''] }));

  const removeMember = (index: number) => {
    setForm((current) => ({
      ...current,
      members: current.members.filter((_, memberIndex) => memberIndex !== index),
    }));
  };

  const handleSubmit = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const response = await fetch('/api/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const result = await response.json();
      setMessage(result.message ?? 'Group created!');
    } catch (error) {
      setMessage((error as Error).message);
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="modal-backdrop fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="card-shadow w-full max-w-2xl rounded-2xl border border-border bg-white p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-muted">Groups</p>
            <h3 className="text-2xl font-semibold">Create a group</h3>
            <p className="text-muted">Pick a bot persona and invite members to collaborate.</p>
          </div>
          <button
            type="button"
            className="rounded-full bg-surface px-3 py-1 text-sm font-semibold text-muted hover:text-primary"
            onClick={onClose}
          >
            Close
          </button>
        </div>

        <div className="mt-6 space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-semibold" htmlFor="group-name">
              Group name
            </label>
            <input
              id="group-name"
              value={form.name}
              onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
              placeholder="My research panel"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-semibold" htmlFor="persona">
              Bot persona
            </label>
            <select
              id="persona"
              value={form.persona}
              onChange={(event) => setForm((current) => ({ ...current, persona: event.target.value }))}
              className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
            >
              {personas.map((persona) => (
                <option key={persona}>{persona}</option>
              ))}
            </select>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold">Members</label>
              <button
                type="button"
                onClick={addMember}
                className="text-sm font-semibold text-accent hover:underline"
              >
                Add member
              </button>
            </div>
            <div className="space-y-2">
              {form.members.map((member, index) => (
                <div key={`member-${index}`} className="flex items-center gap-3">
                  <input
                    type="email"
                    value={member}
                    onChange={(event) => updateMember(index, event.target.value)}
                    className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-sm outline-none focus:border-accent focus:ring-2 focus:ring-accent/20"
                    placeholder="person@example.com"
                  />
                  {form.members.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMember(index)}
                      className="rounded-lg border border-border px-3 py-2 text-sm text-muted hover:text-primary"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-2 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-border px-4 py-3 text-sm font-semibold text-primary hover:border-primary/40"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading}
              className="rounded-xl bg-accent px-4 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create group'}
            </button>
          </div>

          {message && <p className="text-sm text-accent">{message}</p>}
        </div>
      </div>
    </div>
  );
}
