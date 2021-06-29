# Modifications to Mono for FontVal on recent Mac OS X

Recent Mac OS X have tighter security. Specifically, The material in this repository is to address the two code-signing related issues with using
mono's mkbundle:

- https://github.com/mono/mono/issues/18826 . There is a pull request to merge https://github.com/HinTak/mono/tree/issue18826-fix .

- https://github.com/mono/mono/issues/17881