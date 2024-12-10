<script lang="ts">
	import '../app.css';
	let { children } = $props();
	const metaTitle = `Ask ${__DOCUMENT_NAME__}`;
	const metaUrl = __BACKEND__;
	const metaDescription = __META_DESCRIPTION__;
	const metaImg = __META_IMG_URL__;

</script>
<svelte:head>
	<title>{metaTitle}</title>
	<meta name="title" content="{metaTitle}">
	<meta name="description" content="{metaDescription}">
	<meta property="og:type" content="website">
	<meta property="og:url" content="{metaUrl}">
	<meta property="og:title" content="{metaTitle}">
	<meta property="og:description" content="{metaDescription}">
	<meta property="og:image" content="{metaImg}">
	<meta property="twitter:card" content="summary_large_image">
	<meta property="twitter:url" content="{metaUrl}">
	<meta property="twitter:title" content="{metaTitle}">
	<meta property="twitter:description" content="{metaDescription}">
	<meta property="twitter:image" content="{metaImg}">
</svelte:head>
{@render children()}
