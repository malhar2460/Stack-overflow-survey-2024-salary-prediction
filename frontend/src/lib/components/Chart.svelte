<script>
  import { onMount } from 'svelte';
  import Chart from 'chart.js/auto';

  export let type;
  export let data;
  export let options;

  let canvas;

  onMount(() => {
    const chart = new Chart(canvas, {
      type,
      data,
      options,
    });

    return () => {
      chart.destroy();
    };
  });
</script>

<div class="chart-container relative w-full max-w-4xl mx-auto h-80 md:h-96">
  <canvas bind:this={canvas}></canvas>
</div>
