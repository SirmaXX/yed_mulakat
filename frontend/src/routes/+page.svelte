<script>
    import Navbar from "../components/Navbar.svelte";
    import SocTestPredict from "../components/SocTestPredict.svelte";
    import SohTestPredict from "../components/SohTestPredict.svelte";
    import HealthCard from "../components/HealthCard.svelte";
</script>

<div class="container-fluid px-4">
    <h1 class="mt-4">Ana Ekran</h1>
    <ol class="breadcrumb mb-4">
        <li class="breadcrumb-item"><a href="index.html">Dashboard</a></li>
        <li class="breadcrumb-item active">Ana Ekran</li>
    </ol>
    <div class="card mb-4">
        <div class="card-body">
            <div class="container-fluid">
                <h1 class="text-center">Servis & Model Kontrol Paneli</h1>
                <div class="row">
                    <div class="col-md-4"><HealthCard /></div>
                    <div class="col-md-4"><SohTestPredict /></div>
                    <div class="col-md-4"><SocTestPredict /></div>
                </div>
            </div>
        </div>
    </div>
    <div style="height: 100vh"></div>
</div>
