<script>
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

    // API URL - this should come from environment variables in a real app
    const API_URL = 'http://127.0.0.1:8000/api/predict';

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
</script>

<form on:submit|preventDefault={getPrediction} class="bg-white p-8 rounded-xl shadow-lg">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 flex-row">
        <div>
            <label for="Country" class="block text-sm font-medium text-gray-700 mb-1">Country</label>
            <input type="text" id="Country" bind:value={profile.Country} class="w-full p-3 border border-gray-300 rounded-lg">
        </div>
        <div>
            <label for="EdLevel" class="block text-sm font-medium text-gray-700 mb-1">Education Level</label>
            <input type="text" id="EdLevel" bind:value={profile.EdLevel} class="w-full p-3 border border-gray-300 rounded-lg">
        </div>
        <div>
            <label for="YearsCodePro" class="block text-sm font-medium text-gray-700 mb-1">Years of Pro Experience</label>
            <input type="number" id="YearsCodePro" bind:value={profile.YearsCodePro} min="0" class="w-full p-3 border border-gray-300 rounded-lg">
        </div>
        <div>
            <label for="RemoteWork" class="block text-sm font-medium text-gray-700 mb-1">Work Style</label>
            <input type="text" id="RemoteWork" bind:value={profile.RemoteWork} class="w-full p-3 border border-gray-300 rounded-lg">
        </div>
        <div class="md:col-span-2">
            <label for="LanguageHaveWorkedWith" class="block text-sm font-medium text-gray-700 mb-1">Languages (semicolon-separated)</label>
            <input type="text" id="LanguageHaveWorkedWith" bind:value={profile.LanguageHaveWorkedWith} class="w-full p-3 border border-gray-300 rounded-lg">
        </div>
        </div>
    <div class="mt-8 text-center">
        <button type="submit" disabled={isLoading} class="bg-primary text-white font-bold py-3 px-8 rounded-lg text-lg w-full md:w-auto hover:bg-opacity-90 disabled:bg-gray-400 transition">
            {isLoading? 'Calculating...' : 'Predict My Salary'}
        </button>
    </div>
</form>

{#if prediction!== null}
    <div class="mt-8 p-6 rounded-lg bg-teal-50 border-l-4 border-primary">
        <p class="text-lg text-gray-700 mb-1">Predicted Annual Salary:</p>
        <p class="text-4xl font-bold text-teal-900">
            {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(prediction)}
        </p>
    </div>
{/if}

{#if error}
    <div class="mt-8 p-6 rounded-lg bg-red-50 border-l-4 border-red-500">
        <p class="font-bold text-red-800">An Error Occurred</p>
        <p class="text-red-700">{error}</p>
    </div>
{/if}
