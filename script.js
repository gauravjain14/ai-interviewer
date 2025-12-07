const topics = [
  {
    id: 'sports',
    title: 'Sports',
    description: 'Your relationship with competition, teams, and the sports you follow.',
    category: 'Lifestyle',
    question:
      "When did you last feel inspired by a game or athlete? What stood out to you?",
    intro:
      'Thanks for joining! We will chat about the games, teams, and memorable moments that shape how you experience sports. I am here to listen and learn—there are no right or wrong answers.',
  },
  {
    id: 'tv',
    title: 'TV & Film',
    description: 'Viewing habits, favorite genres, and how screen stories shape your world.',
    category: 'Entertainment',
    question:
      'What was the last show or film that made you think differently about something, and why?',
    intro:
      'I would love to hear about the stories you enjoy on screen. We will explore the characters, genres, and viewing rituals that matter to you.',
  },
  {
    id: 'science',
    title: 'Science & Tech',
    description: 'Curiosity about breakthroughs, gadgets, and how innovation affects you.',
    category: 'Curiosity',
    question:
      'Which emerging technology are you most curious about right now? What excites or worries you about it?',
    intro:
      'Let us talk about how science and technology show up in your life. Your perspective helps us understand what feels promising and what feels uncertain.',
  },
  {
    id: 'travel',
    title: 'Travel',
    description: 'Places you dream about, trips you cherish, and how you like to explore.',
    category: 'Lifestyle',
    question:
      'Tell me about a place that left a strong impression on you. What made it memorable?',
    intro:
      'We will chat about the destinations and travel styles that resonate with you, from quick getaways to bucket-list adventures.',
  },
  {
    id: 'food',
    title: 'Food',
    description: 'Flavors, cooking habits, and the meals that connect you with others.',
    category: 'Everyday moments',
    question:
      'What is a dish that feels like home to you? What makes it special?',
    intro:
      'Share the tastes and traditions that matter to you. I am excited to learn how food fits into your routine and memories.',
  },
  {
    id: 'careers',
    title: 'Career growth',
    description: 'Work goals, learning paths, and the environments where you thrive.',
    category: 'Work & learning',
    question:
      'What skill are you trying to grow this year, and what is motivating you?',
    intro:
      'Let us explore how you navigate work and learning. Your insights help us understand what support is most helpful.',
  },
];

const topicsGrid = document.getElementById('topicsGrid');
const topicTitle = document.getElementById('topicTitle');
const topicCategory = document.getElementById('topicCategory');
const topicDescription = document.getElementById('topicDescription');
const conversationCard = document.getElementById('conversationCard');
const conversationIntro = document.getElementById('conversationIntro');

let activeTopicId = null;

const createTopicCard = (topic) => {
  const card = document.createElement('article');
  card.className = 'topic-card';
  card.dataset.topicId = topic.id;

  card.innerHTML = `
    <h3 class="topic-card__title">${topic.title}</h3>
    <p class="topic-card__meta">${topic.category}</p>
  `;

  card.addEventListener('click', () => {
    setActiveTopic(topic.id);
  });

  return card;
};

const renderTopics = () => {
  topicsGrid.innerHTML = '';
  topics.forEach((topic) => topicsGrid.appendChild(createTopicCard(topic)));
};

const clearActiveCard = () => {
  const previous = document.querySelector('.topic-card.active');
  if (previous) previous.classList.remove('active');
};

const renderConversation = (topic) => {
  conversationCard.innerHTML = '';

  const introBlock = document.createElement('div');
  introBlock.className = 'conversation__intro';
  introBlock.innerHTML = `
    <span class="prompt-chip">Hey there!</span>
    <p class="prompt-body">${topic.intro}</p>
    <p class="conversation__message">Does that sound good?</p>
  `;

  const reply = document.createElement('div');
  reply.className = 'reply-bubble';
  reply.textContent = 'Hello';

  const firstQuestion = document.createElement('p');
  firstQuestion.className = 'prompt-body';
  firstQuestion.textContent = topic.question;

  const inputRow = document.createElement('div');
  inputRow.className = 'input-row';
  inputRow.innerHTML = `
    <textarea rows="2" placeholder="Share your thoughts..."></textarea>
    <button aria-label="Send">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M3 11.5 21 3l-8.5 18-2.5-7-7-2.5Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>
      </svg>
    </button>
  `;

  const footer = document.createElement('p');
  footer.className = 'footer-note';
  footer.textContent = 'Share as much or as little as you like—your perspective helps us learn.';

  conversationCard.append(introBlock, reply, firstQuestion, inputRow, footer);
};

const setActiveTopic = (topicId) => {
  if (activeTopicId === topicId) return;
  activeTopicId = topicId;
  clearActiveCard();

  const topic = topics.find((item) => item.id === topicId);
  const card = document.querySelector(`[data-topic-id="${topicId}"]`);
  if (card) card.classList.add('active');

  topicTitle.textContent = topic.title;
  topicCategory.textContent = topic.category;
  topicDescription.textContent = topic.description;

  renderConversation(topic);
};

renderTopics();

if (topics.length) {
  setActiveTopic(topics[0].id);
}
