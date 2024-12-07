<script>
    import { writable } from 'svelte/store';
    import {
        docName,
        userMessage,
        chatMessages,
        askedQuestions,
        selectedQuestion,
        isModalOpen,
        sendMessage,
        openModal,
        closeModal,
        getResponseForQuestion,
    } from '$lib/utils/chat';

    // State for light/dark mode toggle
    const darkMode = writable(false);
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

</script>

<style>
    @import '$lib/styles/chat.css';
</style>

<div class="flex flex-col h-screen">
    <!-- Top Menu Bar -->
    <div class="flex justify-between items-center px-4 py-2 border-b border-gray-300 dark:border-gray-300" style="background-color: inherit;">
        <h1 class="text-lg font-semibold">Ask {docName}</h1>
        <div class="flex items-center">
            <a href="#" class="menu-link">Document</a>
            <a href="https://github.com/theBoEffect/ask_the_doc" class="menu-link">Source Code</a>
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
                {#each $askedQuestions as question}
                    <li class="text-sm truncate cursor-pointer" on:click={() => openModal(question)}>{question}</li>
                {/each}
            </ul>
        </div>

        <!-- Main Content -->
        <div class="flex flex-col w-3/4">
            <!-- Chat Section -->
            <div class="flex-grow p-4 overflow-y-auto space-y-4" style="background-color: inherit;">
                {#each $chatMessages as message (message.text)}
                    <div class="chat-message {message.role}">
                        <div class="chat-bubble">{message.text}</div>
                    </div>
                {/each}
            </div>

            <!-- Input Section -->
            <div class="flex items-center p-4 border-t border-gray-300 dark:border-gray-300" style="background-color: inherit;">
                <input
                  type="text"
                  bind:value={$userMessage}
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
    {#if $isModalOpen}
        <div class="modal" on:click={closeModal}>
            <div class="modal-content" on:click|stopPropagation>
                <div class="modal-header">
                    <h2>Response</h2>
                    <button class="modal-close" on:click={closeModal}>&times;</button>
                </div>
                <p>{getResponseForQuestion($selectedQuestion)}</p>
            </div>
        </div>
    {/if}
</div>