<script>
  import { onMount } from 'svelte';

  let schemaFields = [];
  let fieldMeta = {};
  let formData = {};
  let prediction = null;
  let isLoading = true;
  let isPredicting = false;
  let error = null;
  let openDropdown = null;

  function prettify(field) {
    return field
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, s => s.toUpperCase())
      .trim();
  }

  onMount(async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/model-schema');
      if (!res.ok) throw new Error('Failed to load model schema');
      const { features } = await res.json();

      schemaFields = Object.keys(features);
      schemaFields.forEach(f => {
        const { type, selection, values } = features[f];
        fieldMeta[f] = {
          type,
          selection,
          values: Array.isArray(values) ? values : []
        };
        formData[f] = selection === 'multi' ? [] : '';
      });
    } catch (err) {
      error = err.message;
    } finally {
      isLoading = false;
    }
  });

  function toggleDropdown(field) {
    openDropdown = openDropdown === field ? null : field;
  }

  function addTag(field, option) {
    if (!formData[field].includes(option)) {
      formData[field] = [...formData[field], option];
    }
  }

  function removeTag(field, option) {
    formData[field] = formData[field].filter(x => x !== option);
  }

  async function handleSubmit() {
    prediction = null;
    error = null;
    isPredicting = true;
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Prediction failed');
      }
      const { prediction: result } = await res.json();
      prediction = result;
    } catch (err) {
      error = err.message;
    } finally {
      isPredicting = false;
    }
  }

  function handleReset() {
    prediction = null;
    error = null;
    schemaFields.forEach(f => {
      formData[f] = fieldMeta[f].selection === 'multi' ? [] : '';
    });
  }
</script>

<main class="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
  <div class="w-full max-w-3xl space-y-8">
    <header class="text-center space-y-2">
      <h1 class="text-5xl font-extrabold text-cyan-400">Developer Salary Predictor</h1>
      <p class="text-gray-400">Fill out the form below to get an instant estimate.</p>
    </header>

    {#if isLoading}
      <p class="text-center text-lg flex justify-center items-center gap-2">
        <span>Loading schema…</span>
        <span class="loader"></span>
      </p>
    {:else if error}
      <div class="bg-red-800 text-red-200 p-4 rounded-lg">
        <strong>Error:</strong> {error}
      </div>
    {:else}
      <form on:submit|preventDefault={handleSubmit} class="bg-gray-800 p-8 rounded-2xl shadow-xl space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          {#each schemaFields as field}
            <div class="flex flex-col">
              <label for={field} class="mb-1 text-gray-300 font-medium">{prettify(field)}</label>

              {#if fieldMeta[field].type === 'numeric'}
                <input
                  id={field}
                  type="number"
                  bind:value={formData[field]}
                  placeholder={`Enter ${prettify(field)}`}
                  class="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  required
                />

              {:else if fieldMeta[field].selection === 'single'}
                <select
                  id={field}
                  bind:value={formData[field]}
                  class="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                  required
                >
                  <option value="" disabled>Select {prettify(field)}</option>
                  {#each fieldMeta[field].values as option}
                    <option value={option}>{option}</option>
                  {/each}
                </select>

              {:else}
                <div class="relative">
                  <div
                    class="flex flex-wrap gap-2 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg cursor-pointer"
                    on:click={() => toggleDropdown(field)}
                  >
                    {#each formData[field] as tag}
                      <span class="flex items-center bg-cyan-600 text-white px-2 py-1 rounded-full text-sm">
                        {tag}
                        <button type="button" class="ml-1" on:click|stopPropagation={() => removeTag(field, tag)}>&times;</button>
                      </span>
                    {/each}
                    <span class="text-gray-400">
                      {formData[field].length ? 'Add more…' : `Select ${prettify(field)}`}
                    </span>
                    <svg class="h-4 w-4 ml-auto transform {openDropdown===field?'rotate-180':''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                  {#if openDropdown === field}
                    <ul class="absolute left-0 right-0 mt-0.5 max-h-40 overflow-auto bg-gray-700 border-t-0 border border-gray-600 rounded-b-lg z-20" style="top:100%;">
                      {#each fieldMeta[field].values as option}
                        <li>
                          <button type="button" class="w-full text-left px-3 py-2 hover:bg-gray-600" on:click={() => addTag(field, option)}>
                            {option}
                          </button>
                        </li>
                      {/each}
                    </ul>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>

        <div class="flex flex-col sm:flex-row gap-4">
          <button
            type="submit"
            class="flex-1 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg font-semibold transition flex items-center justify-center gap-2"
            disabled={isPredicting}
          >
            {#if isPredicting}
              <span class="loader border-white"></span>
              Predicting your salary…
            {:else}
              Predict Salary
            {/if}
          </button>

          <button
            type="button"
            on:click={handleReset}
            class="flex-1 py-3 bg-gray-600 hover:bg-gray-500 rounded-lg font-semibold transition"
            disabled={isPredicting}
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
  </div>
</main>

<style>
  .loader {
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-top-color: white;
    border-radius: 50%;
    width: 1rem;
    height: 1rem;
    animation: spin 1s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
