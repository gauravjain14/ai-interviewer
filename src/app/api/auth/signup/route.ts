import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const { email, password } = await request.json();

  if (!email || !password) {
    return NextResponse.json({ message: 'Email and password are required.' }, { status: 400 });
  }

  return NextResponse.json({
    message: 'Signup successful. A confirmation link has been sent to your email.',
    email,
  });
}
