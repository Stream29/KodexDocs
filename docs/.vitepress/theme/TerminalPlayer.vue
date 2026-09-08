<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { withBase } from 'vitepress';

const props = defineProps({
  recording: { type: Object, required: true },
});

const container = ref();
let player;
let disposed = false;

onMounted(async () => {
  const { create } = await import('asciinema-player');
  if (disposed || !container.value) return;
  player = create(withBase(props.recording.src), container.value, {
    preload: true,
    autoPlay: true,
    loop: true,
    controls: false,
    fit: 'width',
    idleTimeLimit: props.recording.idleTimeLimit ?? 1000,
    speed: props.recording.speed ?? 1,
    terminalFontFamily: '"JetBrains Mono", "Noto Sans Mono CJK SC", monospace',
    markers: props.recording.markers,
  });
});

onBeforeUnmount(() => {
  disposed = true;
  player?.dispose();
});
</script>

<template>
  <aside class="terminal-player" :data-recording="withBase(recording.src)"
         :data-marker="recording.marker" :aria-label="recording.marker">
    <div ref="container" class="terminal-player__mount" inert></div>
  </aside>
</template>
