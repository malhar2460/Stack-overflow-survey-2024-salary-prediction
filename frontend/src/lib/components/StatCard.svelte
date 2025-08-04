<script>
  export let value;
  export let description;
  export let colorClass = 'text-primary';
</script>

<div class="bg-white border border-gray-200 rounded-xl p-6 text-center transition-transform transform hover:-translate-y-1 hover:shadow-lg">
    <div class="text-5xl font-bold {colorClass} mb-2">{value}</div>
    <p class="text-gray-600">{description}</p>
</div>
