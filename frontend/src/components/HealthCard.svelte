<script>
  import { onMount } from 'svelte';

  let isHealthy = null;
  let isLoading = false;
  let error = null;

  async function checkHealth() {
    isLoading = true;
    error = null;

    try {
      const res = await fetch('http://localhost:8000/health');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const result = await res.json();
      isHealthy = result.status === 'ok';
    } catch (err) {
      error = err.message;
      isHealthy = false;
    } finally {
      isLoading = false;
    }
  }

  onMount(() => {
    checkHealth();
  });
</script>

<div class="container mt-4">
  <h2>Service Health</h2>

  <button
    class="btn btn-outline-primary mb-3"
    on:click={checkHealth}
    disabled={isLoading}
  >
    {isLoading ? 'Checking...' : 'Check Health'}
  </button>

  {#if isHealthy === true}
    <div class="card border-success mb-3">
      <div class="card-header bg-success text-white">Status</div>
      <div class="card-body">
        <h5 class="card-title">Service is OK ✅</h5>
      </div>
    </div>
  {:else if isHealthy === false}
    <div class="card border-danger mb-3">
      <div class="card-header bg-danger text-white">Status</div>
      <div class="card-body">
        <h5 class="card-title">Service is Down ❌</h5>
        {#if error}
          <p class="text-muted"><small>Error: {error}</small></p>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .card {
    max-width: 400px;
    margin-top: 20px;
  }
</style>
