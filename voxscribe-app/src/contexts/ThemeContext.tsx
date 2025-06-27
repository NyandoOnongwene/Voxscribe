import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: React.ReactNode;
}

// Function to apply theme to DOM
const applyThemeToDOM = (theme: Theme) => {
  console.log(`Applying theme to DOM: ${theme}`);
  
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
    document.body.classList.add('dark');
    console.log('Added dark classes to documentElement and body');
  } else {
    document.documentElement.classList.remove('dark');
    document.body.classList.remove('dark');
    console.log('Removed dark classes from documentElement and body');
  }
  
  console.log('Final documentElement classes:', document.documentElement.classList.toString());
  console.log('Final body classes:', document.body.classList.toString());
};

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Check if theme is stored in localStorage
    const savedTheme = localStorage.getItem('voxscribe-theme') as Theme;
    console.log('Initial theme from localStorage:', savedTheme);
    
    if (savedTheme && (savedTheme === 'light' || savedTheme === 'dark')) {
      console.log('Using saved theme:', savedTheme);
      return savedTheme;
    }
    
    // Check system preference
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      console.log('Using system dark theme preference');
      return 'dark';
    }
    
    console.log('Defaulting to light theme');
    return 'light';
  });

  const toggleTheme = () => {
    console.log('toggleTheme called, current theme:', theme);
    const newTheme = theme === 'light' ? 'dark' : 'light';
    console.log('Setting new theme to:', newTheme);
    
    // Update state
    setTheme(newTheme);
    
    // Save to localStorage
    localStorage.setItem('voxscribe-theme', newTheme);
    console.log('Theme stored in localStorage:', newTheme);
    
    // Immediately apply to DOM
    applyThemeToDOM(newTheme);
  };

  // Apply theme changes to DOM whenever theme state changes
  useEffect(() => {
    console.log('ThemeContext useEffect triggered, theme:', theme);
    applyThemeToDOM(theme);
  }, [theme]);

  // Initial theme application on mount
  useEffect(() => {
    console.log('Initial theme setup on mount, theme:', theme);
    applyThemeToDOM(theme);
  }, []);

  const value = {
    theme,
    toggleTheme,
  };

  console.log('ThemeProvider rendering with theme:', theme);

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
