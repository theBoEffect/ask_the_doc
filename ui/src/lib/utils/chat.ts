import { writable, get, type Writable } from 'svelte/store';

// Define types
export interface Message {
	role: 'user' | 'assistant';
	text: string;
}

export const docName: string = __DOCUMENT_NAME__;

// Define writable stores
export const userMessage: Writable<string> = writable('');
export const chatMessages: Writable<Message[]> = writable([
	{
		role: 'assistant',
		text: `Hello! I am an AI language model that has been given information about ${docName}. If you ask me a question, I will do my best to answer based on only the information in the document, while citing the pages I am referencing for my answer. Please remember that I am not perfect and I might make mistakes. Use me as a reference but check my sources in the document by downloading it yourself using the top menu link. What's on your mind?`,
	},
]);
export const askedQuestions: Writable<string[]> = writable([]);
export const selectedQuestion: Writable<string | null> = writable(null);
export const isModalOpen: Writable<boolean> = writable(false);

// Define functions
export const sendMessage = async (): Promise<void> => {
	const currentMessage = get(userMessage).trim();

	if (currentMessage) {
		// Update chat messages
		chatMessages.update((messages) => [
			...messages,
			{ role: 'user', text: currentMessage },
		]);

		// Update asked questions
		askedQuestions.update((questions) => [...questions, currentMessage]);

		// Clear user message input
		userMessage.set('');

		// Simulate an assistant response
		setTimeout(() => {
			chatMessages.update((messages) => [
				...messages,
				{
					role: 'assistant',
					text: `This is a simulated response for: ${currentMessage}`,
				},
			]);
		}, 1000);
	}
};

export const openModal = (question: string): void => {
	selectedQuestion.set(question);
	isModalOpen.set(true);
};

export const closeModal = (): void => {
	isModalOpen.set(false);
	selectedQuestion.set(null);
};

export const getResponseForQuestion = (question: string): string => {
	const messages = get(chatMessages);
	const response = messages.find(
		(message) => message.role === 'assistant' && message.text.includes(question)
	);
	return response ? response.text : 'No response available.';
};
