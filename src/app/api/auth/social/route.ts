import { NextResponse } from 'next/server';

const supportedProviders = ['instagram', 'x'];

export async function POST(request: Request) {
  const { provider } = await request.json();

  if (!supportedProviders.includes(provider)) {
    return NextResponse.json({ message: 'Unsupported provider.' }, { status: 400 });
  }

  return NextResponse.json({
    message: `Redirecting to ${provider} authentication...`,
    provider,
  });
}
