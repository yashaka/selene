- optimise: cash by demand + cash by first usage
    - refactor cash impl to allow un-cashing

- fix the is_displayed method - it should not be executed with _execute with default wait for visibility

- add test about "non-exising" method call on selement/selementscollection

- add docstrings

- make autocompletion work after get_driver().

- make selene support parallel execution

- add screenshots to error messages

- add config.implicitlyWaitFor = conditions.enabled

- test and prettify all error messages (especially where locators are stringified)

- catch IndexError

- finalize all todos in code comments

- find the way for auto-completion to work in cases: ss("..").of(Task)[1].HERE()
  - First try with Jedi's autocompletion
  - Think on how to make it work in Intellij Idea...

- ensure auto-completion work for all "intercepted" methods... like click() , etc...

- improve test coverage, especially of "unit level", not "acceptance" one

- think on privatizing some selement/collection fields

- consider renaming finder() to get_actual_entity(), etc...

- add ability to get "cached" version of selement for 

- accept more than one condition in assure

- add `not` condition

- ss("#item").insist(condition) expect "collection condition" as param...
i.e. the one that knows by itself that it needs to examine items of the ss result (which is SelementsCollection)
in order to assert "element condition" on each item among ss result, you need
to use .insist_each

what if make insist to define itself what condition was passed - collection or element one, and so define
how to assert this condition - on all collection of items or on each item?

(todo: think on this once more... a year passed and now I do not Understand what I wrote :D )

- in case ss("...") finds selements but all of them are hidden, should the .insist(empty) still fail?

- Think on how to implement:


    with the(order.details) as d:
        d.first_name = 'Johanna'
        d.last_name = 'Smith'
        d.salutation = 'Mrs'

instead of 

    with the(order.details) as d:
        d.first_name.set('Johanna')
        d.last_name.set('Smith')
        d.salutation.set('Mrs')
        
        
though seems like this is impossible...

- DSL for "init" page with elements:


    def init(self):
        self.e(name='#name')
        self.e(other_data='#other_specific_data')
        self.ee(Item, items='#list_items')

this may be really valuable because otherwise user needs to call super constructor explicitly and may find an error like here:

    class Item(SElement):
        def __init__(self, locator):
            self.that(lambda it: it.is_displayed())
            self.name = s('.item_name', self)
            self.other_data = s('.item_other_data', self)
            super(Order.Item, self).__init__(locator)

this will fail... the fix is:


    class Item(SElement):
        def __init__(self, locator):
            self.name = s('.item_name', self)
            self.other_data = s('.item_other_data', self)
            super(Order.Item, self).__init__(locator)
            self.that(lambda it: it.is_displayed())

- one more way to init elements:


        self.first_name = self.s('[name="first_name"]')
        self.last_name = self.s('[name="last_name"]')
        self.salutation = self.s('#salutation', SelectList)
       
or:

        self.define(
            first_name=s('[name="first_name"]'),
            last_name=s('[name="last_name"]'),
            salutation=SelectList('#salutation'),
            items = ss('#items'),
            widgets = ss('#widget', Widget)
        )

instead of:


        self.first_name = s('[name="first_name"]', self)
        self.last_name = s('[name="last_name"]', self)
        self.salutation = SelectList('#salutation', self)


