<script>
	// Simple password gate for pages still in development — drop <PasswordGate /> at the top
	// of a page's markup to lock it, and remove/comment out that one line once it's ready to
	// go public. Not real security (the password ships in the client bundle); it's just a
	// speed bump to keep a work-in-progress page from being casually seen before launch.

	export let password = "catcatmeow";

	let entered = "";
	let unlocked = false;

	function checkPassword() {
		if (entered === password) {
			unlocked = true;
		} else {
			alert("Incorrect password");
		}
	}
</script>

{#if !unlocked}
	<div class="overlay">
		<div class="password-box">
			<h3>This page is under development :)</h3>
			<input
				type="password"
				bind:value={entered}
				placeholder="Enter password"
				on:keydown={(e) => e.key === "Enter" && checkPassword()}
			/>
			<button on:click={checkPassword}>Unlock</button>
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(255, 255, 255, 0.9);
		backdrop-filter: blur(4px);
		z-index: 9999;
		display: flex;
		justify-content: center;
		align-items: center;
	}

	.password-box {
		background: white;
		padding: 2rem;
		border-radius: 8px;
		box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
		text-align: center;
	}

	h3 {
		font-family: "Source Serif Pro", serif;
		font-weight: normal;
		font-size: 20px;
		color: black;
		margin-top: 0;
	}

	input {
		padding: 0.5rem;
		margin-right: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	button {
		padding: 0.5rem 1rem;
		background-color: black;
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
	}
	button:hover {
		opacity: 0.7;
	}
</style>
