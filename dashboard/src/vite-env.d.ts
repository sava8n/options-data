/// <reference types="vite/client" />

// echarts-gl ships no TypeScript types
// it registers the 3D chart types onto echarts as an import side-effect.
declare module 'echarts-gl';
