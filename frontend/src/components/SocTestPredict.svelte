<script>
  let predictedSoc = null;
  let isLoading = false;
  let error = null;

  async function fetchSocPrediction() {
    isLoading = true;
    error = null;

    try {
      const response = await fetch("http://localhost:8000/soc-test-predict/");

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      predictedSoc = data.predicted_soc;
    } catch (err) {
      error = err.message;
      console.error("Error fetching SOC prediction:", err);
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="container mt-4">
  <h2>SOC Test Prediction</h2>

  <button
    on:click={fetchSocPrediction}
    disabled={isLoading}
    class="btn btn-primary mb-3"
  >
    {isLoading ? "Loading..." : "Get SOC Prediction"}
  </button>

  {#if error}
    <div class="alert alert-danger">
      Error: {error}
    </div>
  {/if}

  {#if predictedSoc !== null}
    <div class="card border-success mb-3">
      <div class="card-header bg-success text-white">Prediction Result</div>
      <div class="card-body">
        <h5 class="card-title">
          Predicted SOC: <strong>{predictedSoc.toFixed(2)}%</strong>
        </h5>
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
