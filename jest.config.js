module.exports = {
  preset: 'ts-jest',
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: 'tests/tsconfig.json',
      },
    ],
  },
  testEnvironment: 'node',
  testRegex: 'tests/.*\\.test\\.ts$',
  coveragePathIgnorePatterns: ['/node_modules/', '/tests/'],
  automock: true,
  moduleFileExtensions: ['ts', 'js', 'json'],
  unmockedModulePathPatterns: [
    'jest-editor-support/node_modules',
    'color-convert',
    'chalk',
    'snapdragon',
    'ansi-styles',
    'core-js',
    'debug',
    '@babel/template',
    'graceful-fs',
    '@babel/types',
  ],
  moduleNameMapper: {
    '\\.(svg)$': '<rootDir>/tests/fileMock.ts',
  },
};
