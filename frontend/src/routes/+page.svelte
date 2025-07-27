<script>
    import { onMount } from 'svelte';
    import Chart from 'chart.js/auto';

    // --- State Management ---
    let profile = {
        Country: "United States of America",
        EdLevel: "Bachelor’s degree (B.A., B.S., B.Eng., etc.)",
        YearsCodePro: 10,
        MainBranch: "I am a developer by profession",
        RemoteWork: "Remote",
        Age: "25-34 years old",
        LanguageHaveWorkedWith: "Python;JavaScript;HTML/CSS;SQL",
        DatabaseHaveWorkedWith: "PostgreSQL;SQLite",
        WebframeHaveWorkedWith: "FastAPI;Svelte",
        OpSysPersonalUse: "Linux-based"
    };

    let prediction = null;
    let isLoading = false;
    let error = null;

    // In a real app, this would come from an environment variable
    // Vercel automatically proxies /api requests to the backend.
    const API_URL = 'http://127.0.0.1:8000/predict'; 

    // --- Form Options ---
    // Data for dropdowns to improve user experience
    const formOptions = {
        Country: ["United States of America", "Germany", "India", "United Kingdom of Great Britain and Northern Ireland", "Canada", "France", "Poland", "Netherlands", "Australia", "Brazil", "Spain", "Italy", "Sweden", "Switzerland", "Other"],
        EdLevel: ["Bachelor’s degree (B.A., B.S., B.Eng., etc.)", "Master’s degree (M.A., M.S., M.Eng., MBA, etc.)", "Some college/university study without earning a degree", "Secondary school (e.g. American high school, German Realschule or Gymnasium, etc.)", "Professional degree (JD, MD, etc.)", "Other doctoral degree (Ph.D., Ed.D., etc.)", "Associate degree (A.A., A.S., etc.)", "Something else"],
        MainBranch: ["I am a developer by profession", "I am not primarily a developer, but I write code sometimes as part of my work", "I am a student who is learning to code", "I code primarily as a hobby", "I used to be a developer by profession, but no longer am"],
        RemoteWork: ["Remote", "Hybrid (some remote, some in-person)", "In-person"],
        Age: ["18-24 years old", "25-34 years old", "35-44 years old", "45-54 years old", "55-64 years old", "65 years or older", "Under 18 years old"],
        OpSysPersonalUse: ["Windows", "macOS", "Linux-based", "Windows Subsystem for Linux (WSL)", "Other"]
    };

    // --- API Call Logic ---
    async function getPrediction() {
        isLoading = true;
        error = null;
        prediction = null;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profile)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'An error occurred while fetching the prediction.');
            }

            const data = await response.json();
            prediction = data.predicted_salary_usd;

        } catch (e) {
            error = e.message;
        } finally {
            isLoading = false;
        }
    }

    // --- Charting Logic ---
    onMount(() => {
        const chartFontColor = '#4B5563';
        const chartGridColor = '#E5E7EB';
        const primaryColor = '#14B8A6'; // Teal
        const secondaryColor = '#F97316'; // Orange

        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: chartFontColor }, grid: { display: false } },
                y: { ticks: { color: chartFontColor }, grid: { color: chartGridColor } }
            }
        };

        const horizontalBarOptions = {
            ...commonOptions,
            indexAxis: 'y',
            scales: {
                x: { ticks: { color: chartFontColor }, grid: { color: chartGridColor } },
                y: { ticks: { color: chartFontColor }, grid: { display: false } }
            }
        };

        // EDA Chart 1: Top Countries
        new Chart(document.getElementById('countryChart'), {
            type: 'bar',
            data: {
                labels: ['USA', 'Germany', 'India', 'UK', 'Canada', 'France'],
                datasets: [{
                    label: 'Respondents',
                    data: [18.9, 8.4, 7.2, 5.5, 3.6, 3.6],
                    backgroundColor: primaryColor,
                    borderRadius: 4
                }]
            },
            options: horizontalBarOptions
        });

        // EDA Chart 2: Top Paying Technologies
        new Chart(document.getElementById('techSalaryChart'), {
            type: 'bar',
            data: {
                labels: ['Erlang', 'Clojure', 'F#', 'Go', 'Ruby', 'Rust'],
                datasets: [{
                    label: 'Median Salary (USD)',
                    data: [100636, 95541, 95000, 92000, 91000, 90000],
                    backgroundColor: secondaryColor,
                    borderRadius: 4
                }]
            },
            options: {
                ...horizontalBarOptions,
                plugins: {
                    ...horizontalBarOptions.plugins,
                    tooltip: {
                        callbacks: {
                            label: (context) => `$${context.parsed.x.toLocaleString()}`
                        }
                    }
                }
            }
        });
    });
</script>

<svelte:head>
    <title>Stack Overflow 2024 Salary Predictor</title>
</svelte:head>

