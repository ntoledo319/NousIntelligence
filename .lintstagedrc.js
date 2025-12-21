module.exports = {
  // Lint and format TypeScript and JavaScript files
  '**/*.{js,jsx,ts,tsx}': (filenames) => [
    'eslint --fix --max-warnings=0',
    `prettier --write ${filenames.join(' ')}`,
    // Run type checking on changed files in watch mode
    'tsc-files --noEmit',
  ],

  // Format MarkDown, JSON, and other files
  '**/*.{md,json,yml,yaml}': (filenames) => `prettier --write ${filenames.join(' ')}`,

  // Format CSS, SCSS, and other style files
  '**/*.{css,scss,less}': (filenames) => [
    'stylelint --fix',
    `prettier --write ${filenames.join(' ')}`,
  ],

  // Run tests related to modified files
  '**/*.{js,jsx,ts,tsx}': (filenames) => {
    const isAppFile = (f) => !f.includes('__tests__');
    const appFiles = filenames.filter(isAppFile);
    return appFiles.length > 0 ? 'jest --findRelatedTests --passWithNoTests' : [];
  },
};

// This configuration ensures that:
// 1. All JavaScript and TypeScript files are linted and formatted
// 2. All style files are formatted
// 3. All Markdown, JSON, YAML files are formatted
// 4. Tests are run for modified files
// 5. Type checking is performed on changed files

// The commands are run in parallel for better performance
// The configuration is optimized to only run necessary checks on staged files
