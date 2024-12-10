# Ask the Document UI

This is the UI for our Document Q&A solution, powered by [`Svelte`](https://github.com/sveltejs/cli).

## Developing

Install dependencies with `yarn`, setup .env, and start a development server:

```
DOCUMENT_NAME=YOUR DOC NAME
BACKEND=http://localhost:8000
```

```bash
yarn dev

# or start the server and open the app in a new browser tab
yarn dev --open
```

## Building

To create a production version of your app:

```bash
yarn build
```

* You can preview the production build with `yarn preview`.
* There is metadata injected in the build/index.html file that may not be visible in dev or preview mode, but you can visually inspect it
* Build will actually create a copy of the static files in the ./service/static folder where you can serve them with the python backend
* Remember to update your .env BACKEND variable to point to where you are hosting the backend

### Todo

* Code cleanup...