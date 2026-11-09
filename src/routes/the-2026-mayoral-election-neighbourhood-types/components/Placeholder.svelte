<script>
	// Stand-in box for a graphic that has not been built yet. Delete once every graphic exists.
	let { note = '', height = 360 } = $props();
</script>

<div class="placeholder" style:height="{height}px">
	<p>Graphic placeholder</p>
	{#if note}<p class="note">{note}</p>{/if}
</div>

<style>
	.placeholder {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		border: 2px dashed var(--brandGray60, #aaa);
		border-radius: 4px;
		background: #f6f6f4;
		text-align: center;
		padding: 0 24px;
		box-sizing: border-box;
	}
	p {
		margin: 0;
		font-family: OpenSans, sans-serif;
		font-size: 14px;
		font-weight: bold;
		color: var(--brandGray90, #555);
	}
	.note {
		margin-top: 8px;
		font-weight: normal;
		max-width: 520px;
		line-height: 1.4;
	}
</style>
