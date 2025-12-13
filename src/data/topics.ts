export type Topic = {
  id: string;
  title: string;
  description: string;
  category: string;
  question: string;
  intro: string;
};

export const topics: Topic[] = [
  {
    id: 'sports',
    title: 'Sports',
    description: 'Your relationship with competition, teams, and the sports you follow.',
    category: 'Lifestyle',
    question: 'When did you last feel inspired by a game or athlete? What stood out to you?',
    intro:
      'Thanks for joining! We will chat about the games, teams, and memorable moments that shape how you experience sports. I am here to listen and learn—there are no right or wrong answers.',
  },
  {
    id: 'tv',
    title: 'TV & Film',
    description: 'Viewing habits, favorite genres, and how screen stories shape your world.',
    category: 'Entertainment',
    question: 'What was the last show or film that made you think differently about something, and why?',
    intro:
      'I would love to hear about the stories you enjoy on screen. We will explore the characters, genres, and viewing rituals that matter to you.',
  },
  {
    id: 'science',
    title: 'Science & Tech',
    description: 'Curiosity about breakthroughs, gadgets, and how innovation affects you.',
    category: 'Curiosity',
    question: 'Which emerging technology are you most curious about right now? What excites or worries you about it?',
    intro:
      'Let us talk about how science and technology show up in your life. Your perspective helps us understand what feels promising and what feels uncertain.',
  },
  {
    id: 'travel',
    title: 'Travel',
    description: 'Places you dream about, trips you cherish, and how you like to explore.',
    category: 'Lifestyle',
    question: 'Tell me about a place that left a strong impression on you. What made it memorable?',
    intro:
      'We will chat about the destinations and travel styles that resonate with you, from quick getaways to bucket-list adventures.',
  },
  {
    id: 'food',
    title: 'Food',
    description: 'Flavors, cooking habits, and the meals that connect you with others.',
    category: 'Everyday moments',
    question: 'What is a dish that feels like home to you? What makes it special?',
    intro: 'Share the tastes and traditions that matter to you. I am excited to learn how food fits into your routine and memories.',
  },
  {
    id: 'careers',
    title: 'Career growth',
    description: 'Work goals, learning paths, and the environments where you thrive.',
    category: 'Work & learning',
    question: 'What skill are you trying to grow this year, and what is motivating you?',
    intro: 'Let us explore how you navigate work and learning. Your insights help us understand what support is most helpful.',
  },
];
