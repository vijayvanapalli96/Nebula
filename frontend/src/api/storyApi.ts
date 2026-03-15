export interface Question {
  id: string;
  question: string;
  options: string[];
}

export interface StoryQuestionsResponse {
  questions: Question[];
}

/** Simulates a network call — swap the body for a real fetch() later. */
export async function fetchStoryQuestions(): Promise<StoryQuestionsResponse> {
  await new Promise((resolve) => setTimeout(resolve, 3200));

  return {
    questions: [
      {
        id: 'tone',
        question: 'What kind of atmosphere should your story have?',
        options: [
          'Dark and mysterious',
          'Adventurous and exciting',
          'Thought-provoking',
          'Hopeful but tense',
        ],
      },
      {
        id: 'motivation',
        question: 'What drives your main character?',
        options: ['Curiosity', 'Revenge', 'Protecting someone', 'Survival'],
      },
      {
        id: 'world',
        question: 'What kind of world does this story take place in?',
        options: [
          'A futuristic civilization',
          'A mysterious modern city',
          'A distant alien planet',
          'A magical hidden world',
        ],
      },
    ],
  };
}
