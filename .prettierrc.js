module.exports = {
  // Use single quotes in JSX and JS
  singleQuote: true,

  // Use trailing commas in objects, arrays, etc.
  trailingComma: 'es5',

  // Use 2 spaces for indentation
  tabWidth: 2,

  // Use spaces instead of tabs
  useTabs: false,

  // Add semicolons at the end of statements
  semi: true,

  // Line length before Prettier tries to wrap
  printWidth: 100,

  // JSX: Use single quotes in JSX
  jsxSingleQuote: true,

  // JSX: Put the > of a multi-line JSX element at the end of the last line
  // instead of being alone on the next line
  bracketSameLine: false,

  // Include parentheses around a sole arrow function parameter
  arrowParens: 'always',

  // Control how attributes are formatted in HTML, JSX, and Vue
  bracketSpacing: true,

  // Format only the content of the top-level file (e.g., for Markdown)
  embeddedLanguageFormatting: 'auto',

  // End of line character
  endOfLine: 'lf',

  // Specify the HTML whitespace sensitivity
  htmlWhitespaceSensitivity: 'css',

  // Put properties of objects in the same line if they fit
  singleAttributePerLine: false,

  // Overrides for specific file patterns
  overrides: [
    {
      files: '*.json',
      options: {
        // Use 2 spaces for JSON files
        tabWidth: 2,
      },
    },
    {
      files: '*.{css,scss,less,styl}',
      options: {
        singleQuote: false,
      },
    },
  ],
};

// This configuration ensures consistent code formatting across the project.
// It's recommended to integrate this with your editor and set up format-on-save.
// For VS Code, add this to your settings.json:
// "editor.defaultFormatter": "esbenp.prettier-vscode",
// "editor.formatOnSave": true,
// "editor.codeActionsOnSave": {
//   "source.fixAll.eslint": true
// }
