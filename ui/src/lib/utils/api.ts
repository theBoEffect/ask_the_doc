export const queryService = async (query: string): Promise<string> => {
	const backendUrl: string = __BACKEND__;

	if (!backendUrl) {
		throw new Error('Backend URL is not defined in the environment variables.');
	}

	try {
		const response = await fetch(`${backendUrl}/api/query`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ query }),
		});

		if (!response.ok) {
			throw new Error(`Error: ${response.status} ${response.statusText}`);
		}

		const data = await response.json();
		return data.response.replace(/\n/g, '<br>'); // Expected to be { "response": "SYSTEM RESPONSE HERE" }
	} catch (error) {
		console.error('Failed to fetch data from the backend:', error);
		throw error;
	}
};
