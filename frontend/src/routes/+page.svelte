<script>
  import { onMount } from 'svelte';

  let schemaFields = [];
  let formData = {};
  let prediction = null;
  let isLoading = true;
  let error = null;

  onMount(async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/model-schema');
      if (!res.ok) throw new Error('Failed to load model schema');
      const data = await res.json();
      schemaFields = data.features;
      schemaFields.forEach(f => (formData[f] = ''));
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  });

  async function handleSubmit() {
    prediction = null;
    error = null;
    isLoading = true;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!res.ok) {
        const e = await res.json();
        throw new Error(e.detail || 'Prediction error');
      }
      const { prediction: p } = await res.json();
      prediction = p;
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  }

  function handleReset() {
    schemaFields.forEach(f => (formData[f] = ''));
    prediction = null;
    error = null;
  }

  function prettify(field) {
    return field
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, s => s.toUpperCase())
      .trim();
  }
</script>

<main class="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
  <div class="w-full max-w-3xl space-y-8">
    <header class="text-center space-y-2">
      <h1 class="text-5xl font-extrabold text-cyan-400">Developer Salary Predictor</h1>
      <p class="text-gray-400">Fill out the form below to get an instant estimate.</p>
    </header>

    {#if isLoading && !schemaFields.length}
      <p class="text-center text-lg">Loading schema…</p>
    {:else if error && !schemaFields.length}
      <div class="bg-red-800 text-red-200 p-4 rounded-lg">
        <strong>Error:</strong> {error}
      </div>
    {:else}
      <form on:submit|preventDefault={handleSubmit} class="bg-gray-800 p-8 rounded-2xl shadow-xl space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {#each schemaFields as field}
            <div class="flex flex-col">
              <label for={field} class="mb-1 text-gray-300 font-medium">
                {prettify(field)}
              </label>
              <input
                id={field}
                bind:value={formData[field]}
                type="text"
                placeholder={`Enter ${prettify(field)}`}
                class="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                required
              />
            </div>
          {/each}
        </div>

        <div class="flex flex-col sm:flex-row gap-4">
          <button
            type="submit"
            class="flex-1 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold transition disabled:opacity-50"
            disabled={isLoading}
          >
            {isLoading ? 'Predicting…' : 'Predict Salary'}
          </button>
          <button
            type="button"
            class="flex-1 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg font-semibold transition"
            on:click={handleReset}
            disabled={isLoading}
          >
            Reset
          </button>
        </div>
      </form>
    {/if}

    {#if prediction !== null}
      <div class="bg-gray-800 p-8 rounded-2xl shadow-xl text-center">
        <h2 class="text-2xl font-semibold text-gray-300">Estimated Salary</h2>
        <p class="mt-4 text-6xl font-extrabold text-cyan-400">
          ${prediction.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
      </div>
    {/if}

    {#if error && schemaFields.length}
      <div class="bg-red-800 text-red-200 p-4 rounded-lg">
        <strong>Error:</strong> {error}
      </div>
    {/if}
  </div>
</main>
