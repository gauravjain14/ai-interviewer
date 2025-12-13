import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { name, persona, members } = await request.json();

  if (!name || !persona) {
    return NextResponse.json({ message: 'Group name and persona are required.' }, { status: 400 });
  }

  return NextResponse.json({
    message: 'Group created successfully.',
    group: {
      id: crypto.randomUUID(),
      name,
      persona,
      members: Array.isArray(members) ? members : [],
    },
  });
}