<div class="min-h-screen bg-gray-50 text-gray-800 font-sans">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
        <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-bold text-gray-900">
                SO<span class="text-teal-500">24</span> Salary Insights
            </h1>
            <a href="#predictor" class="bg-teal-500 text-white px-5 py-2 rounded-full font-semibold hover:bg-teal-600 transition-colors">
                Go to Predictor
            </a>
        </nav>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-6 py-12">
        <!-- Introduction Section -->
        <section class="text-center mb-20">
            <h2 class="text-4xl md:text-5xl font-extrabold mb-4">Explore the 2024 Developer Landscape</h2>
            <p class="text-lg text-gray-600 max-w-3xl mx-auto">
                Discover key insights from the Stack Overflow 2024 survey and use our machine learning model to predict your salary based on your unique profile.
            </p>
        </section>

        <!-- EDA Dashboard Section -->
        <section id="eda" class="mb-20">
            <h3 class="text-3xl font-bold text-center mb-10">Key Insights from the Survey</h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div class="bg-white p-6 rounded-xl shadow-md">
                    <h4 class="text-xl font-semibold text-center mb-4">Top Responding Countries</h4>
                    <div class="relative h-96">
                        <canvas id="countryChart"></canvas>
                    </div>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-md">
                    <h4 class="text-xl font-semibold text-center mb-4">Highest Paying Technologies</h4>
                    <div class="relative h-96">
                        <canvas id="techSalaryChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- Predictor Section -->
        <section id="predictor">
            <div class="max-w-4xl mx-auto">
                <div class="text-center mb-10">
                    <h3 class="text-3xl font-bold">Salary Predictor</h3>
                    <p class="text-md text-gray-600 mt-2">Fill in your details below to get a salary estimate.</p>
                </div>

                <form on:submit|preventDefault={getPrediction} class="bg-white p-8 rounded-xl shadow-lg space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <!-- Form Fields -->
                        <div>
                            <label for="Country" class="block text-sm font-medium text-gray-700 mb-1">Country</label>
                            <select id="Country" bind:value={profile.Country} class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition">
                                {#each formOptions.Country as option}
                                    <option value={option}>{option}</option>
                                {/each}
                            </select>
                        </div>
                        <div>
                            <label for="EdLevel" class="block text-sm font-medium text-gray-700 mb-1">Education Level</label>
                            <select id="EdLevel" bind:value={profile.EdLevel} class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition">
                                {#each formOptions.EdLevel as option}
                                    <option value={option}>{option}</option>
                                {/each}
                            </select>
                        </div>
                        <div>
                            <label for="YearsCodePro" class="block text-sm font-medium text-gray-700 mb-1">Years of Pro Experience</label>
                            <input type="number" id="YearsCodePro" bind:value={profile.YearsCodePro} min="0" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition">
                        </div>
                        <div>
                            <label for="RemoteWork" class="block text-sm font-medium text-gray-700 mb-1">Work Style</label>
                            <select id="RemoteWork" bind:value={profile.RemoteWork} class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition">
                                {#each formOptions.RemoteWork as option}
                                    <option value={option}>{option}</option>
                                {/each}
                            </select>
                        </div>
                        <div class="md:col-span-2">
                            <label for="LanguageHaveWorkedWith" class="block text-sm font-medium text-gray-700 mb-1">Languages (semicolon-separated)</label>
                            <input type="text" id="LanguageHaveWorkedWith" bind:value={profile.LanguageHaveWorkedWith} class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 transition">
                        </div>
                        <!-- Add other fields from your schema here if needed -->
                    </div>
                    <div class="pt-4 text-center">
                        <button type="submit" disabled={isLoading} class="bg-teal-500 text-white font-bold py-3 px-10 rounded-lg text-lg w-full md:w-auto hover:bg-teal-600 disabled:bg-gray-400 transition-all transform hover:scale-105">
                            {#if isLoading}
                                <span>Calculating...</span>
                            {:else}
                                <span>Predict My Salary</span>
                            {/if}
                        </button>
                    </div>
                </form>

                <!-- Result/Error Display -->
                {#if prediction !== null}
                    <div class="mt-8 p-6 rounded-lg bg-teal-50 border-l-4 border-teal-500 text-center">
                        <p class="text-lg text-gray-700 mb-1">Predicted Annual Salary (USD):</p>
                        <p class="text-5xl font-bold text-teal-900">
                            {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(prediction)}
                        </p>
                        <p class="text-xs text-gray-500 mt-3">Disclaimer: This is an estimate based on a machine learning model and survey data. Actual salaries can vary.</p>
                    </div>
                {/if}

                {#if error}
                    <div class="mt-8 p-6 rounded-lg bg-red-50 border-l-4 border-red-500">
                        <p class="font-bold text-red-800">An Error Occurred</p>
                        <p class="text-red-700">{error}</p>
                    </div>
                {/if}
            </div>
        </section>
    </main>
</div>
