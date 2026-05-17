import useThemeStore from '../store/useThemeStore';

/** Maps app shell theme to @carbon/charts `options.theme` (dark → g100, light → white). */
export function useCarbonChartTheme() {
  const theme = useThemeStore((s) => s.theme);
  return theme === 'g100' ? 'g100' : 'white';
}
