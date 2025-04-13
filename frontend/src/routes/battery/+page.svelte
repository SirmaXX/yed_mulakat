<script>
  import BatteryTable from "../../components/BatteryTable.svelte";
</script>

<div class="container-fluid px-4">
  <h1 class="mt-4">Batarya Verileri</h1>
  <ol class="breadcrumb mb-4">
    <li class="breadcrumb-item"><a href="index.html">Dashboard</a></li>
    <li class="breadcrumb-item active">Batarya Verileri</li>
  </ol>
  <div class="card mb-4">
    <div class="card-body">
      <div class="container-fluid">
        <h1 class="text-center">Batarya Verileri</h1>
        <div class="row">
          <div class="col-md-12"><BatteryTable /></div>
        </div>
      </div>
    </div>
  </div>
  <div style="height: 100vh"></div>
</div>
