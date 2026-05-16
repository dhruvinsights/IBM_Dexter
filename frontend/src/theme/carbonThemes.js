import { CARBON_THEMES } from '../store/useThemeStore';

export const themeOptions = [
  {
    id: CARBON_THEMES.DARK,
    label: 'Dark',
    description: 'IBM Carbon g100 theme for enterprise dashboard usage',
  },
  {
    id: CARBON_THEMES.LIGHT,
    label: 'Light',
    description: 'IBM Carbon white theme for presentation and daylight usage',
  },
];

export const themeMetadata = {
  [CARBON_THEMES.DARK]: {
    layer: 'dark',
    page: 'g100',
    default: true,
  },
  [CARBON_THEMES.LIGHT]: {
    layer: 'light',
    page: 'white',
    default: false,
  },
};

export const getThemeLabel = (theme) =>
  themeOptions.find((option) => option.id === theme)?.label || 'Dark';

// Made with Bob
