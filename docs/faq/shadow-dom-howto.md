# How to work with Shadow DOM in Selene?

{% include-markdown 'warn-from-next-release.md' %}

## Via built-in WebDriver-based properties

– As simply as:

```python
from selene import browser, have

# GIVEN
paragraphs = browser.all('my-paragraph')

# WHEN it's enough to access specific elements
paragraph_2_shadow = paragraphs.second.shadow_root  # 💡
my_shadowed_text_2 = paragraph_2_shadow.element('[name=my-text]')
# OR when you need all shadow roots
my_shadowed_texts = paragraphs.shadow_roots.all('[name=my-text]')  # 💡

# As you can see these queries are lazy,
# so you were able to store them in vars ↖️
# even before open ↙️
browser.open('https://the-internet.herokuapp.com/shadowdom')

# THEN
my_shadowed_text_2.should(have.exact_text("My default text"))  # ⬅️
my_shadowed_texts.should(have.exact_texts("My default text", "My default text"))  # ⬅️
```

## Via JavaScript queries at query.js.*

– By using advanced [query.js.shadow_root][selene.core.query.js.shadow_root] and [query.js.shadow_roots][selene.core.query.js.shadow_roots] queries, as simply as:

```python
from selene import browser, have, query

# GIVEN
paragraphs = browser.all('my-paragraph')

# WHEN it's enough to access specific elements
paragraph_2_shadow = paragraphs.second.get(query.js.shadow_root)  # 💡
my_shadowed_text_2 = paragraph_2_shadow.element('[name=my-text]')
# OR when you need all shadow roots
my_shadowed_texts = paragraphs.get(query.js.shadow_roots).all('[name=my-text]')  # 💡

# As you can see these queries are lazy,
# so you were able to store them in vars ↖️
# even before open ↙️
browser.open('https://the-internet.herokuapp.com/shadowdom')

# THEN
my_shadowed_text_2.should(have.exact_text("My default text"))  # ⬅️
my_shadowed_texts.should(have.exact_texts("My default text", "My default text"))  # ⬅️
```
