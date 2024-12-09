import { writable, get, type Writable } from 'svelte/store';
import { v4 as uuidv4 } from 'uuid';
import { queryService } from './api';

// Define types
// Define types
export interface Message {
	id: string;
	role: 'user' | 'assistant';
	text: string;
	questionId?: string;
}

export interface Question {
	id: string;
	question: string;
}

export const docName: string = __DOCUMENT_NAME__;

// Define writable stores
export const userMessage: Writable<string> = writable('');
export const chatMessages: Writable<Message[]> = writable([
	{
		id: uuidv4(),
		role: 'assistant',
		text: `Hello! I am an AI language model that has been given information about ${docName}. If you ask me a question, I will do my best to answer based on only the information in the document, while citing the pages I am referencing for my answer. Please remember that I am not perfect and I might make mistakes. Use me as a reference but check my sources in the document by downloading it yourself using the top menu link. What's on your mind?`,
	},
]);

export const askedQuestions: Writable<Question[]> = writable([]);
export const selectedQuestion: Writable<Question | null> = writable(null);
export const isModalOpen: Writable<boolean> = writable(false);
export const isLoading: Writable<boolean> = writable(false); // NEW store for loading state
// Define functions
// Function to add a message to the chat
export const addMessage = (role: 'user' | 'assistant', text: string) => {
	chatMessages.update((messages) => [
		...messages,
		{ id: uuidv4(), role, text },
	]);
};

// Function to add a question to the list of asked questions
export const addQuestion = (question: string) => {
	askedQuestions.update((questions) => [
		...questions,
		{ id: uuidv4(), question },
	]);
};

export const sendMessage = async (): Promise<void> => {
	const currentMessage = get(userMessage).trim();
	if (!currentMessage) return;

	// Generate a unique ID for this question
	const questionId = uuidv4();

	// Add the user's message to the chat
	addMessage('user', currentMessage);

	// Add the question to the asked questions list
	askedQuestions.update((questions) => [
		...questions,
		{ id: questionId, question: currentMessage },
	]);

	// Clear the user's input
	userMessage.set('');
	// Start loading
	isLoading.set(true);

	try {
		// Fetch the response from the backend using queryService
		const systemResponse = await queryService(currentMessage);

		// Add the assistant's response to the chat, tied to the question ID
		chatMessages.update((messages) => [
			...messages,
			{ id: uuidv4(), role: 'assistant', text: systemResponse, questionId },
		]);
	} catch (error) {
		chatMessages.update((messages) => [
			...messages,
			{
				id: uuidv4(),
				role: 'assistant',
				text: 'An error occurred while processing your query. Please try again later.',
				questionId,
			},
		]);
		console.error('Error during sendMessage:', error);
	} finally {
		// Stop loader
		isLoading.set(false);
	}
};

// Open Modal
export const openModal = (questionId: string): void => {
	const questions = get(askedQuestions);
	const question = questions.find((q) => q.id === questionId);
	if (question) {
		selectedQuestion.set(question);
		isModalOpen.set(true);
	}
};

// Close Modal
export const closeModal = (): void => {
	selectedQuestion.set(null);
	isModalOpen.set(false);
};

// Get response for a specific question
export const getResponseForQuestion = (questionId: string): string => {
	const messages = get(chatMessages);
	const response = messages.find(
		(message) => message.role === 'assistant' && message.questionId === questionId
	);
	return response ? response.text : 'No response available.';
};