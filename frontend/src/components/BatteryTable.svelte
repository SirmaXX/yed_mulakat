<script>
  import { onMount } from 'svelte';
  import DataTable from 'datatables.net';
  import 'datatables.net-dt/css/dataTables.dataTables.css';  

  let selectedBattery = "05";
  let batteryData = [];
  let error = null;
  let tableElement;
  let table;

  async function fetchData() {
    error = null;
    try {
      const res = await fetch(`http://localhost:8000/api/data/${selectedBattery}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      batteryData = await res.json();

      // Destroy existing table if exists
      if (table) {
        table.destroy();
        table = null;
      }

      // Wait DOM to update
      await tick();

      // Re-init DataTable
      if (tableElement) {
        table = new DataTable(tableElement, {
          paging: true,
          responsive: true,
          searching: true
        });
      }
    } catch (err) {
      error = err.message;
      console.error("Veri çekme hatası:", err);
    }
  }

  import { tick } from 'svelte';
</script>

<div class="container">
  <h2>Batarya Verisi</h2>

  <div class="form-group">
    <label for="batterySelect">Batarya Seçin:</label>
    <select id="batterySelect" bind:value={selectedBattery} class="form-select">
      <option value="05">Batarya 5</option>
      <option value="06">Batarya 6</option>
      <option value="18">Batarya 18</option>
    </select>
  </div>

  <button class="btn btn-primary mt-2" on:click={fetchData}>
    Veriyi Getir
  </button>

  {#if error}
    <div class="alert alert-danger mt-3">Hata: {error}</div>
  {/if}

  {#if batteryData.length > 0}
    <table bind:this={tableElement} id="battery_table" class="display mt-4">
      <thead>
        <tr>
          {#each Object.keys(batteryData[0]) as col}
            <th>{col}</th>
          {/each}
        </tr>
      </thead>
      <tbody>
        {#each batteryData as row}
          <tr>
            {#each Object.values(row) as value}
              <td>{value}</td>
            {/each}
          </tr>
        {/each}
      </tbody>
    </table>
  {/if}
</div>
