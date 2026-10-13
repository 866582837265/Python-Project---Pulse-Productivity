import { useEffect } from 'react';

export const useTheme = () => {
  useEffect(() => {
    // Force dark theme on app load
    document.documentElement.setAttribute('data-theme', 'dark');
    document.body.classList.add('theme-loaded');
    document.body.classList.remove('theme-loading');
    
    // Store theme preference
    localStorage.setItem('theme', 'dark');
  }, []);

  return 'dark';
};

export default useTheme;