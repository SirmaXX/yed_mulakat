<script>
    import Navbar from "../components/Navbar.svelte";
    import SocTestPredict from "../components/SocTestPredict.svelte";
    import SohTestPredict from "../components/SohTestPredict.svelte";
    import BatteryTable from "../components/BatteryTable.svelte";
    let { children } = $props();
</script>

<Navbar />

<div id="layoutSidenav">
    <div id="layoutSidenav_nav">
        <nav class="sb-sidenav accordion sb-sidenav-dark" id="sidenavAccordion">
            <div class="sb-sidenav-menu">
                <div class="nav">
                    <a class="nav-link" aria-label="anasayfa" href="/">
                        <div class="sb-nav-link-icon">
                            <i class="fas fa-tachometer-alt"></i>
                        </div>
                        Anasayfa
                    </a>

                    <div class="sb-sidenav-menu-heading">Bataryalar</div>
                    <a
                        class="nav-link"
                        aria-label="bataryaların listesi"
                        href="/battery"
                    >
                        <div class="sb-nav-link-icon">
                            <i class="fas fa-table"></i>
                        </div>
                        Bataryalar
                    </a>
                    <a
                        class="nav-link"
                        aria-label="bataryaların zaman serisi"
                        href="/batterytime"
                    >
                        <div class="sb-nav-link-icon">
                            <i class="fas fa-chart-area"></i>
                        </div>
                        Batarya-zaman grafiği
                    </a>
                </div>
            </div>
        </nav>
    </div>
    <div id="layoutSidenav_content">
        <main>
            {@render children()}
        </main>
        <footer class="py-4 bg-light mt-auto">
            <div class="container-fluid px-4">
                <div
                    class="d-flex align-items-center justify-content-between small"
                >
                    <div class="text-muted">Copyright &copy; Deniz Balcı</div>
                    <div>
                        <a href="#">Privacy Policy</a>
                        &middot;
                        <a href="#">Terms &amp; Conditions</a>
                    </div>
                </div>
            </div>
        </footer>
    </div>
</div>
