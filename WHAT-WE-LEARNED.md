# What we learned

Even if it seems obvious in retrospect, what have we learned about Python Shiny in this project?

## Some basic html attributes are not supported

I can mark a button as disabled, but it doesn't seem that a `ui.input_select` can be disabled.

## No warning if ID mismatch

Unless I'm missing something, there doesn't seem to be any warning when there isn't a matching function name in the server for an ID in the UI. Either from typos, or fumbling some more complicated display logic, there have been times where this could have been helpful.

For example, in one branch had renamed `input.upper()` to `input.upper_bound()`, but in another branch a new function had also introduced a reference to `input.upper()`. Differ parts of the code, so no merge conflict, but when it tries to get the old input value it fails silently: No error on screen, and nothing in the log.

## No warning if type mismatch

Related: I had
```
ui.output_text("epsilon")
```
but then changed `epsilon` from `render.text` to `reactive.value` and forgot to update the UI. No warning in the logs: Spinner in the browser window.

## UI and Server functions don't really separate concerns

My first impression was that the UI function would be something like a "view" and the server would be a "controller", but for any kind of conditional display I need a `render.ui`, so that distinction breaks down quickly. Just maintaining a naming convention for these little bits of UI in the server gets to be a chore. It would be kludgy, but what if we could suply lambdas instead of names?

## Values vs. reactive values

A couple times I've started with something as a plain value, and then realized I needed a reactive value. This gets confusing if there are merge conflicts, or if some variables are reactive, and some aren't.

Typing might help here. I've also wondered about naming conventions, but I haven't been sure whether the the reactive values or the plain values are the ones to flag.

## Reactive calcs feel redundant

It seems like the returned value would be the same, so I would like to compress something like this:
```python
@reactive.calc
def csv_labels_calc():
    return read_labels(req(csv_path()))

@render.text
def csv_labels():
    return csv_labels_calc()
```
into:
```python
@reactive.calc
@render.text
def csv_labels():
    return read_labels(req(csv_path()))
```
but that returns an error:
```
Renderer.__call__() missing 1 required positional argument: '_fn'
```

If I just refer to a reactive calc directly in the UI there is no error in the log, just a spinner in the UI.

## No component testing

It feels like a gap in the library that there is no component testing. The only advice is to pull out testable logic from the server functions, and for the rest, use end-to-end tests: There's not a recommended way to test the ui+server interaction for just one component.

Short of full component testing, being able to write unit tests around reactive values would be nice.

## Unstated requirements for module IDs

The [docs](https://shiny.posit.co/py/docs/modules.html#how-to-use-modules) only say:

> This id has two requirements. First, it must be unique in a single scope, and can’t be duplicated in a given application or module definition. ... Second, the UI and server ids must match.

But it's fussier than that:

```
ValueError: The string 'Will this work?' is not a valid id; only letters, numbers, and underscore are permitted
```

Was planning to just use the CSV column headers as IDs, but that's not going to work. Could Shiny just hash whatever we provide, so we wouldn't have to worry about this?

## Normal tooling doesn't work inside of app?

There are several bits of tooling that don't seem to work inside end-to-end app tests. My guess is that this isn't related to Shiny per se, but rather the ASGI framework: It's not running in the same process as pytest, so it's not surprising that the pytest process can't instrument this.
- [App code skipped by test coverage](https://github.com/opendp/dp-wizard/issues/18)
- [Mocks don't work inside app](https://github.com/opendp/dp-wizard/issues/119)
- `breakpoint()` doesn't work inside end-to-end tests. (A comparison might be made to debugging a React application: With React devtools in the browser, it's pretty easy!)

## You still need some webdev skills

I've had to tweak the CSS a few times:
- Adding margin to the page
- Overriding tricky bootstrap hover styling for tooltips
- Hiding elements of the slider that we didn't want (because we're using it for a logarithmic scale)

## R vs. Python / Express vs. Core

The different flavors of "Shiny" are a bit of nuissance when trying to find examples.
The maturity of Shiny for R means that the vast majority of the examples are for R, even with Python in the search. It would be nice if the docs site remembered that I only want to look at docs for Core.

## More validation / type casting on inputs

If we imagine we have a field that is a required positive integer, it would be nice to be able to specify that in the input itself, with a default error message handled by the UI, instead of needing to set up a calc on our side.

## It's easy to forget `return`

This is simple, but I was still scratching my head for a while. While there are some cases where returning `None` is intended, is it more more likely to be an error? What if it raised a warning, and an explicit empty string could be returned if that's really what you want?

## Shiny docs could have better formatting

- https://shiny.posit.co/py/api/core/ui.layout_columns.html: bullet list not rendered correctly.

## Silent errors if input type doesn't match update method

Multi selectize is almost a drop-in replacement for checkbox group, but they have different update methods, `update_selectize` vs `update_checkbox_group`, and if you use the wrong one it fails silently: The UI doesn't update, and there is no error.

## Add CSS for selectize in cards?

```
/*
Selectize menus should overflow the containing card.
*/
.card, .card-body { overflow: visible !important; }
```
