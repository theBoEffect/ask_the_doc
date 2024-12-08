<script>
    import { writable } from 'svelte/store';

    // State for light/dark mode toggle
    const darkMode = writable(false);
    const docName = __DOCUMENT_NAME__;

    const toggleDarkMode = () => {
        darkMode.update((mode) => !mode);

        // Apply the correct class to the body
        if ($darkMode) {
            document.body.classList.add('dark');
            document.body.classList.remove('light');
        } else {
            document.body.classList.add('light');
            document.body.classList.remove('dark');
        }
    };

    let userMessage = '';
    let chatMessages = [
        { role: 'assistant', text: `Hello! I am an AI language model that has been given information about ${docName}. If you ask me a question, I will do my best to answer based on only the information in the document, while citing the pages I am referencing for my answer. Please remember that I am not perfect and I might make mistakes. Use me as a reference but check my sources in the document by downloading it yourself using the top menu link. What\'s on your mind?` }
    ];
    let askedQuestions = [];
    let selectedQuestion = null;
    let isModalOpen = false;
    async function sendMessage() {
        if (userMessage.trim()) {
            // Add user's message
            chatMessages = [...chatMessages, { role: 'user', text: userMessage }];
            askedQuestions = [...askedQuestions, userMessage];

            const currentMessage = userMessage; // Store the message
            userMessage = ''; // Clear input field

            // Simulate a delayed assistant response
            setTimeout(() => {
                chatMessages = [
                    ...chatMessages,
                    { role: 'assistant', text: "This is a simulated response for: " + currentMessage }
                ];
            }, 1000);
        }
    }

    function openModal(question) {
        selectedQuestion = question;
        isModalOpen = true;
    }

    function closeModal() {
        isModalOpen = false;
        selectedQuestion = null;
    }

    function getResponseForQuestion(question) {
        const response = chatMessages.find(
          (message) => message.role === 'assistant' && message.text.includes(question)
        );
        return response ? response.text : 'No response available.';
    }

</script>

<style>
    /* Style for the dark and light modes */
    :global(html, body) {
        margin: 0;
        padding: 0;
        font-family: 'Arial', sans-serif;
    }
    :global(body.light) {
        background-color: #f9f9f9;
        color: #3c3c3c;
    }
    :global(body.dark) {
        background-color: #3c3c3c;
        color: #ffffff;
    }

    :global(.border-gray-300) {
        border-color: #3c3c3c !important;
    }
    :global(.dark .border-gray-300) {
        border-color: #ffffff !important;
    }

    .text-gray-800 {
        color: #3c3c3c;
    }
    .dark .text-gray-800 {
        color: #ffffff;
    }

    .toggle-btn {
        background-color: inherit;
        color: inherit;
    }
    .dark .toggle-btn {
        border: 1px solid #ffffff;
    }
    .menu-link {
        margin-right: 1rem;
        color: inherit;
        text-decoration: none;
    }
    .menu-link:hover {
        text-decoration: underline;
    }

    .chat-message {
        display: flex;
        margin-bottom: 0.5rem;
    }

    .chat-message.user {
        justify-content: flex-end;
        margin-left: auto; /* Push the message to the right */
    }

    .chat-message.assistant {
        justify-content: flex-start;
        margin-right: auto; /* Push the message to the left */
    }

    .chat-bubble {
        padding: 0.5rem 1rem;
        border-radius: 1rem;
        background-color: var(--chat-bubble-bg, #f0f0f0);
        color: var(--chat-bubble-color, #000);
        max-width: 75%; /* Ensure bubbles are not overly wide */
        word-wrap: break-word; /* Handle long text */
    }

    .chat-message.user .chat-bubble {
        --chat-bubble-bg: #007bff;
        --chat-bubble-color: #fff;
    }

    .chat-message.assistant .chat-bubble {
        --chat-bubble-bg: #e5e5e5;
        --chat-bubble-color: #000;
    }

    body.dark .chat-message.assistant .chat-bubble {
        --chat-bubble-bg: #555;
        --chat-bubble-color: #fff;
    }

    body.dark .chat-message.user .chat-bubble {
        --chat-bubble-bg: #1e90ff;
        --chat-bubble-color: #fff;
    }
    .modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
    }

    .modal-content {
        background: #fff;
        color: #000;
        padding: 2rem;
        border-radius: 8px;
        width: 80%;
        max-width: 600px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    body.dark .modal-content {
        background: #333;
        color: #fff;
    }

    .modal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .modal-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
    }
</style>

<div class="flex flex-col h-screen">
    <!-- Top Menu Bar -->
    <div class="flex justify-between items-center px-4 py-2 border-b border-gray-300 dark:border-gray-300" style="background-color: inherit;">
        <h1 class="text-lg font-semibold">Ask {docName}</h1>
        <div class="flex items-center">
            <a href="#" class="menu-link">Document</a>
            <a href="#" class="menu-link">Source Code</a>
            <button
              class="p-2 rounded toggle-btn"
              on:click={toggleDarkMode}
            >
                {#if $darkMode} 🌙 {:else} ☀️ {/if}
            </button>
        </div>
    </div>

    <div class="flex flex-grow">
        <!-- Left Sidebar -->
        <div class="w-1/4 border-r border-gray-300 dark:border-gray-300 p-4" style="background-color: inherit;">
            <h2 class="text-lg font-bold mb-4">Questions so far...</h2>
            <ul class="space-y-2">
                {#each askedQuestions as question}
                    <li class="text-sm truncate cursor-pointer" on:click={() => openModal(question)}>{question}</li>
                {/each}
            </ul>
        </div>

        <!-- Main Content -->
        <div class="flex flex-col w-3/4">
            <!-- Chat Section -->
            <div class="flex-grow p-4 overflow-y-auto space-y-4" style="background-color: inherit;">
                {#each chatMessages as message (message.text)}
                    <div class="chat-message {message.role}">
                        <div class="chat-bubble">{message.text}</div>
                    </div>
                {/each}
            </div>

            <!-- Input Section -->
            <div class="flex items-center p-4 border-t border-gray-300 dark:border-gray-300" style="background-color: inherit;">
                <input
                  type="text"
                  bind:value={userMessage}
                  placeholder="Type your question..."
                  class="flex-grow px-4 py-2 border rounded bg-gray-300 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-200 focus:outline-none focus:ring focus:ring-blue-300"
                />
                <button
                  on:click={sendMessage}
                  class="ml-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 focus:ring focus:ring-blue-300"
                >
                    Send
                </button>
            </div>
        </div>
    </div>
    {#if isModalOpen}
        <div class="modal" on:click={closeModal}>
            <div class="modal-content" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>Response</h2>
                    <button class="modal-close" on:click={closeModal}>&times;</button>
                </div>
                <p>{getResponseForQuestion(selectedQuestion)}</p>
            </div>
        </div>
    {/if}
</div>