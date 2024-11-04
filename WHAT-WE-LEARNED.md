# What we learned

Even if it seems obvious in retrospect, what have we learned about Python Shiny in this project?

## No warning if ID mismatch

Unless I'm missing something, there doesn't seem to be any warning when there isn't a matching function name in the server for an ID in the UI. Either from typos, or fumbling some more complicated display logic, there have been times where this could have been helpful.

## UI and Server functions don't really separate concerns

My first impression was that the UI function would be something like a "view" and the server would be a "controller", but for any kind of conditional display I need a `render.ui`, so that distinction breaks down quickly.

## Refactoring: values vs. reactive values

A couple times I've started with something as a plain value, and then realized I needed a reactive value. This gets confusing if there are merge conflicts, or if some variables are reactive, and some aren't.

Typing might help here. I've also wondered about naming conventions, but I haven't been sure whether the the reactive values or the plain values are the ones to flag.

## Reactive calcs feel redundant

It seems like the returned value would be the same, so I would like to compress something like this:
```python
@reactive.calc
def csv_fields_calc():
    return read_field_names(req(csv_path()))

@render.text
def csv_fields():
    return csv_fields_calc()
```
into:
```python
@reactive.calc
@render.text
def csv_fields():
    return read_field_names(req(csv_path()))
```
but that returns an error:
```
Renderer.__call__() missing 1 required positional argument: '_fn'
```

## No component testing

It feels like a gap in the library that there is no component testing. The only advice is to pull out testable logic from the server functions, and for the rest, use end-to-end tests: There's not a recommended way to test the ui+server interaction for just one component.

## Normal tooling doesn't work inside of app?

There are several bits of tooling that don't seem to work inside end-to-end app tests. My guess is that this isn't related to Shiny per se, but rather the ASGI framework: It's not running in the same process as pytest, so it's not surprising that the pytest process can't instrument this.
- [App code skipped by test coverage](https://github.com/opendp/dp-creator-ii/issues/18)
- [Mocks don't work inside app](https://github.com/opendp/dp-creator-ii/issues/119)
- `breakpoint()` doesn't work inside end-to-end tests. (A comparison might be made to debugging a React application: With React devtools in the browser, it's pretty easy!)

## You still need some webdev skills

I've had to tweak the CSS a few times:
- Adding margin to the page
- Overriding tricky bootstrap hover styling for tooltips
- Hiding elements of the slider that we didn't want (because we're using it for a logarithmic scale)

## R vs. Python / Express vs. Core

The different flavors of "Shiny" are a bit of nuissance when trying to find examples.
The maturity of Shiny for R means that the vast majority of the examples are for R, even with Python in the search. It would be nice if the docs site remembered that I only want to look at docs for Core.
