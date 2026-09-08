<script setup>
import { computed, ref, watch, watchPostEffect } from 'vue';
import { useEventListener, useMounted } from '@vueuse/core';
import { useData, useRoute, withBase } from 'vitepress';
import { locales, repository } from '../locales.mjs';
import { pages } from '../pages.mjs';
import TerminalPlayer from './TerminalPlayer.vue';
import { recordingForText } from './terminal-recordings.mjs';

const rawFiles = import.meta.glob('../../**/*.md', {
  eager: true, query: '?url&no-inline', import: 'default',
});
const { page, lang } = useData();
const route = useRoute();
const locale = computed(() => locales[lang.value] ?? locales['en-US']);
const chunks = computed(() => page.value.rawDocument
  ? JSON.parse(decodeURIComponent(page.value.rawDocument)).chunks : []);
const chapters = computed(() => chunks.value.filter(chunk => chunk.title));
const languagePages = computed(() => pages.filter(item => item.lang === lang.value));
const ready = useMounted();
const pinned = ref(false);
const hovered = ref(false);
const keyboardFocus = ref(false);
const expanded = computed(() => !ready.value || pinned.value || hovered.value || keyboardFocus.value);
const toggle = ref();
const main = ref();
const active = ref('');
const hash = ref('');
const rawLink = computed(() => rawFiles[`../../${page.value.relativePath}`]);

function languageLink(target) {
  const relative = page.value.relativePath.replace(/^zh-(?:CN|TW)\//, '').replace(/index\.md$/, '').replace(/\.md$/, '.html');
  const candidate = `/${target.path}${relative}`;
  return withBase(pages.some(item => item.url === candidate) ? candidate : `/${target.path}`) + hash.value;
}
function focusIn(event) {
  keyboardFocus.value = event.target.matches(':focus-visible');
}
function focusOut(event) {
  if (!event.currentTarget.contains(event.relatedTarget)) keyboardFocus.value = false;
}
function dismiss() {
  toggle.value?.focus();
  pinned.value = hovered.value = keyboardFocus.value = false;
}
function chapterClick() {
  if (matchMedia('(hover: none)').matches) {
    main.value?.focus({ preventScroll: true });
    pinned.value = hovered.value = keyboardFocus.value = false;
  }
}
function updateActive() {
  active.value = chapters.value.findLast(chapter =>
    document.getElementById(chapter.id)?.getBoundingClientRect().top <= 80)?.id ?? '';
}
function updateHash() { hash.value = location.hash; }
watch(() => route.path, () => {
  hovered.value = keyboardFocus.value = false;
});
watchPostEffect(() => {
  if (ready.value) {
    updateHash();
    updateActive();
  }
});
useEventListener('hashchange', updateHash);
useEventListener('scroll', updateActive, { passive: true });
</script>

<template>
  <div :class="{ 'sidebar-enhanced': ready, 'sidebar-open': expanded }">
    <a class="skip-link" href="#main" @click="main?.focus()">{{ locale.skip }}</a>
    <header class="topbar">
      <a class="brand" :href="withBase(`/${locale.path}`)"><span>&gt;</span>Kodex / docs</a>
      <nav class="languages" :aria-label="locale.language">
        <a v-for="code in ['zh-CN', 'zh-TW', 'en-US']" :key="code"
           :href="languageLink(locales[code])" :lang="code" :hreflang="code"
           :aria-current="code === lang ? 'page' : undefined">{{ code }}</a>
      </nav>
    </header>
    <div v-if="page.isNotFound" class="not-found">
      <h1>404</h1>
      <a :href="withBase('/')">[←] Kodex / docs</a>
    </div>
    <div v-else class="workspace">
      <aside class="sidebar" @pointerenter="event => { if (event.pointerType !== 'touch') hovered = true }"
             @pointerleave="hovered = false" @focusin="focusIn" @focusout="focusOut" @keydown.esc.prevent="dismiss">
        <button ref="toggle" class="sidebar-toggle" type="button" :hidden="!ready"
                aria-controls="sidebar-panel" :aria-expanded="expanded" :aria-pressed="pinned"
                :aria-label="pinned ? locale.unpin : locale.pin" :title="pinned ? locale.unpin : locale.pin"
                @click="pinned = !pinned">{{ expanded ? '[←]' : '[→]' }}</button>
        <Transition name="sidebar-panel">
        <div v-show="expanded" id="sidebar-panel" :inert="!expanded" :aria-hidden="!expanded || undefined">
          <nav class="contents" :aria-label="locale.navigation">
            <template v-for="item in languagePages" :key="item.url">
              <a v-if="languagePages.length > 1" :href="withBase(item.url)"
                 :aria-current="route.path === withBase(item.url) ? 'page' : undefined">{{ item.title }}</a>
            </template>
            <a v-for="chapter in chapters" :key="chapter.id" :href="`#${chapter.id}`"
               :aria-current="active === chapter.id ? 'location' : undefined"
               @click="chapterClick">{{ chapter.title }}</a>
          </nav>
          <nav class="resources" :aria-label="locale.source">
            <a :href="`${repository}/releases`">{{ locale.release }}</a>
            <a :href="repository">GitHub</a>
            <a :href="rawLink" target="_blank" rel="noopener">{{ locale.raw }}</a>
          </nav>
        </div>
        </Transition>
      </aside>
      <main id="main" ref="main" tabindex="-1">
        <h1 class="sr-only">{{ page.title }}</h1>
        <section v-for="chunk in chunks" :id="chunk.id" :key="chunk.id">
          <pre class="markdown" v-text="chunk.text"></pre>
          <TerminalPlayer v-if="recordingForText(chunk.text)"
                          :key="`${page.relativePath}:${recordingForText(chunk.text).marker}`"
                          :recording="recordingForText(chunk.text)" />
        </section>
      </main>
    </div>
  </div>
</template>
