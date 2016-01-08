import pypandoc

desc = pypandoc.convert('CHANGELOG.md', 'rst', format='markdown')

with open("CHANGELOG.rst", "w") as f:
    f.write(desc)

